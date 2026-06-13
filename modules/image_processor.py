"""
Image Processor Module
- Auto resizes image to meet each site's size limit
- Auto converts JPG/PNG as needed
- Saves processed image to images/processed/ folder
"""

import os
import json
from PIL import Image

CONFIG_PATH = os.path.join(os.path.dirname(__file__), '..', 'config', 'config.json')

with open(CONFIG_PATH) as f:
    CONFIG = json.load(f)

MASTER_FOLDER    = os.path.join(os.path.dirname(__file__), '..', CONFIG['images_folder'])
PROCESSED_FOLDER = os.path.join(os.path.dirname(__file__), '..', CONFIG['processed_folder'])

os.makedirs(MASTER_FOLDER,    exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)


def get_file_size_mb(path):
    return os.path.getsize(path) / (1024 * 1024)


def process_image(image_filename, site_name, max_size_mb, allowed_formats):
    """
    Takes master image, converts format and compresses to fit site limits.
    Returns path to processed image ready for upload.
    """
    master_path = os.path.join(MASTER_FOLDER, image_filename)

    if not os.path.exists(master_path):
        print(f"  [ERROR] Image not found: {master_path}")
        return None

    # Decide output format
    preferred_format = 'jpg'
    if 'jpg' in allowed_formats or 'jpeg' in allowed_formats:
        preferred_format = 'jpg'
    elif 'png' in allowed_formats:
        preferred_format = 'png'

    output_filename = f"{site_name.lower().replace('.', '_').replace(' ', '_')}_{image_filename.rsplit('.', 1)[0]}.{preferred_format}"
    output_path     = os.path.join(PROCESSED_FOLDER, output_filename)

    img = Image.open(master_path).convert('RGB')

    # Save at full quality first
    pil_format = 'JPEG' if preferred_format == 'jpg' else 'PNG'
    quality    = 95

    img.save(output_path, pil_format, quality=quality)

    # Compress until under size limit
    while get_file_size_mb(output_path) > max_size_mb and quality > 20:
        quality -= 5
        img.save(output_path, pil_format, quality=quality)

    # If still too large, resize image dimensions
    if get_file_size_mb(output_path) > max_size_mb:
        width, height = img.size
        while get_file_size_mb(output_path) > max_size_mb and width > 400:
            width  = int(width  * 0.85)
            height = int(height * 0.85)
            img_resized = img.resize((width, height), Image.LANCZOS)
            img_resized.save(output_path, pil_format, quality=quality)

    final_size = get_file_size_mb(output_path)
    print(f"  [IMAGE] {site_name}: {image_filename} → {output_filename} ({final_size:.2f} MB)")
    return output_path


if __name__ == '__main__':
    # Quick test
    print("Image Processor — Test Run")
    test = process_image('myimage.jpg', 'TestSite', max_size_mb=1, allowed_formats=['jpg'])
    if test:
        print(f"  Output: {test}")
