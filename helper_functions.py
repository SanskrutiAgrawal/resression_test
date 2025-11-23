import os
import requests

def download_image(img_url: str, img_dir_name: str, article_index: int, driver_name: str) -> str:
    """Downloads an image from a URL and saves it to a specified path."""
    
    # Construct the image directory path
    images_dir = os.path.join(os.getcwd(), img_dir_name)
    os.makedirs(images_dir, exist_ok=True)
    
    
    img_file = f"article_{article_index + 1}_cover_{driver_name}.jpg"
    final_path = os.path.join(images_dir, img_file)

    try:
        if img_url and img_url.startswith("http"):
            print(f"Downloading image from: {img_url}")
            response = requests.get(img_url, stream=True, timeout=10)
            response.raise_for_status()
            
            with open(final_path, 'wb') as file:
                for chunk in response.iter_content(1024):
                    file.write(chunk)
            
            print(f"Cover image saved: {img_file}")
            return final_path
        else:
            print("No valid cover image URL found")
            return "N/A"
    except requests.exceptions.RequestException as e:
        print(f"Error downloading image: {e}")
        return f"Error: {e}"