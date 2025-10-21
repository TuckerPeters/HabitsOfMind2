#!/usr/bin/env python3
"""
Blog scraper for Habits of Mind Institute blog.
Extracts blog posts with content, metadata, and images.
"""

import requests
from bs4 import BeautifulSoup
import json
import re
from urllib.parse import urljoin, urlparse
from datetime import datetime
import time
import os

def get_page_soup(url):
    """Fetch and parse a webpage"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return BeautifulSoup(response.content, 'html.parser')
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def extract_blog_posts(base_url):
    """Extract blog posts from the blog listing page"""
    soup = get_page_soup(base_url)
    if not soup:
        return []

    blog_posts = []

    # Look for blog post links - common patterns
    post_selectors = [
        'article a[href*="blog"]',
        '.blog-post a[href]',
        '.post-title a[href]',
        'h2 a[href]',
        'h3 a[href]',
        '.entry-title a[href]',
        '.post-link[href]',
        'a[href*="/blog/"]',
        'a[href*="/post/"]'
    ]

    post_links = set()

    for selector in post_selectors:
        links = soup.select(selector)
        for link in links:
            href = link.get('href')
            if href:
                full_url = urljoin(base_url, href)
                # Filter out pagination, categories, tags, etc.
                if not any(exclude in full_url.lower() for exclude in ['page/', 'category/', 'tag/', 'author/', '?page=', '#']):
                    post_links.add(full_url)

    # Also check for pagination to get more blog posts
    pagination_links = soup.select('a[href*="page"]')
    all_blog_pages = [base_url]

    for link in pagination_links[:10]:  # Limit to first 10 pages
        href = link.get('href')
        if href:
            page_url = urljoin(base_url, href)
            if page_url not in all_blog_pages:
                all_blog_pages.append(page_url)

    # Crawl additional blog pages
    for page_url in all_blog_pages[1:]:  # Skip first page (already processed)
        print(f"Crawling blog page: {page_url}")
        page_soup = get_page_soup(page_url)
        if page_soup:
            for selector in post_selectors:
                links = page_soup.select(selector)
                for link in links:
                    href = link.get('href')
                    if href:
                        full_url = urljoin(base_url, href)
                        if not any(exclude in full_url.lower() for exclude in ['page/', 'category/', 'tag/', 'author/', '?page=', '#']):
                            post_links.add(full_url)
        time.sleep(1)  # Be respectful

    print(f"Found {len(post_links)} potential blog posts")

    # Extract content from each blog post
    for i, post_url in enumerate(list(post_links)[:50]):  # Limit to first 50 posts
        print(f"Processing post {i+1}: {post_url}")
        post_data = extract_post_content(post_url)
        if post_data:
            blog_posts.append(post_data)
        time.sleep(0.5)  # Be respectful to the server

    return blog_posts

def extract_post_content(post_url):
    """Extract content from a single blog post"""
    soup = get_page_soup(post_url)
    if not soup:
        return None

    post_data = {
        'url': post_url,
        'scraped_at': datetime.now().isoformat(),
        'title': '',
        'author': '',
        'date': '',
        'content': '',
        'excerpt': '',
        'images': [],
        'categories': [],
        'tags': []
    }

    # Extract title
    title_selectors = ['h1', '.post-title', '.entry-title', 'title']
    for selector in title_selectors:
        title_elem = soup.select_one(selector)
        if title_elem:
            post_data['title'] = title_elem.get_text().strip()
            break

    # Extract content
    content_selectors = [
        '.post-content',
        '.entry-content',
        '.blog-content',
        'article .content',
        '.post-body',
        'article',
        '.single-post',
        '.blog-post'
    ]

    content_elem = None
    for selector in content_selectors:
        content_elem = soup.select_one(selector)
        if content_elem:
            break

    if content_elem:
        # Remove unwanted elements
        for unwanted in content_elem.select('script, style, .social-share, .related-posts, .comments'):
            unwanted.decompose()

        post_data['content'] = content_elem.get_text().strip()

    # Extract images from the post
    images = []

    # Look for images in content area first, then fallback to whole page
    img_parent = content_elem if content_elem else soup

    for img in img_parent.select('img'):
        src = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
        if src:
            full_img_url = urljoin(post_url, src)

            # Get alt text and other metadata
            img_data = {
                'src': full_img_url,
                'alt': img.get('alt', ''),
                'title': img.get('title', ''),
                'width': img.get('width', ''),
                'height': img.get('height', ''),
                'class': img.get('class', [])
            }

            # Filter out tiny images, icons, etc.
            if not any(skip in src.lower() for skip in ['icon', 'logo', 'avatar', 'social']):
                images.append(img_data)

    # Also look for featured image / thumbnail
    featured_img_selectors = [
        '.featured-image img',
        '.post-thumbnail img',
        '.entry-image img',
        '.blog-image img',
        'meta[property="og:image"]',
        'meta[name="twitter:image"]'
    ]

    for selector in featured_img_selectors:
        elem = soup.select_one(selector)
        if elem:
            if elem.name == 'meta':
                src = elem.get('content')
            else:
                src = elem.get('src') or elem.get('data-src')

            if src:
                full_img_url = urljoin(post_url, src)
                img_data = {
                    'src': full_img_url,
                    'alt': elem.get('alt', '') if elem.name != 'meta' else 'Featured image',
                    'title': 'Featured image',
                    'featured': True
                }

                # Add if not already present
                if not any(img['src'] == full_img_url for img in images):
                    images.insert(0, img_data)  # Put featured image first

    post_data['images'] = images

    # Extract author
    author_selectors = ['.author', '.post-author', '.by-author', '.entry-author']
    for selector in author_selectors:
        author_elem = soup.select_one(selector)
        if author_elem:
            post_data['author'] = author_elem.get_text().strip()
            break

    # Extract date
    date_selectors = [
        'time[datetime]',
        '.post-date',
        '.entry-date',
        '.published-date',
        'meta[property="article:published_time"]'
    ]

    for selector in date_selectors:
        date_elem = soup.select_one(selector)
        if date_elem:
            if date_elem.name == 'meta':
                post_data['date'] = date_elem.get('content', '')
            elif date_elem.name == 'time':
                post_data['date'] = date_elem.get('datetime') or date_elem.get_text().strip()
            else:
                post_data['date'] = date_elem.get_text().strip()
            break

    # Extract categories and tags
    category_selectors = ['.categories a', '.post-categories a', '.entry-categories a']
    for selector in category_selectors:
        cat_links = soup.select(selector)
        for link in cat_links:
            post_data['categories'].append(link.get_text().strip())

    tag_selectors = ['.tags a', '.post-tags a', '.entry-tags a']
    for selector in tag_selectors:
        tag_links = soup.select(selector)
        for link in tag_links:
            post_data['tags'].append(link.get_text().strip())

    # Create excerpt from content
    if post_data['content']:
        # Clean up content and create excerpt
        content = re.sub(r'\s+', ' ', post_data['content'])
        sentences = content.split('.')[:3]  # First 3 sentences
        post_data['excerpt'] = '. '.join(sentences).strip()
        if post_data['excerpt'] and not post_data['excerpt'].endswith('.'):
            post_data['excerpt'] += '.'

    return post_data

def main():
    blog_url = "https://www.habitsofmindinstitute.org/habits-of-mind-blog/"

    print(f"Starting to crawl: {blog_url}")

    blog_posts = extract_blog_posts(blog_url)

    print(f"\nExtracted {len(blog_posts)} blog posts")

    # Save to JSON
    output_file = "habits_of_mind_blog_posts.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'scraped_at': datetime.now().isoformat(),
            'source_url': blog_url,
            'total_posts': len(blog_posts),
            'posts': blog_posts
        }, f, indent=2, ensure_ascii=False)

    print(f"Blog posts saved to: {output_file}")

    # Print summary
    total_images = sum(len(post.get('images', [])) for post in blog_posts)
    print(f"Total images found: {total_images}")

    if blog_posts:
        print(f"\nSample post:")
        sample = blog_posts[0]
        print(f"Title: {sample.get('title', 'N/A')}")
        print(f"URL: {sample.get('url', 'N/A')}")
        print(f"Images: {len(sample.get('images', []))}")
        print(f"Content length: {len(sample.get('content', ''))}")

if __name__ == "__main__":
    main()