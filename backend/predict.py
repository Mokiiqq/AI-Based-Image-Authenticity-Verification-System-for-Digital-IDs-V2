import torch
from PIL import Image
from torchvision import transforms
from load_model import load_model

def predict():
    model = load_model()

    image = Image.open("test_id.jpg").convert("RGB")

    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
    ])

    img_tensor = transform(image).unsqueeze(0)

    with torch.no_grad():
        outputs = model(img_tensor)
        probs = torch.softmax(outputs, dim=1)
        confidence, predicted = torch.max(probs, 1)

    labels = ["FAKE ID", "REAL ID"]

    print(f"Prediction: {labels[predicted.item()]}")
    print(f"Confidence: {confidence.item():.2f}")

if __name__ == "__main__":
    predict()
