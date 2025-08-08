import platform
from pathlib import Path
from typing import Protocol, cast

import soundfile as sf
from cffi import FFI

EXTENSION = {"Darwin": ".dylib", "Linux": ".so", "Windows": ".dll"}[platform.system()]
HERE = Path(__file__).parent


class LibEbur128(Protocol):
    def ebur128_init(self, channels: int, samplerate: int, mode: int): ...
    def ebur128_destroy(self, state_ptr): ...
    def ebur128_add_frames_float(self, state, frames, frames_size: int) -> int: ...
    def ebur128_loudness_global(self, state, out_ptr) -> int: ...


class Meter:
    def __init__(self, lib_path: Path | None = None):
        self.ffi = FFI()
        self.ffi.cdef("""
        typedef struct ebur128_state ebur128_state;

        ebur128_state* ebur128_init(unsigned int channels, unsigned long samplerate, unsigned int mode);
        void ebur128_destroy(ebur128_state** st);
        int ebur128_add_frames_float(ebur128_state* st, const float* frames, size_t frames_size);
        int ebur128_loudness_global(ebur128_state* st, double* out);
        """)

        if lib_path is None:
            lib_path = HERE / f"libebur128{EXTENSION}"
        self.lib = cast(LibEbur128, self.ffi.dlopen(str(lib_path)))

    def measure(self, filepath: str, blocksize: int = 4096) -> float:
        """Compute integrated loudness (LUFS) of the given audio file using streaming."""
        info = sf.info(filepath)
        samplerate = info.samplerate
        channels = info.channels

        # Mode: EBUR128_MODE_I | EBUR128_MODE_LRA (0x1 | 0x4)
        mode = 0x1 | 0x1 << 2
        st = self.lib.ebur128_init(channels, samplerate, mode)
        if not st:
            raise RuntimeError("Failed to initialize ebur128_state")

        try:
            for block in sf.blocks(
                filepath, blocksize=blocksize, dtype="float32", always_2d=True
            ):
                c_block = self.ffi.cast("float *", block.ctypes.data)
                res = self.lib.ebur128_add_frames_float(st, c_block, block.shape[0])
                if res != 0:
                    raise RuntimeError("Failed to add frames")

            out_loudness = self.ffi.new("double*")
            res = self.lib.ebur128_loudness_global(st, out_loudness)
            if res != 0:
                raise RuntimeError("Failed to compute loudness")

            return out_loudness[0]
        finally:
            self.lib.ebur128_destroy(self.ffi.new("ebur128_state**", st))
