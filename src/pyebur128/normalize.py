from pathlib import Path

import numpy as np
import soundfile as sf

from .meter import Meter


def normalize(
    input_path: Path, output_path: Path, target_loudness: float, chunksize: int = 2048
) -> None:
    lkfs = Meter().measure(str(input_path))
    gain = np.power(10.0, (target_loudness - lkfs) / 20.0)

    with sf.SoundFile(input_path, "r") as fin:
        kwargs = {
            "samplerate": fin.samplerate,
            "channels": fin.channels,
            "endian": fin.endian,
            "format": fin.format,
            "subtype": fin.subtype,
        }
        with sf.SoundFile(output_path, "w", **kwargs) as fout:
            while True:
                chunk = fin.read(chunksize, always_2d=True)
                if len(chunk) == 0:
                    break

                fout.write(chunk * gain)
