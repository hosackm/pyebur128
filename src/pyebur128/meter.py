from ._ffi import build_ffi_and_lib
import soundfile as sf

__all__ = ["Meter"]


class Meter:
    def __init__(self):
        self.ffi, self.lib = build_ffi_and_lib()

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
