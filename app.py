from flask import Flask, render_template, jsonify, request
import os
import random
import soundfile as sf
import numpy as np
from datetime import datetime

app = Flask(__name__)

# Dictionary mapping animal names to their categories
MARINE_ANIMALS = {
    'Dolphin': 'Mammal',
    'Beluga': 'Mammal',
    'Orca': 'Mammal',
    'Humpback Whale': 'Mammal',
    'Harbor Seal': 'Mammal',
    'Right Whale': 'Mammal',
    'Gray Whale': 'Mammal',
    'Sperm Whale': 'Mammal',
    'Minke Whale': 'Mammal',
    'Pilot Whale': 'Mammal',
    'Rissos Dolphin': 'Mammal',
    'Cuviers Beaked Whale': 'Mammal',
    'Leopard Seal': 'Mammal',
    'Weddell Seal': 'Mammal',
    'Bearded Seal': 'Mammal',
    'Ringed Seal': 'Mammal',
    'Walrus': 'Mammal',
    'Manatee': 'Mammal',
    'Snapping Shrimp': 'Crustacean',
    'Atlantic Croaker': 'Fish',
    'Barred Grunt': 'Fish',
    'Black Drum': 'Fish',
    'Oyster Toadfish': 'Fish',
    'Perch': 'Fish',
    'Scalyfin Corvina': 'Fish',
    'Midshipman': 'Fish',
    'Bar Jack': 'Fish'
}

def clean_filename(name):
    """Convert animal name to a clean filename."""
    # Remove special characters and replace spaces with underscores
    name = name.lower()
    name = name.replace("'", "")  # Remove apostrophes
    name = name.replace(" ", "_")
    return name

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_random_animal')
def get_random_animal():
    # Get list of available images
    images_dir = os.path.join('static', 'images')
    available_images = set()
    if os.path.exists(images_dir):
        for filename in os.listdir(images_dir):
            if filename.endswith('.jpg'):
                available_images.add(filename.replace('.jpg', ''))
    
    # Filter animals to only those with images
    available_animals = []
    for animal in MARINE_ANIMALS.keys():
        clean_name = clean_filename(animal)
        if clean_name in available_images:
            available_animals.append(animal)
    
    if not available_animals:
        return jsonify({'error': 'No animals with images available'}), 500
    
    animal = random.choice(available_animals)
    category = MARINE_ANIMALS[animal]
    return jsonify({
        'animal': animal,
        'category': category,
        'sound_file': f'processed_{clean_filename(animal)}.wav',
        'image_file': f'{clean_filename(animal)}.jpg'
    })

@app.route('/save_recording', methods=['POST'])
def save_recording():
    try:
        audio_data = request.get_data()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'recording_{timestamp}.wav'
        
        # Create recordings directory if it doesn't exist
        os.makedirs('recordings', exist_ok=True)
        
        # Save the recording
        with open(os.path.join('recordings', filename), 'wb') as f:
            f.write(audio_data)
        
        return jsonify({'success': True, 'filename': filename})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/get_recordings')
def get_recordings():
    try:
        recordings_dir = 'recordings'
        if not os.path.exists(recordings_dir):
            return jsonify([])
        
        recordings = []
        for filename in os.listdir(recordings_dir):
            if filename.endswith('.wav'):
                filepath = os.path.join(recordings_dir, filename)
                # Get file size and creation time
                size = os.path.getsize(filepath)
                created = datetime.fromtimestamp(os.path.getctime(filepath))
                recordings.append({
                    'filename': filename,
                    'size': size,
                    'created': created.strftime('%Y-%m-%d %H:%M:%S')
                })
        
        # Sort by creation time, newest first
        recordings.sort(key=lambda x: x['created'], reverse=True)
        return jsonify(recordings)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/analyze_recording', methods=['POST'])
def analyze_recording():
    try:
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400
        
        audio_file = request.files['audio']
        target_animal = request.form.get('animal')
        
        if not target_animal:
            return jsonify({'error': 'No target animal specified'}), 400
        
        # For now, we'll just return a simple score based on the audio file size
        # In a real implementation, you would do actual audio analysis here
        file_size = len(audio_file.read())
        score = min(100, int(file_size / 1000))  # Simple scoring based on file size
        
        feedback = "Great job!" if score > 80 else "Try again!" if score > 50 else "Keep practicing!"
        
        return jsonify({
            'score': score,
            'feedback': feedback
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 