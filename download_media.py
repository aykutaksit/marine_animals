import requests
from bs4 import BeautifulSoup
import os
import re
import time
from urllib.parse import urljoin

def setup_directories():
    """Create necessary directories for storing files."""
    os.makedirs('static/images', exist_ok=True)
    os.makedirs('static/sounds', exist_ok=True)

def clean_filename(name):
    """Clean the filename to be URL and filesystem friendly."""
    cleaned = re.sub(r'[^\w\s-]', '', name)
    cleaned = re.sub(r'[-\s]+', '_', cleaned)
    return cleaned.lower()

def create_session():
    """Create a session with proper headers."""
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0'
    })
    return session

def download_file(session, url, filename):
    """Download a file from URL to the specified filename."""
    try:
        response = session.get(url, stream=True)
        response.raise_for_status()
        
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        print(f"Successfully downloaded: {filename}")
        return True
    except Exception as e:
        print(f"Error downloading {filename}: {str(e)}")
        return False

def get_animal_links(session):
    """Get all animal links from the OCR sound library."""
    print("Getting animal links from OCR sound library...")
    animal_links = []
    
    try:
        # Get the main sound library page
        response = session.get("https://ocr.org/sound-library/")
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for links in different potential locations
        content_divs = soup.find_all(['div', 'ul'], class_=['sound-library', 'entry-content', 'sound-library-list'])
        
        for div in content_divs:
            links = div.find_all('a')
            for link in links:
                href = link.get('href')
                if href and '/sound-library/' in href and not href.endswith('/sound-library/'):
                    print(f"Found link: {href}")
                    animal_links.append(href)
        
        return list(set(animal_links))  # Remove duplicates
    except Exception as e:
        print(f"Error getting animal links: {str(e)}")
        return []

def process_animal_page(session, url):
    """Process a single animal page to extract image and sound URLs."""
    try:
        print(f"\nProcessing page: {url}")
        
        # Get the animal name from the URL
        animal_name = url.split('/')[-2].replace('-', ' ').title()
        print(f"Processing: {animal_name}")
        
        # Get the page content
        response = session.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the main image
        image_found = False
        for img in soup.find_all('img', class_=['wp-post-image', 'attachment-full']):
            image_url = img.get('src')
            if image_url:
                image_filename = f"static/images/{clean_filename(animal_name)}.jpg"
                if download_file(session, image_url, image_filename):
                    image_found = True
                    break
        
        if not image_found:
            # Try finding any image in the content
            for img in soup.find_all('img'):
                image_url = img.get('src')
                if image_url and ('sound-library' in image_url or 'wp-content' in image_url):
                    image_filename = f"static/images/{clean_filename(animal_name)}.jpg"
                    if download_file(session, image_url, image_filename):
                        image_found = True
                        break
        
        if not image_found:
            print(f"No image found for {animal_name}")
        
        # Find the sound file
        sound_found = False
        
        # Try finding audio element first
        audio = soup.find('audio')
        if audio:
            source = audio.find('source')
            if source:
                sound_url = source.get('src')
                if sound_url:
                    sound_filename = f"static/sounds/{clean_filename(animal_name)}.mp3"
                    if download_file(session, sound_url, sound_filename):
                        sound_found = True
        
        # If no audio element, try finding direct links
        if not sound_found:
            for link in soup.find_all('a'):
                href = link.get('href', '')
                if href.endswith(('.mp3', '.wav')):
                    ext = '.mp3' if href.endswith('.mp3') else '.wav'
                    sound_filename = f"static/sounds/{clean_filename(animal_name)}{ext}"
                    if download_file(session, href, sound_filename):
                        sound_found = True
                        break
        
        if not sound_found:
            print(f"No sound file found for {animal_name}")
        
        return True
    except Exception as e:
        print(f"Error processing {url}: {str(e)}")
        return False

def main():
    # Set up directories
    setup_directories()
    
    # Create a session with proper headers
    session = create_session()
    
    # Get all animal links
    animal_links = get_animal_links(session)
    print(f"\nTotal unique animal links found: {len(animal_links)}")
    
    # Process each animal
    for url in animal_links:
        process_animal_page(session, url)
        time.sleep(2)  # Be nice to the server

if __name__ == "__main__":
    main() 