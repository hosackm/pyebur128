from pathlib import Path

import pyebur128 as ebu
import pytest

HERE = Path(__file__).parent


def is_close(actual, target, threshold=0.1):
    return target - threshold <= actual <= target + threshold


@pytest.mark.parametrize(
    "input_path,target",
    [
        ("data/1770-2_Comp_23LKFS_10000Hz_2ch.wav", -23),
        ("data/1770-2_Comp_23LKFS_10000Hz_2ch.wav", -23),
        ("data/1770-2_Comp_23LKFS_10000Hz_2ch.wav", -23),
        ("data/1770-2_Comp_23LKFS_2000Hz_2ch.wav", -23),
        ("data/1770-2_Comp_24LKFS_10000Hz_2ch.wav", -24),
        ("data/1770-2_Comp_24LKFS_2000Hz_2ch.wav", -24),
        ("data/1770-2_Comp_23LKFS_1000Hz_2ch.wav", -23),
        ("data/1770-2_Comp_23LKFS_25Hz_2ch.wav", -23),
        ("data/1770-2_Comp_24LKFS_1000Hz_2ch.wav", -24),
        ("data/1770-2_Comp_24LKFS_25Hz_2ch.wav", -24),
        ("data/1770-2_Comp_23LKFS_100Hz_2ch.wav", -23),
        ("data/1770-2_Comp_23LKFS_500Hz_2ch.wav", -23),
        ("data/1770-2_Comp_24LKFS_100Hz_2ch.wav", -24),
        ("data/1770-2_Comp_24LKFS_500Hz_2ch.wav", -24),
        ("data/1770-2_Conf_Mono_Voice+Music-23LKFS.wav", -23),
        ("data/1770-2_Conf_Mono_Voice+Music-24LKFS.wav", -24),
        ("data/1770-2_Conf_Stereo_VinL+R-23LKFS.wav", -23),
        ("data/1770-2_Conf_Stereo_VinL+R-24LKFS.wav", -24),
    ],
)
def test_measure(input_path, target):
    input_path = HERE / input_path
    meter = ebu.Meter()
    loudness = meter.measure(str(input_path))
    assert is_close(loudness, target)
