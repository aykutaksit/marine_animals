import os
from pathlib import Path
from pydub import AudioSegment
import time

def process_sound_file(input_file, output_file, target_duration=5000):
    """Process a sound file to be exactly target_duration milliseconds long."""
    try:
        # Load the audio file
        audio = AudioSegment.from_file(input_file)
        
        # If the audio is shorter than the target duration, loop it
        if len(audio) < target_duration:
            repeats = target_duration // len(audio) + 1
            audio = audio * repeats
        
        # Trim to the target duration
        audio = audio[:target_duration]
        
        # Export as WAV
        audio.export(output_file, format='wav')
        print(f"Processed: {output_file.name}")
        return True
    except Exception as e:
        print(f"Error processing {input_file.name}: {str(e)}")
        return False

def main():
    sounds_dir = Path('static/sounds')
    processed_dir = sounds_dir / 'processed'
    processed_dir.mkdir(exist_ok=True)
    
    # Process all WAV files
    for sound_file in sounds_dir.glob('*.wav'):
        if sound_file.name.startswith('processed_'):
            output_file = processed_dir / sound_file.name
            process_sound_file(sound_file, output_file)
            time.sleep(0.1)  # Small delay to prevent system overload
    
    print("\nSound processing complete!")

if __name__ == '__main__':
    main() 