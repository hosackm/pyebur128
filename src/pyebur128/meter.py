from pathlib import Path

from ._ffi import build_ffi_and_lib
import soundfile as sf

__all__ = ["Meter"]


class Meter:
    def __init__(self):
        self.ffi, self.lib = build_ffi_and_lib()

    def measure(self, filepath: Path | str, blocksize: int = 4096) -> float:
        """Compute integrated loudness (LUFS) of the given audio file."""
        with sf.SoundFile(filepath, "r") as f:
            # Mode: EBUR128_MODE_I | EBUR128_MODE_LRA (0x1 | 0x4)
            mode = 0x1 | 0x1 << 2
            st = self.lib.ebur128_init(f.channels, f.samplerate, mode)
            if not st:
                raise RuntimeError("Failed to initialize ebur128_state")

            try:
                while True:
                    block = f.read(blocksize, always_2d=True, dtype="float32")
                    if len(block) == 0:
                        break

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
