"""Pattern B: numpy_reference and ONNX both accept the raw
rank-2 grid; the reference may transform locally if needed.

In this example, both the ONNX model and the ``numpy_reference``
operate on the same rank-2 grid shape. The "raw grid + local
encoding" framing applies when the build script needs to
preprocess (e.g., one-hot encode, normalize, flatten) the raw
ARC-AGI grid to match the ONNX model's expected input shape.
The reference function does whatever transformation is needed
inside its body so the caller can pass the raw grid uniformly.

When the ONNX model's input shape exactly matches the raw
grid shape (as in this example), the local-encoding step
becomes a no-op identity. When the ONNX model expects a
different shape (e.g., ``(1, 10, H, W)`` one-hot), the
reference function performs the encoding before computing.

The companion ``.json`` task file at
``raw_grid_input_example.json`` provides probe grids in the
raw rank-2 shape.
"""

from __future__ import annotations


def numpy_reference(grid):
    import numpy as np

    # Pattern B: input is raw rank-2 grid. The reference does
    # whatever the ONNX model does (here: identity).
    return np.array(grid, dtype=np.float32)
