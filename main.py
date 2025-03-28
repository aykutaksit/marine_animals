from flask import Flask, render_template, send_from_directory, jsonify, request, session
from pathlib import Path
import random
import librosa
import numpy as np
import soundfile as sf
import io
import wave
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Required for session support

# Cute descriptions for each animal
ANIMAL_DESCRIPTIONS = {
    'Dolphin': 'Dolphins make high-pitched whistles and clicks that sound like happy giggles! 🐬',
    'Harbor Seal': 'Harbor seals make deep barking sounds like a friendly puppy! 🦭',
    'Orca': 'Orcas make distinctive whistles and clicks that sound like underwater songs! 🐋',
    'Beluga': 'Belugas are called "canaries of the sea" with their high-pitched calls! 🐳',
    'Humpback Whale': 'Humpback whales sing beautiful songs that echo through the ocean! 🐋',
    'Gray Whale': 'Gray whales make deep, gentle sounds like underwater sighs! 🐋',
    'Right Whale': 'Right whales make low, peaceful sounds like gentle ocean waves! 🐋',
    'Sperm Whale': 'Sperm whales make deep clicking sounds like underwater drums! 🐋',
    'Bowhead Whale': 'Bowhead whales sing complex songs that last for hours! 🐋',
    'Minke Whale': 'Minke whales make short, high-pitched sounds like underwater chirps! 🐋',
    'Pilot Whale': 'Pilot whales make whistling sounds like underwater flutes! 🐋',
    'Cuviers Beaked Whale': 'Cuvier\'s beaked whales make clicking sounds like underwater sonar! 🐋',
    'Bearded Seal': 'Bearded seals make trilling sounds like underwater birds! 🦭',
    'Weddell Seal': 'Weddell seals make whistling sounds like underwater wind! 🦭',
    'Bar Jack': 'Bar jacks make clicking sounds like underwater castanets! 🐟',
    'Barred Grunt': 'Barred grunts make grunting sounds like underwater pigs! 🐟',
    'Black Drum': 'Black drums make drumming sounds like underwater percussion! 🐟',
    'Atlantic Croaker': 'Atlantic croakers make croaking sounds like underwater frogs! 🐟',
    'Midshipman': 'Midshipmen make humming sounds like underwater bees! 🐟',
    'Oyster Toadfish': 'Oyster toadfish make boat whistle sounds like underwater trains! 🐟',
    'Perch': 'Perch make clicking sounds like underwater crickets! 🐟',
    'Snapping Shrimp': 'Snapping shrimp make popping sounds like underwater bubbles! 🦐'
}

def get_available_animals():
    """Get list of available animals from the processed sounds directory."""
    sounds_dir = Path('static/sounds/processed')
    if not sounds_dir.exists():
        return []
    
    animals = []
    for sound_file in sounds_dir.glob('processed_*.wav'):
        # Convert filename to animal name (e.g., 'processed_humpback_whale.wav' -> 'humpback whale')
        animal_name = sound_file.stem.replace('processed_', '').replace('_', ' ').title()
        animals.append({
            'name': animal_name,
            'sound': f'/sounds/processed/{sound_file.name}',
            'image': f'/images/{sound_file.stem.replace("processed_", "")}.jpg',
            'description': ANIMAL_DESCRIPTIONS.get(animal_name, 'Listen to this amazing marine animal! 🌊')
        })
    return animals

def analyze_audio(original_path, user_path):
    try:
        # Load audio files
        original, sr_orig = librosa.load(original_path, sr=None)
        user, sr_user = librosa.load(user_path, sr=None)
        
        # Resample user audio to match original sample rate if needed
        if sr_user != sr_orig:
            user = librosa.resample(user, orig_sr=sr_user, target_sr=sr_orig)
        
        # Ensure both audio files are the same length
        min_len = min(len(original), len(user))
        original = original[:min_len]
        user = user[:min_len]
        
        # Extract pitch features
        original_pitch, original_mag = librosa.piptrack(y=original, sr=sr_orig)
        user_pitch, user_mag = librosa.piptrack(y=user, sr=sr_orig)
        
        # Get mean pitch values (ignoring zero magnitudes)
        original_pitch_mean = np.mean(original_pitch[original_mag > 0])
        user_pitch_mean = np.mean(user_pitch[user_mag > 0])
        
        # Calculate pitch similarity (much stricter scaling)
        pitch_diff = abs(original_pitch_mean - user_pitch_mean)
        pitch_score = max(0, 100 - (pitch_diff / 10))  # Much stricter scaling factor
        
        # Extract basic features for rhythm
        original_onset = librosa.onset.onset_strength(y=original, sr=sr_orig)
        user_onset = librosa.onset.onset_strength(y=user, sr=sr_orig)
        
        # Calculate rhythm similarity (much stricter scaling)
        rhythm_diff = np.mean(np.abs(original_onset - user_onset))
        rhythm_score = max(0, 100 - (rhythm_diff * 20))  # Much stricter scaling factor
        
        # Calculate energy similarity
        original_energy = librosa.feature.rms(y=original)
        user_energy = librosa.feature.rms(y=user)
        energy_diff = np.mean(np.abs(original_energy - user_energy))
        energy_score = max(0, 100 - (energy_diff * 30))  # Strict energy comparison
        
        # Calculate final score (weighted combination)
        final_score = (pitch_score * 0.5 + rhythm_score * 0.3 + energy_score * 0.2)
        
        # Make scoring even stricter by applying a penalty for any significant differences
        if pitch_diff > 20 or rhythm_diff > 0.5 or energy_diff > 0.3:
            final_score *= 0.8  # 20% penalty for significant differences
        
        # Generate feedback based on score
        if final_score >= 90:
            feedback = "Perfect! You're a marine animal sound expert! 🌟"
        elif final_score >= 75:
            feedback = "Very good! You're getting really close! 🎯"
        elif final_score >= 50:
            feedback = "Not bad! Keep practicing to match the sound better! 🎵"
        else:
            feedback = "Keep trying! Focus on matching the pitch and rhythm! 💪"
        
        return {
            'score': round(final_score, 1),
            'feedback': feedback
        }
    except Exception as e:
        print(f"Error in analyze_audio: {str(e)}")
        return {
            'score': 0,
            'feedback': "Let's try again! Make sure to record a clear sound impression. 🎤"
        }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/sounds/<path:filename>')
def serve_sound(filename):
    return send_from_directory('static/sounds', filename)

@app.route('/images/<path:filename>')
def serve_image(filename):
    return send_from_directory('static/images', filename)

@app.route('/api/random-animal')
def random_animal():
    animals = get_available_animals()
    if not animals:
        return jsonify({'error': 'No animals available'}), 404
    animal = random.choice(animals)
    session['current_animal'] = animal  # Store the current animal in session
    return jsonify(animal)

@app.route('/api/analyze_recording', methods=['POST'])
def analyze_recording():
    try:
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400
        
        audio_file = request.files['audio']
        if audio_file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        # Get the current animal from the session
        current_animal = session.get('current_animal')
        if not current_animal:
            return jsonify({'error': 'No animal selected'}), 400
        
        # Create recordings directory if it doesn't exist
        recordings_dir = os.path.join('static', 'recordings')
        os.makedirs(recordings_dir, exist_ok=True)
        
        # Save the user's recording
        user_recording_path = os.path.join(recordings_dir, f'user_{current_animal["name"].lower().replace(" ", "_")}.wav')
        audio_file.save(user_recording_path)
        
        # Get the original sound path
        original_sound_path = os.path.join('static', 'sounds', 'processed', f'processed_{current_animal["name"].lower().replace(" ", "_")}.wav')
        
        if not os.path.exists(original_sound_path):
            return jsonify({
                'score': 0,
                'feedback': "Oops! Couldn't find the original sound. Please try another animal! 🐋"
            })
        
        # Analyze the recording
        result = analyze_audio(original_sound_path, user_recording_path)
        
        return jsonify(result)
    except Exception as e:
        print(f"Error processing recording: {str(e)}")
        return jsonify({
            'score': 0,
            'feedback': "Oops! Something went wrong. Let's try recording again! 🎤"
        })

if __name__ == '__main__':
    app.run(debug=True)
