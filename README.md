# Bulk Media Downloader for Kemono.su

Welcome to the Media Downloader for Kemono.su! This Python script allows you to fetch and download media files from various content platforms supported by the Kemono.su API. The script can handle multiple platforms and perform concurrent downloads to ensure efficiency.

## Features

- **Fetch Artist Data**: Retrieves data from various platforms (Patreon, Fanbox, Pixiv, Discord, Fantia, Afdian, Boosty, Gumroad, Subscribestar) using the Kemono.su API.
- **Concurrent Downloads**: Downloads media files concurrently using multiple threads to speed up the process.
- **Progress Tracking**: Displays download progress for each file.
- **Platform Support**: Handles multiple platforms with their respective API endpoints.

## Supported Platforms

- **Fanbox**
- **Patreon**
- **Pixiv**
- **Discord**
- **Fantia**
- **Afdian**
- **Boosty**
- **Gumroad**
- **Subscribestar**

## Requirements

Ensure you have Python installed on your system. The script requires the following libraries:

- `requests`: For making HTTP requests.
- `tqdm`: For displaying download progress.
- `concurrent.futures`: For handling concurrent downloads.

You can install the required libraries using pip:

```bash
pip install requests tqdm
```

## Installation

1. **Clone the Repository**:
    ```bash
    git clone https://github.com/yourusername/yourrepository.git
    cd yourrepository
    ```

2. **Install Dependencies**:
    Install the necessary Python libraries if you haven't already:
    ```bash
    pip install requests tqdm
    ```

## Usage

Run the script using Python:

```bash
python media_downloader.py
```

You will be prompted with the following steps:

1. **Enter Artist Page URL**:
   - Provide the URL of the artist's page from a supported platform. Example URLs:
     - `https://kemono.su/patreon/user/2430075`
     - `https://kemono.su/fanbox/user/23216574`

2. **Enter Download Directory**:
   - Specify the directory where you want to save the downloaded files.

The script will fetch the media files and download them to the specified directory.

## Example

### Download Media

```plaintext
Enter the artist page URL: https://kemono.su/patreon/user/2430075
Enter the directory where you want to download the files: ./downloads
```

The script will then proceed to download the media files concurrently and display progress for each file.

## Notes

- **File Size Detection**: The script uses HTTP headers to determine the file size for progress tracking.
- **Thumbnails and Zip Files**: Thumbnails and zip files are skipped during the download process.
- **Error Handling**: If an error occurs during fetching or downloading, appropriate messages are displayed.

## Troubleshooting

- **Unsupported Platform**: Ensure that the provided URL corresponds to a supported platform.
- **Download Issues**: Verify that the download directory is writable and has sufficient space.

## Contributing

Feel free to fork this repository and submit pull requests. For major changes or feature requests, please open an issue to discuss.
