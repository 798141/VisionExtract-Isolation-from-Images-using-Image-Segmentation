import os
from PIL import Image
from torch.utils.data import Dataset
from torchvision import transforms

class VehicleMaskDataset(Dataset):
    def __init__(self, image_folder, mask_folder, transform=None):
        self.image_folder = image_folder
        self.mask_folder = mask_folder
        self.transform = transform
        self.image_files = os.listdir(image_folder)

    def __len__(self):
        return len(self.image_files)

    def __getitem__(self, idx):
        image_filename = self.image_files[idx]
        image_path = os.path.join(self.image_folder, image_filename)
        image_stem = os.path.splitext(image_filename)[0]

        found_mask = None
        mask_extensions = ['.png', '.jpg', '.jpeg']
        mask_variants = ['', '_mask', '-mask', ' mask']

        for ext in mask_extensions:
            for suffix in mask_variants:
                candidate_mask = image_stem + suffix + ext
                candidate_path = os.path.join(self.mask_folder, candidate_mask)
                if os.path.exists(candidate_path):
                    found_mask = candidate_path
                    break
            if found_mask:
                break

        if not found_mask:
            print("DEBUG: Missing mask for", image_filename)
            print("Checked directory:", self.mask_folder)
            raise FileNotFoundError(f"❌ No mask corresponding to: {image_filename}")

        image = Image.open(image_path).convert("RGB")
        mask = Image.open(found_mask).convert("L")

        if self.transform:
            image = self.transform(image)
        else:
            image = transforms.Resize((128, 128))(image)

        mask = transforms.Resize((128, 128))(mask)
        mask = transforms.ToTensor()(mask)

        return image, mask
