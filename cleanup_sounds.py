import os
from pathlib import Path

def cleanup_sounds():
    """Clean up duplicate sound files and keep only the processed WAV files."""
    sounds_dir = Path('static/sounds')
    
    # Keep only processed WAV files and remove others
    for file in sounds_dir.glob('*'):
        if file.suffix == '.mp3' or (file.suffix == '.wav' and not file.name.startswith('processed_')):
            try:
                file.unlink()
                print(f"Removed: {file.name}")
            except Exception as e:
                print(f"Error removing {file.name}: {str(e)}")

if __name__ == '__main__':
    cleanup_sounds() 