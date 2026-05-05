"""Pattern A: numpy_reference accepts the already-one-hot input.

The convention assumes the caller (NeuroGolf builder pipeline)
has already encoded the raw ARC-AGI grid into ``(1, 10, H, W)``
one-hot before passing to both the ONNX model and the
``numpy_reference``. This pattern is simpler when the build
script's reference and the ONNX export both operate on the
same one-hot tensor shape.

The companion ``.json`` task file at
``onehot_input_example.json`` provides probe grids in the
already-encoded shape (rank-4 with 10 channels).
"""

from __future__ import annotations


def numpy_reference(grid):
    import numpy as np

    # Pattern A: the input is already (1, 10, H, W) one-hot.
    # The reference is an identity (matches the ONNX Identity
    # op in onehot_input_example.onnx).
    return np.array(grid, dtype=np.float32)
