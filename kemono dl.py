import os
import requests
import urllib.parse
from pathlib import Path
from tqdm import tqdm
import concurrent.futures

# Mapping of platforms to their respective API endpoints
platform_api_endpoints = {
    'fanbox': 'https://kemono.su/api/v1/fanbox/user/{user_id}',
    'patreon': 'https://kemono.su/api/v1/patreon/user/{user_id}',
    'pixiv': 'https://kemono.su/api/v1/pixiv/user/{user_id}',
    'discord': 'https://kemono.su/api/v1/discord/user/{user_id}',
    'fantia': 'https://kemono.su/api/v1/fantia/user/{user_id}',
    'afdian': 'https://kemono.su/api/v1/afdian/user/{user_id}',
    'boosty': 'https://kemono.su/api/v1/boosty/user/{user_id}',
    'gumroad': 'https://kemono.su/api/v1/gumroad/user/{user_id}',
    'subscribestar': 'https://kemono.su/api/v1/subscribestar/user/{user_id}'
}

# Media file formats (images, videos, gifs, etc.)
media_file_extensions = {
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.heif', '.heic',  # Image formats
    '.mp4', '.webm', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.mpeg', '.mpg',  # Video formats
    '.ogv', '.3gp',  # Other video formats
    '.apng', '.gifv', '.m4v'  # Animated Image/Video formats
}

def fetch_artist_data(artist_url):
    # Extract platform and user ID from the provided URL
    parsed_url = urllib.parse.urlparse(artist_url)
    platform = parsed_url.path.split('/')[1]
    user_id = parsed_url.path.split('/')[-1]

    # Ensure platform is valid
    if platform not in platform_api_endpoints:
        print("Unsupported platform. Please provide a valid URL.")
        return None

    # Fetch all pages of data
    artist_data = []
    offset = 0
    total_pages = 0
    print("Loading pages...")

    # First, calculate the total number of pages (for progress bar)
    while True:
        api_url = f"https://kemono.su/api/v1/{platform}/user/{user_id}?o={offset}"
        headers = {'accept': 'application/json'}
        
        response = requests.get(api_url, headers=headers)
        if response.status_code == 200:
            page_data = response.json()
            if not page_data:  # No more data
                break
            total_pages += 1
            offset += 50  # Move to the next page
        else:
            print(f"Failed to fetch data from {platform.capitalize()} API. Status code: {response.status_code}")
            break

    # Create a progress bar for page loading
    with tqdm(total=total_pages, desc="Loading pages", ncols=100) as page_bar:
        offset = 0
        while True:
            api_url = f"https://kemono.su/api/v1/{platform}/user/{user_id}?o={offset}"
            response = requests.get(api_url, headers=headers)
            if response.status_code == 200:
                page_data = response.json()
                if not page_data:  # No more data
                    break
                artist_data.extend(page_data)
                offset += 50  # Move to the next page
                page_bar.update(1)
            else:
                print(f"Failed to fetch data from {platform.capitalize()} API. Status code: {response.status_code}")
                break

    return artist_data

def download_file(file_url, file_name, download_dir, progress_bar):
    try:
        # Get file size for progress bar
        file_size = int(requests.head(file_url).headers.get("Content-Length", 0))
    except KeyError:
        print(f"Failed to get file size for {file_name}")
        return

    with requests.get(file_url, stream=True) as r:
        r.raise_for_status()
        with open(os.path.join(download_dir, file_name), 'wb') as f:
            with tqdm(total=file_size, unit='B', unit_scale=True, desc=file_name, ncols=100, position=1, leave=False) as pbar:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        pbar.update(len(chunk))

    # Now update the total progress bar (this is what you're asking for)
    progress_bar.update(1)  # This updates the single progress bar showing total progress
    print(f"Downloaded: {file_name}")

def download_media_files(artist_data, download_dir, download_all):
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    # Prepare media download files and calculate total number of files
    total_files = 0
    for post in artist_data:
        if 'attachments' in post:
            for attachment in post['attachments']:
                file_name = attachment['name']
                # Check if the file is a media file based on its extension
                if download_all or any(file_name.lower().endswith(ext) for ext in media_file_extensions):
                    total_files += 1

    # Create a single total progress bar for all downloads (this is what you're asking for)
    with tqdm(total=total_files, desc="Downloading media", ncols=100) as progress_bar:
        # Create a ThreadPoolExecutor with 5 concurrent threads
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            for post in artist_data:
                if 'attachments' in post:
                    for attachment in post['attachments']:
                        file_name = attachment['name']
                        file_url = f'https://kemono.su{attachment["path"]}'

                        # Skip thumbnails and zip files, unless downloading everything
                        if download_all or (not file_name.endswith('.zip') and not '_thumb' in file_name and any(file_name.lower().endswith(ext) for ext in media_file_extensions)):
                            futures.append(executor.submit(download_file, file_url, file_name, download_dir, progress_bar))

            # Wait for all futures (downloads) to complete
            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    print(f"Exception occurred: {e}")

def main():
    # Ask user for the artist page URL
    artist_url = input("Enter the artist page URL: ").strip()

    # Ask if the user wants to download everything or just media files
    download_option = input("Do you want to download (1) everything or (2) just media files? (Enter 1 or 2): ").strip()

    # Fetch artist data from respective platform API
    artist_data = fetch_artist_data(artist_url)

    if artist_data:
        # Prompt user to choose download directory
        download_dir = input("Enter the directory where you want to download the files: ").strip()

        # Download media files concurrently
        download_media_files(artist_data, download_dir, download_option == '1')
        print("Download completed!")
    else:
        print("Failed to fetch artist data. Please check the provided URL and try again.")

if __name__ == "__main__":
    main()
