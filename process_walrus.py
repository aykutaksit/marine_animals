import os
import subprocess

def process_walrus_video():
    # Input and output paths
    video_path = 'walrus.mp4'
    output_path = 'static/sounds/processed_walrus.wav'
    
    try:
        # Ensure the output directory exists
        os.makedirs('static/sounds', exist_ok=True)
        
        # Extract first 5 seconds of audio using ffmpeg
        print("Processing video file...")
        cmd = [
            'ffmpeg',
            '-i', video_path,
            '-t', '5',  # Duration of 5 seconds
            '-vn',  # No video
            '-acodec', 'pcm_s16le',  # WAV codec
            '-ar', '44100',  # Sample rate
            '-ac', '2',  # Stereo
            output_path
        ]
        
        subprocess.run(cmd, check=True)
        
        # Delete the original video file
        print("Cleaning up...")
        os.remove(video_path)
        
        print(f"Successfully processed Walrus audio and saved to {output_path}")
        
    except subprocess.CalledProcessError as e:
        print(f"Error processing video: {str(e)}")
        raise
    except Exception as e:
        print(f"Error: {str(e)}")
        raise

if __name__ == "__main__":
    process_walrus_video() 