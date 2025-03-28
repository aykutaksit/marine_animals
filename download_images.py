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

def clean_filename(name):
    """Convert animal name to a clean filename."""
    name = re.sub(r'[^\w\s-]', '', name)
    return name.replace(' ', '_').lower()

def download_image(url, filename):
    """Download an image from URL and save it."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        images_dir = Path('static/images')
        images_dir.mkdir(parents=True, exist_ok=True)
        
        filepath = images_dir / filename
        with open(filepath, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded: {filename}")
        return True
    except Exception as e:
        print(f"Error downloading {filename}: {str(e)}")
        return False

def setup_driver():
    """Set up and return a configured Chrome WebDriver."""
    chrome_options = Options()
    chrome_options.add_argument('--headless=new')  # Use new headless mode
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

def get_animal_images():
    """Get animal images from OCR website using Selenium."""
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
    
    # Default images to skip
    default_images = {
        'harbor-seal-horizontal.png',
        'default-image.jpg'
    }
    
    # Keep track of downloaded images to avoid duplicates
    downloaded_urls = set()
    
    print("Setting up Chrome WebDriver...")
    driver = setup_driver()
    
    if not driver:
        print("Failed to set up Chrome WebDriver. Exiting.")
        return
    
    try:
        print("Starting to process animal pages...")
        for path, display_name in animals.items():
            animal_url = urljoin(base_url, path)
            print(f"\nProcessing {display_name}...")
            
            try:
                print(f"Accessing {animal_url}")
                driver.get(animal_url)
                
                # Wait for content to load with timeout
                try:
                    wait = WebDriverWait(driver, 10)
                    wait.until(EC.presence_of_element_located((By.TAG_NAME, 'article')))
                except TimeoutException:
                    print(f"Timeout waiting for {display_name} page to load")
                    continue
                
                # Give a short time for images to load
                time.sleep(2)
                
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
                
                # Find all images in the content
                images = []
                for selector in [
                    ('img', {'class': 'wp-post-image'}),
                    ('img', {'class': 'featured-image'}),
                    ('img', {'class': 'attachment-post-thumbnail'}),
                    ('img', {'class': 'size-medium'}),
                    ('img', {})
                ]:
                    found_images = content.find_all(selector[0], selector[1])
                    for img in found_images:
                        if img.get('src') and any(ext in img['src'].lower() for ext in ['.jpg', '.jpeg', '.png']):
                            images.append(img)
                
                # Try to find a unique image for this animal
                image_found = False
                for image in images:
                    if 'src' in image.attrs:
                        image_url = image['src']
                        if not image_url.startswith('http'):
                            image_url = urljoin(base_url, image_url)
                        
                        # Skip if it's a default image or we've already downloaded it
                        if any(default in image_url for default in default_images) or image_url in downloaded_urls:
                            continue
                        
                        print(f"Found unique image URL: {image_url}")
                        filename = f"{clean_filename(display_name)}.jpg"
                        if download_image(image_url, filename):
                            downloaded_urls.add(image_url)
                            image_found = True
                            break
                
                if not image_found:
                    print(f"No unique image found for {display_name}")
                
                time.sleep(1)  # Be nice to the server
                
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
    
    print(f"\nImage download complete! Downloaded {len(downloaded_urls)} unique images.")

if __name__ == '__main__':
    get_animal_images() 