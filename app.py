from flask import Flask, render_template, jsonify, request, send_from_directory
import os
import random
import soundfile as sf
import numpy as np
from datetime import datetime

app = Flask(__name__, static_folder='static', static_url_path='/static')

# Dictionary mapping animal names to their categories and descriptions
MARINE_ANIMALS = {
    'Dolphin': {
        'category': 'Mammal',
        'description': 'Dolphins are known for their high-pitched whistles and clicks. They use echolocation to navigate and hunt, producing rapid clicking sounds that bounce off objects and return to them.'
    },
    'Beluga': {
        'category': 'Mammal',
        'description': 'Beluga whales are often called "canaries of the sea" due to their wide range of vocalizations. They produce whistles, clicks, and chirps, and can even mimic human speech patterns.'
    },
    'Orca': {
        'category': 'Mammal',
        'description': 'Orcas, also known as killer whales, produce a variety of sounds including whistles, clicks, and pulsed calls. Each pod has its own unique dialect of calls.'
    },
    'Humpback Whale': {
        'category': 'Mammal',
        'description': 'Humpback whales are famous for their complex songs, which can last for 20 minutes and be heard for miles. Males sing these songs during breeding season to attract mates.'
    },
    'Harbor Seal': {
        'category': 'Mammal',
        'description': 'Harbor seals produce a variety of vocalizations including growls, grunts, and barks. They are most vocal during breeding season and when communicating with their pups.'
    },
    'Right Whale': {
        'category': 'Mammal',
        'description': 'Right whales produce low-frequency moans and groans that can travel long distances underwater. They use these sounds for communication and navigation.'
    },
    'Gray Whale': {
        'category': 'Mammal',
        'description': 'Gray whales produce low-frequency moans and grunts. They are known for their distinctive "knocks" and "bongs" which they use for communication during migration.'
    },
    'Sperm Whale': {
        'category': 'Mammal',
        'description': 'Sperm whales produce the loudest sounds of any animal on Earth - powerful clicks that can reach 230 decibels. They use these clicks for echolocation and communication.'
    },
    'Minke Whale': {
        'category': 'Mammal',
        'description': 'Minke whales produce a variety of sounds including low-frequency moans and high-frequency clicks. They are known for their "boing" sound, which is unique to this species.'
    },
    'Pilot Whale': {
        'category': 'Mammal',
        'description': 'Pilot whales produce whistles and clicks for communication and echolocation. They are highly social animals and maintain strong family bonds through vocal communication.'
    },
    'Rissos Dolphin': {
        'category': 'Mammal',
        'description': 'Rissos dolphins produce a variety of sounds including whistles, clicks, and burst-pulse sounds. They use these sounds for communication and navigation in deep waters.'
    },
    'Cuviers Beaked Whale': {
        'category': 'Mammal',
        'description': 'Cuviers beaked whales produce distinctive echolocation clicks and whistles. They are deep divers and use their clicks to navigate and hunt in the deep ocean.'
    },
    'Leopard Seal': {
        'category': 'Mammal',
        'description': 'Leopard seals produce a variety of vocalizations including growls, grunts, and trills. They are known for their haunting underwater calls during breeding season.'
    },
    'Weddell Seal': {
        'category': 'Mammal',
        'description': 'Weddell seals produce a wide range of sounds including whistles, trills, and chirps. They are known for their complex underwater songs during breeding season.'
    },
    'Bearded Seal': {
        'category': 'Mammal',
        'description': 'Bearded seals are known for their distinctive "trill" calls, which sound like descending whistles. Males produce these calls during breeding season to attract mates.'
    },
    'Ringed Seal': {
        'category': 'Mammal',
        'description': 'Ringed seals produce a variety of vocalizations including growls, grunts, and whistles. They use these sounds for communication, especially during breeding season.'
    },
    'Walrus': {
        'category': 'Mammal',
        'description': 'Walruses produce a variety of sounds including bell-like sounds, grunts, and whistles. They are known for their distinctive "bell" calls during breeding season.'
    },
    'Manatee': {
        'category': 'Mammal',
        'description': 'Manatees produce squeaks, squeals, and chirps for communication. They are social animals and use these sounds to maintain contact with other manatees.'
    },
    'Snapping Shrimp': {
        'category': 'Crustacean',
        'description': 'Snapping shrimp produce loud snapping sounds by rapidly closing their claws. These snaps create cavitation bubbles and are one of the loudest sounds in the ocean.'
    },
    'Atlantic Croaker': {
        'category': 'Fish',
        'description': 'Atlantic croakers produce a distinctive "croaking" sound by vibrating their swim bladder. They are most vocal during breeding season.'
    },
    'Barred Grunt': {
        'category': 'Fish',
        'description': 'Barred grunts produce grunting sounds by grinding their teeth together. These sounds are used for communication and territorial defense.'
    },
    'Black Drum': {
        'category': 'Fish',
        'description': 'Black drums produce a deep drumming sound by vibrating their swim bladder. They are known for their distinctive "drumming" calls during breeding season.'
    },
    'Oyster Toadfish': {
        'category': 'Fish',
        'description': 'Oyster toadfish produce a distinctive "boat whistle" sound during breeding season. Males use these sounds to attract females to their nests.'
    },
    'Perch': {
        'category': 'Fish',
        'description': 'Perch produce a variety of sounds including grunts and clicks. They use these sounds for communication and territorial defense.'
    },
    'Scalyfin Corvina': {
        'category': 'Fish',
        'description': 'Scalyfin corvina produce a distinctive "drumming" sound during breeding season. They gather in large schools and create a chorus of sounds.'
    },
    'Midshipman': {
        'category': 'Fish',
        'description': 'Midshipman fish are known for their "humming" sounds during breeding season. Males produce these sounds to attract females to their nests.'
    },
    'Bar Jack': {
        'category': 'Fish',
        'description': 'Bar jacks produce a variety of sounds including grunts and clicks. They use these sounds for communication and maintaining school cohesion.'
    }
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
    animal_info = MARINE_ANIMALS[animal]
    return jsonify({
        'animal': animal,
        'category': animal_info['category'],
        'description': animal_info['description'],
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

# Add CORS headers for static files
@app.after_request
def add_header(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

# Ensure static files are served with correct MIME types
@app.route('/static/sounds/<path:filename>')
def serve_sound(filename):
    return send_from_directory('static/sounds', filename, mimetype='audio/wav')

if __name__ == '__main__':
    app.run(debug=True) 