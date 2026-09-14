import torchvision.transforms as transforms
from selection import *
from datasetClass import *

val_samples, train_samples = split_dataset(IMAGE_DIR, class_to_idx(IMAGE_DIR))

train_trans = transforms.Compose([
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(30),
    transforms.ColorJitter(),
    transforms.RandomResizedCrop(128, scale=(0.4,1.0)),
    transforms.ToTensor()
])

val_trans = transforms.Compose([
    transforms.Resize((128,128)),
    transforms.ToTensor()
])

train_ds = BirdImageDataset(train_samples, train_trans)
val_ds = BirdImageDataset(val_samples, val_trans)

train_loader = DataLoader(train_ds, batch_size=16, shuffle=True)
val_loader = DataLoader(val_ds, batch_size=16, shuffle=False)

for images, labels in train_loader:
    print(images.shape, labels.shape)
    break