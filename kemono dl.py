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

def fetch_artist_data(artist_url):
    # Extract platform and user ID from the provided URL
    parsed_url = urllib.parse.urlparse(artist_url)
    platform = parsed_url.path.split('/')[1]
    user_id = parsed_url.path.split('/')[-1]

    # Ensure platform is valid
    if platform not in platform_api_endpoints:
        print("Unsupported platform. Please provide a valid URL.")
        return None

    # Construct API request URL
    api_url = platform_api_endpoints[platform].format(user_id=user_id)
    headers = {'accept': 'application/json'}

    # Make GET request to respective platform API
    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch data from {platform.capitalize()} API. Status code: {response.status_code}")
        return None

def download_file(file_url, file_name, download_dir):
    try:
        # Get file size for progress bar
        file_size = int(requests.head(file_url).headers["Content-Length"])
    except KeyError:
        print(f"Failed to get file size for {file_name}")
        return

    with requests.get(file_url, stream=True) as r:
        r.raise_for_status()
        with open(os.path.join(download_dir, file_name), 'wb') as f:
            with tqdm(total=file_size, unit='B', unit_scale=True, desc=file_name, ncols=100) as pbar:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        pbar.update(len(chunk))

    print(f"Downloaded: {file_name}")

def download_media_files(artist_data, download_dir):
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    # Create a ThreadPoolExecutor with 5 concurrent threads
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = []
        for post in artist_data:
            if 'attachments' in post:
                for attachment in post['attachments']:
                    file_path = attachment['path']
                    file_name = attachment['name']
                    file_url = f'https://kemono.su{file_path}'

                    # Skip thumbnails and zip files
                    if not file_name.endswith('.zip') and not '_thumb' in file_name:
                        futures.append(executor.submit(download_file, file_url, file_name, download_dir))

        # Wait for all futures (downloads) to complete
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"Exception occurred: {e}")

def main():
    # Example links:
    # https://kemono.su/patreon/user/2430075
    # https://kemono.su/fanbox/user/23216574

    # Ask user for the artist page URL
    artist_url = input("Enter the artist page URL: ").strip()

    # Fetch artist data from respective platform API
    artist_data = fetch_artist_data(artist_url)

    if artist_data:
        # Prompt user to choose download directory
        download_dir = input("Enter the directory where you want to download the files: ").strip()

        # Download media files concurrently
        download_media_files(artist_data, download_dir)
        print("Download completed!")
    else:
        print("Failed to fetch artist data. Please check the provided URL and try again.")

if __name__ == "__main__":
    main()