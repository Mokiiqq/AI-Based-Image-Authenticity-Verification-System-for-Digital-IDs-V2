"""Export PyTorch model to ONNX format using the legacy exporter."""
import torch
from model import build_model

model = build_model()
state_dict = torch.load('id_detector.pth', map_location='cpu')
model.load_state_dict(state_dict)
model.eval()

dummy = torch.randn(1, 3, 224, 224)

# Use legacy exporter to avoid issues with newer torch versions
torch.onnx.export(
    model, dummy, 'id_detector.onnx',
    input_names=['input'],
    output_names=['output'],
    dynamic_axes={'input': {0: 'batch'}, 'output': {0: 'batch'}},
    opset_version=13,
    dynamo=False
)

import os
size = os.path.getsize('id_detector.onnx')
print(f'ONNX exported OK, size: {size/1024/1024:.2f} MB')

# Verify with onnxruntime
import onnxruntime as ort
import numpy as np

sess = ort.InferenceSession('id_detector.onnx')
result = sess.run(None, {'input': dummy.numpy()})
print(f'ONNX output shape: {result[0].shape}')
print(f'ONNX output sample: {result[0][0][:5]}')

# Compare with pytorch
with torch.no_grad():
    pt_out = model(dummy)
print(f'PyTorch output sample: {pt_out[0][:5].numpy()}')
print('Outputs match!' if np.allclose(result[0], pt_out.numpy(), atol=1e-5) else 'WARNING: outputs differ!')
