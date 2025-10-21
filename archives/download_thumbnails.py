#!/usr/bin/env python3
"""
Download authentic blog thumbnail images locally
"""

import json
import requests
import os
from urllib.parse import urlparse
import time

def download_image(url, local_path):
    """Download an image from URL to local path"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(local_path), exist_ok=True)

        with open(local_path, 'wb') as f:
            f.write(response.content)

        print(f"Downloaded: {url} -> {local_path}")
        return True

    except Exception as e:
        print(f"Failed to download {url}: {e}")
        return False

def main():
    # Load the scraped blog posts
    with open('habits_of_mind_blog_posts.json', 'r') as f:
        blog_data = json.load(f)

    # Create thumbnails directory
    thumbnails_dir = 'frontend/static/images/blog-thumbnails'
    os.makedirs(thumbnails_dir, exist_ok=True)

    downloaded_images = {}

    for i, post in enumerate(blog_data['posts']):
        print(f"\nProcessing post {i+1}: {post['title']}")

        # Find the featured image
        featured_img = None
        for img in post.get('images', []):
            if img.get('featured', False):
                featured_img = img
                break

        if not featured_img and post.get('images'):
            # Use first image if no featured image
            featured_img = post['images'][0]

        if featured_img:
            img_url = featured_img['src']

            # Parse URL to get filename
            parsed = urlparse(img_url)
            filename = os.path.basename(parsed.path)

            # If no extension, try to determine from URL
            if '.' not in filename:
                if '.png' in img_url.lower():
                    filename += '.png'
                elif '.jpg' in img_url.lower() or '.jpeg' in img_url.lower():
                    filename += '.jpg'
                elif '.webp' in img_url.lower():
                    filename += '.webp'
                else:
                    filename += '.jpg'  # default

            # Create a clean filename based on post title
            clean_title = "".join(c for c in post['title'] if c.isalnum() or c in (' ', '-')).rstrip()
            clean_title = clean_title.replace(' ', '-').lower()[:50]  # Limit length

            # Get file extension
            ext = filename.split('.')[-1]
            local_filename = f"{clean_title}.{ext}"

            local_path = os.path.join(thumbnails_dir, local_filename)

            # Download the image
            if download_image(img_url, local_path):
                downloaded_images[post['url']] = {
                    'original_url': img_url,
                    'local_path': f"/images/blog-thumbnails/{local_filename}",
                    'title': post['title'],
                    'post_url': post['url']
                }

            # Be respectful to the server
            time.sleep(1)
        else:
            print(f"No suitable image found for: {post['title']}")

    # Save mapping of downloaded images
    with open('downloaded_thumbnails.json', 'w') as f:
        json.dump(downloaded_images, f, indent=2)

    print(f"\nDownloaded {len(downloaded_images)} thumbnails")
    print("Mapping saved to downloaded_thumbnails.json")

if __name__ == "__main__":
    main()