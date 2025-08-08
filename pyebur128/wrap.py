from pathlib import Path
import soundfile as sf
from cffi import FFI

from typing import Protocol, cast

HERE = Path(__file__).parent


class LibEbur128(Protocol):
    def ebur128_init(self, channels: int, samplerate: int, mode: int): ...
    def ebur128_destroy(self, state_ptr): ...
    def ebur128_add_frames_float(self, state, frames, frames_size: int) -> int: ...
    def ebur128_loudness_global(self, state, out_ptr) -> int: ...


ffi = FFI()

ffi.cdef("""
typedef struct ebur128_state ebur128_state;

ebur128_state* ebur128_init(unsigned int channels, unsigned long samplerate, unsigned int mode);
void ebur128_destroy(ebur128_state** st);
int ebur128_add_frames_float(ebur128_state* st, const float* frames, size_t frames_size);
int ebur128_loudness_global(ebur128_state* st, double* out);
""")


lib = cast(LibEbur128, ffi.dlopen(str(HERE / "libebur128.dylib")))


def compute_loudness_streaming(filepath: str, blocksize: int = 4096) -> float:
    info = sf.info(filepath)
    samplerate = info.samplerate
    channels = info.channels

    st = lib.ebur128_init(channels, samplerate, 0x1 | (0x1 << 2))
    if not st:
        raise RuntimeError("Failed to initialize ebur128_state")

    for block in sf.blocks(
        filepath, blocksize=blocksize, dtype="float32", always_2d=True
    ):
        c_block = ffi.cast("float *", block.ctypes.data)
        res = lib.ebur128_add_frames_float(st, c_block, block.shape[0])
        if res != 0:
            raise RuntimeError("Failed to add frames")

    out_loudness = ffi.new("double*")
    res = lib.ebur128_loudness_global(st, out_loudness)
    if res != 0:
        raise RuntimeError("Failed to compute loudness")

    lib.ebur128_destroy(ffi.new("ebur128_state**", st))

    return out_loudness[0]


if __name__ == "__main__":
    input_path = "/Users/matthosack/code/python/loudeval/audio/bigbuckbunny_2hr.wav"
    samplerate = sf.info(input_path).samplerate
    loudness = compute_loudness_streaming(input_path, 4096)
    print(loudness)
