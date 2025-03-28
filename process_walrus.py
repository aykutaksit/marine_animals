import os
import subprocess

def process_video(video_name):
    # Input and output paths
    video_path = f'{video_name}.mp4'
    output_path = f'static/sounds/processed_{video_name}.wav'
    
    try:
        # Ensure the output directory exists
        os.makedirs('static/sounds', exist_ok=True)
        
        # Extract first 5 seconds of audio using ffmpeg
        print(f"Processing {video_name} video file...")
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
        
        print(f"Successfully processed {video_name} audio and saved to {output_path}")
        
    except subprocess.CalledProcessError as e:
        print(f"Error processing video: {str(e)}")
        raise
    except Exception as e:
        print(f"Error: {str(e)}")
        raise

if __name__ == "__main__":
    # Process ringed seal video
    process_video('ringed_seal') 