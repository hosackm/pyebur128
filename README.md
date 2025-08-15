# pyebur128

Python bindings to wrap [libebur128](https://github.com/jiixyj/libebur128/tree/master/ebur128).

## Install

```bash
pip install .
```

## To Use

```python
# To measure
import pyebur128 as ebu
meter = ebu.Meter()
lkfs = meter.measure("some-file.wav")

# To normalize
target = -14
ebu.normalize("some-file.wav", "output.wav", target)
```

