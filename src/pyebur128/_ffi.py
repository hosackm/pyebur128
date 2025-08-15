import platform
from pathlib import Path
from typing import Protocol, cast

from cffi import FFI

__all__ = ["build_ffi_and_lib"]


EXTENSION = {"Darwin": ".dylib", "Linux": ".so", "Windows": ".dll"}[platform.system()]
HERE = Path(__file__).parent


class LibEbur128(Protocol):
    def ebur128_init(self, channels: int, samplerate: int, mode: int): ...
    def ebur128_destroy(self, state_ptr): ...
    def ebur128_add_frames_float(self, state, frames, frames_size: int) -> int: ...
    def ebur128_loudness_global(self, state, out_ptr) -> int: ...


def build_ffi_and_lib() -> tuple[FFI, LibEbur128]:
    ffi = FFI()
    ffi.cdef("""
    typedef struct ebur128_state ebur128_state;

    ebur128_state* ebur128_init(unsigned int channels, unsigned long samplerate, unsigned int mode);
    void ebur128_destroy(ebur128_state** st);
    int ebur128_add_frames_float(ebur128_state* st, const float* frames, size_t frames_size);
    int ebur128_loudness_global(ebur128_state* st, double* out);
    """)
    lib_path = Path(HERE, "lib", f"libebur128{EXTENSION}")
    return ffi, cast(LibEbur128, ffi.dlopen(str(lib_path)))
