import os
import requests
from pathlib import Path
import time
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, WebDriverException
from pydub import AudioSegment
import subprocess

def clean_filename(name):
    """Convert animal name to a clean filename."""
    name = re.sub(r'[^\w\s-]', '', name)
    return name.replace(' ', '_').lower()

def download_audio(url, filename):
    """Download an audio file from URL and save it."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        sounds_dir = Path('static/sounds')
        sounds_dir.mkdir(parents=True, exist_ok=True)
        
        filepath = sounds_dir / filename
        with open(filepath, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded: {filename}")
        return True
    except Exception as e:
        print(f"Error downloading {filename}: {str(e)}")
        return False

def convert_and_process_audio(input_file, output_file, duration=5000):
    """Convert audio file to WAV format and process it to a specific duration."""
    try:
        # Load the audio file
        audio = AudioSegment.from_file(input_file)
        
        # If the audio is shorter than the target duration, loop it
        if len(audio) < duration:
            repeats = duration // len(audio) + 1
            audio = audio * repeats
        
        # Trim to the target duration
        audio = audio[:duration]
        
        # Export as WAV
        audio.export(output_file, format='wav')
        print(f"Converted and processed: {output_file}")
        return True
    except Exception as e:
        print(f"Error converting {input_file}: {str(e)}")
        return False

def setup_driver():
    """Set up and return a configured Chrome WebDriver."""
    chrome_options = Options()
    chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--remote-debugging-port=9222')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver
    except Exception as e:
        print(f"Error setting up Chrome WebDriver: {str(e)}")
        return None

def get_animal_sounds():
    """Get animal sounds from OCR website using Selenium."""
    base_url = 'https://ocr.org'
    
    # Known animal pages with their display names
    animals = {
        '/sound-library/right-whale/': 'Right Whale',
        '/sound-library/orca/': 'Orca',
        '/sound-library/cuviers-beaked-whale/': 'Cuvier\'s Beaked Whale',
        '/sound-library/leopard-seal/': 'Leopard Seal',
        '/sound-library/manatee/': 'Manatee',
        '/sound-library/dolphin/': 'Dolphin',
        '/sound-library/humpback-whale/': 'Humpback Whale',
        '/sound-library/gray-whale/': 'Gray Whale',
        '/sound-library/bowhead-whale/': 'Bowhead Whale',
        '/sound-library/weddell-seal/': 'Weddell Seal',
        '/sound-library/sperm-whale/': 'Sperm Whale',
        '/sound-library/minke-whale/': 'Minke Whale',
        '/sound-library/ringed-seal/': 'Ringed Seal',
        '/sound-library/belugas/': 'Beluga',
        '/sound-library/rissos-dolphin/': 'Risso\'s Dolphin',
        '/sound-library/harbor-seal/': 'Harbor Seal',
        '/sound-library/pilot-whale/': 'Pilot Whale',
        '/sound-library/walrus/': 'Walrus'
    }
    
    # Check which sounds we already have
    sounds_dir = Path('static/sounds')
    existing_sounds = {f.stem.replace('processed_', '') for f in sounds_dir.glob('processed_*.wav')}
    
    # Keep track of downloaded sounds to avoid duplicates
    downloaded_urls = set()
    
    print("Setting up Chrome WebDriver...")
    driver = setup_driver()
    
    if not driver:
        print("Failed to set up Chrome WebDriver. Exiting.")
        return
    
    try:
        print("Starting to process animal pages...")
        for path, display_name in animals.items():
            animal_name = clean_filename(display_name)
            
            # Skip if we already have the sound
            if animal_name in existing_sounds:
                print(f"\nSkipping {display_name} - sound already exists")
                continue
            
            animal_url = urljoin(base_url, path)
            print(f"\nProcessing {display_name}...")
            
            try:
                print(f"Accessing {animal_url}")
                driver.get(animal_url)
                
                # Wait for content to load with longer timeout
                try:
                    wait = WebDriverWait(driver, 30)  # Increased timeout to 30 seconds
                    wait.until(EC.presence_of_element_located((By.TAG_NAME, 'article')))
                except TimeoutException:
                    print(f"Timeout waiting for {display_name} page to load")
                    continue
                
                # Give more time for dynamic content to load
                time.sleep(5)  # Increased wait time to 5 seconds
                
                # Parse the page
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                
                # Try different ways to find the content
                content = None
                for selector in [
                    ('article', {}),
                    ('div', {'class': 'post'}),
                    ('div', {'class': 'entry'}),
                    ('div', {'class': 'content-area'}),
                    ('div', {'class': 'entry-content'})
                ]:
                    content = soup.find(selector[0], selector[1])
                    if content:
                        break
                
                if not content:
                    print(f"No content found for {display_name}")
                    continue
                
                # Find audio elements with more variations
                audio_elements = []
                
                # Look for standard audio elements
                audio_elements.extend(content.find_all(['audio', 'source']))
                
                # Look for video elements (they might contain audio)
                video_elements = content.find_all('video')
                for video in video_elements:
                    sources = video.find_all('source')
                    audio_elements.extend(sources)
                
                # Look for links that might be audio files
                links = content.find_all('a', href=re.compile(r'\.(mp3|wav|m4a|ogg|mp4)$'))
                audio_elements.extend(links)
                
                if not audio_elements:
                    print(f"No audio elements found for {display_name}")
                    
                    # Try JavaScript rendered content
                    try:
                        # Execute JavaScript to get dynamically loaded content
                        dynamic_content = driver.execute_script("return document.documentElement.outerHTML;")
                        dynamic_soup = BeautifulSoup(dynamic_content, 'html.parser')
                        
                        # Look for audio URLs in the dynamic content
                        audio_urls = re.findall(r'https?://[^\s<>"]+?\.(?:mp3|wav|m4a|ogg|mp4)[^\s<>"]*', dynamic_content)
                        for url in audio_urls:
                            audio_elements.append({'src': url})
                    except Exception as e:
                        print(f"Error getting dynamic content: {str(e)}")
                    
                    if not audio_elements:
                        continue
                
                # Try to find a unique audio file
                audio_found = False
                for audio in audio_elements:
                    # Get the audio URL from various possible attributes
                    audio_url = None
                    for attr in ['src', 'href', 'data-src']:
                        audio_url = audio.get(attr)
                        if audio_url:
                            break
                    
                    if not audio_url:
                        continue
                    
                    if not audio_url.startswith('http'):
                        audio_url = urljoin(base_url, audio_url)
                    
                    # Skip if we've already downloaded this URL
                    if audio_url in downloaded_urls:
                        continue
                    
                    print(f"Found audio URL: {audio_url}")
                    
                    # Download the audio file
                    temp_file = sounds_dir / f"temp_{animal_name}.mp3"
                    if download_audio(audio_url, temp_file.name):
                        # Convert and process to WAV
                        output_file = sounds_dir / f"processed_{animal_name}.wav"
                        if convert_and_process_audio(temp_file, output_file):
                            downloaded_urls.add(audio_url)
                            audio_found = True
                            # Clean up temp file
                            temp_file.unlink()
                            break
                
                if not audio_found:
                    print(f"No unique audio found for {display_name}")
                
                time.sleep(2)  # Be nice to the server
                
            except WebDriverException as e:
                print(f"WebDriver error processing {display_name}: {str(e)}")
                continue
            except Exception as e:
                print(f"Error processing {display_name}: {str(e)}")
                continue
    
    except Exception as e:
        print(f"Error: {str(e)}")
    
    finally:
        print("Closing browser...")
        driver.quit()
    
    print(f"\nSound download complete! Downloaded {len(downloaded_urls)} unique sounds.")

if __name__ == '__main__':
    get_animal_sounds() 