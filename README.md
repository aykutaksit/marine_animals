# Marine Animal Sound and Image Library

This project contains a collection of marine animal sounds and images, organized for educational and research purposes.

## Project Structure

```
.
├── static/
│   ├── images/          # Marine animal images
│   └── sounds/          # Marine animal sound files
│       └── processed/   # 5-second processed sound files
├── download_images.py   # Script to download marine animal images
├── download_sounds.py   # Script to download marine animal sounds
└── process_sounds.py    # Script to process sound files to 5 seconds
```

## Features

- Collection of marine animal images from various sources
- High-quality sound recordings of marine animals
- All sound files are processed to be exactly 5 seconds long
- Automated scripts for downloading and processing media files

## Requirements

- Python 3.x
- Required Python packages:
  - requests
  - beautifulsoup4
  - selenium
  - webdriver_manager
  - pydub

## Usage

1. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

2. Download images:
   ```bash
   python download_images.py
   ```

3. Download sounds:
   ```bash
   python download_sounds.py
   ```

4. Process sounds to 5 seconds:
   ```bash
   python process_sounds.py
   ```

## Notes

- All sound files are processed to be exactly 5 seconds long
- Images are downloaded from various sources including OCR and Pixabay
- Sound files are downloaded from OCR's sound library
- The project maintains a clean and organized structure for easy access to media files 