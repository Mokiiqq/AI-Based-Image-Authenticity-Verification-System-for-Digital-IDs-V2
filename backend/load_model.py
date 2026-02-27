import torch
from model import build_model

MODEL_PATH = "id_detector.pth"

def load_model():
    print("Loading ResNet model...")
    print(f"Model path: {MODEL_PATH}")
    
    model = build_model()
    state_dict = torch.load(MODEL_PATH, map_location="cpu")
    
    print(f"State dict keys: {list(state_dict.keys())[:5]}...")
    print(f"Total parameters in state_dict: {len(state_dict)}")

    model.load_state_dict(state_dict)
    model.eval()

    print("ResNet STATE_DICT loaded successfully ")
    
    fc_weight = model.fc.weight.data
    print(f"FC layer weight sample: {fc_weight[0][:5]}")
    
    return model


if __name__ == "__main__":
    model = load_model()
    print("Model ready for inference ")
