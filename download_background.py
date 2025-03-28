import os
import requests
from pathlib import Path
from PIL import Image, ImageDraw

# Create images directory if it doesn't exist
images_dir = Path('static/images')
images_dir.mkdir(parents=True, exist_ok=True)

# URL for a cute ocean-themed background image
BACKGROUND_URL = 'https://raw.githubusercontent.com/your-username/your-repo/main/background.png'

def download_background():
    """Download the background image and save it to the images directory."""
    try:
        # For now, let's create a simple gradient background instead of downloading an image
        # Create a new image with a gradient background
        width = 1920
        height = 1080
        image = Image.new('RGB', (width, height))
        draw = ImageDraw.Draw(image)
        
        # Create a gradient from light blue to white
        for y in range(height):
            r = int(224 + (255 - 224) * y / height)  # 224 is 0xE0
            g = int(247 + (255 - 247) * y / height)  # 247 is 0xF7
            b = int(250 + (255 - 250) * y / height)  # 250 is 0xFA
            draw.line([(0, y), (width, y)], fill=(r, g, b))
        
        # Save the image
        filepath = images_dir / 'background.png'
        image.save(filepath)
        print("Successfully created background image")
    except Exception as e:
        print(f"Error creating background image: {str(e)}")

if __name__ == '__main__':
    download_background() 