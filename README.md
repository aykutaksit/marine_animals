# Marine Animal Sounds 🐋

An interactive web application that teaches children about marine animals through their sounds and images.

## Features

- Random marine animal selection
- High-quality animal images
- Authentic animal sounds
- Recording and playback functionality
- Beautiful, child-friendly interface
- Educational descriptions of each animal

## Local Development

1. Clone the repository:
```bash
git clone https://github.com/yourusername/marine_animals.git
cd marine_animals
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python app.py
```

5. Open your browser and visit `http://localhost:5000`

## Deployment

This project is configured for deployment on Render.com:

1. Create a Render.com account
2. Connect your GitHub repository
3. Create a new Web Service
4. Select the repository
5. Use the following settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
   - Python Version: 3.9.0

The application will be automatically deployed and available at your Render.com URL.

## Technologies Used

- Python/Flask
- HTML5/CSS3
- JavaScript
- Web Audio API
- Gunicorn

## License

MIT License 