import torch
import torch.nn as nn
import torch.optim as optim
import argparse
import os
from torch.utils.data import DataLoader, random_split
from torchvision import datasets, transforms
from detect import CNNModel

parser = argparse.ArgumentParser(description="Training settings")
parser.add_argument("-e", "--epochs", type=int, default=5, help="number of epochs for training")
args = parser.parse_args()
epochs = args.epochs

transform = transforms.Compose([
    transforms.Grayscale(num_output_channels=1),
    transforms.Resize((28, 28)),
    transforms.ToTensor(),
    transforms.Normalize((0.0,), (1.0,))
])

dataset = datasets.ImageFolder(root="./dataset/", transform=transform)
train_size = int(0.8 * len(dataset))
test_size = len(dataset) - train_size
train_dataset, test_dataset = random_split(dataset, [train_size, test_size])
train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=64, shuffle=False)

model = CNNModel()
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

def train_model(model, criterion, optimizer, train_loader, epochs=epochs):
    model.train()
    print("Training...")
    for epoch in range(epochs):
        running_loss = 0.0
        for images, labels in train_loader:
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            running_loss += loss.item()
        print(f"Epoch [{epoch+1}/{epochs}], Loss: {running_loss/len(train_loader):.4f}")
    os.makedirs("logs", exist_ok=True)
    torch.save(model.state_dict(), "logs/model.pth")
    print("Model saved to 'logs/model.pth'")

def evaluate_model(model, test_loader):
    model.eval()
    correct = 0
    total = 0
    with torch.no_grad():
        for images, labels in test_loader:
            outputs = model(images)
            _, detected = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (detected == labels).sum().item()
    accuracy = 100 * correct / total
    print(f"Accuracy: {accuracy:.2f}%")

if __name__ == "__main__":
    print("Number of images in training set:", len(train_dataset))
    print("Number of images in test set:", len(test_dataset))
    train_model(model, criterion, optimizer, train_loader)
    evaluate_model(model, test_loader)
