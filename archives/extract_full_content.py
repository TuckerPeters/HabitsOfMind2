#!/usr/bin/env python3
"""
Extract full content from WordPress SQL dump including titles, dates, and content
"""
import re
import json
import csv
from html.parser import HTMLParser

class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs= True
        self.text = []
    def handle_data(self, d):
        self.text.append(d)
    def get_data(self):
        return ''.join(self.text)

def strip_tags(html):
    s = MLStripper()
    try:
        s.feed(html)
        return s.get_data()
    except:
        return html

def parse_wp_record(line, post_type):
    """Parse a single WordPress post record"""
    try:
        # Extract fields using regex - WordPress INSERT format:
        # (ID, author, date, date_gmt, content, title, excerpt, status, comment_status, ping_status, password, name, ...)

        # Match the pattern more carefully
        pattern = r'\((\d+),\s*(\d+),\s*\'([^\']*)\',\s*\'([^\']*)\',\s*\'((?:[^\']|\\\')*)\',\s*\'((?:[^\']|\\\')*)\',\s*\'((?:[^\']|\\\')*)\'.*?\'(publish)\'.*?\'%s\'' % post_type

        match = re.search(pattern, line, re.DOTALL)
        if not match:
            return None

        post_id, author, date, date_gmt, content, title, excerpt, status = match.groups()[:8]

        # Clean up escaped quotes
        content = content.replace("\\'", "'").replace("\\\"", '"')
        title = title.replace("\\'", "'").replace("\\\"", '"')
        excerpt = excerpt.replace("\\'", "'").replace("\\\"", '"')

        # Extract post_name (slug) if possible
        slug_match = re.search(r"'([a-z0-9-]+)',\s*'',\s*'',\s*'[^']*',\s*'[^']*',\s*'',\s*\d+,\s*'[^']*',\s*\d+,\s*'%s'" % post_type, line)
        slug = slug_match.group(1) if slug_match else f"post-{post_id}"

        return {
            'id': post_id,
            'author_id': author,
            'date': date,
            'title': title[:200],  # Limit for safety
            'slug': slug,
            'excerpt': excerpt[:500] if excerpt else '',
            'content': content[:5000],  # First 5000 chars
            'content_length': len(content),
            'type': post_type
        }
    except Exception as e:
        print(f"Error parsing record: {e}")
        return None

def extract_content():
    """Extract and categorize all content"""

    sql_file = '/Volumes/SANDISK/public_html_copy/localhost.sql'

    posts = []
    pages = []
    downloads = []
    consultants = []

    print("Reading SQL file and extracting full content...")

    with open(sql_file, 'r', encoding='utf-8', errors='ignore') as f:
        for i, line in enumerate(f):
            # Look for lines with published content
            if "'publish'" not in line:
                continue

            if "'post'" in line and len(line) > 100:
                record = parse_wp_record(line, 'post')
                if record and record not in posts:
                    posts.append(record)
                    if len(posts) % 10 == 0:
                        print(f"Found {len(posts)} blog posts...")

            elif "'page'" in line and len(line) > 100:
                record = parse_wp_record(line, 'page')
                if record and record not in pages:
                    pages.append(record)

            elif "'dlm_download'" in line and len(line) > 100:
                record = parse_wp_record(line, 'dlm_download')
                if record and record not in downloads:
                    downloads.append(record)

            elif "'consultant'" in line and len(line) > 100:
                record = parse_wp_record(line, 'consultant')
                if record and record not in consultants:
                    consultants.append(record)

            if i % 200000 == 0:
                print(f"Scanned {i:,} lines - Posts: {len(posts)}, Pages: {len(pages)}, Downloads: {len(downloads)}, Consultants: {len(consultants)}")

            # Stop after collecting enough
            if len(posts) > 500:
                break

    return posts, pages, downloads, consultants

def save_to_files(posts, pages, downloads, consultants):
    """Save extracted content to JSON and CSV files"""

    output_dir = '/Users/tuckerpeters/HabitsOfMind2/extracted_content'

    import os
    os.makedirs(output_dir, exist_ok=True)

    # Save as JSON
    with open(f'{output_dir}/blog_posts.json', 'w', encoding='utf-8') as f:
        json.dump(posts, f, indent=2, ensure_ascii=False)

    with open(f'{output_dir}/pages.json', 'w', encoding='utf-8') as f:
        json.dump(pages[:100], f, indent=2, ensure_ascii=False)  # Limit pages

    with open(f'{output_dir}/downloads.json', 'w', encoding='utf-8') as f:
        json.dump(downloads, f, indent=2, ensure_ascii=False)

    with open(f'{output_dir}/consultants.json', 'w', encoding='utf-8') as f:
        json.dump(consultants, f, indent=2, ensure_ascii=False)

    # Save posts as CSV for easier review
    if posts:
        with open(f'{output_dir}/blog_posts.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['id', 'date', 'title', 'slug', 'excerpt', 'content_length'])
            writer.writeheader()
            for post in posts:
                writer.writerow({
                    'id': post['id'],
                    'date': post['date'],
                    'title': post['title'],
                    'slug': post['slug'],
                    'excerpt': strip_tags(post['excerpt'])[:200],
                    'content_length': post['content_length']
                })

    print(f"\nSaved files to {output_dir}/")
    print(f"  - blog_posts.json ({len(posts)} posts)")
    print(f"  - blog_posts.csv ({len(posts)} posts)")
    print(f"  - pages.json ({min(len(pages), 100)} pages)")
    print(f"  - downloads.json ({len(downloads)} downloads)")
    print(f"  - consultants.json ({len(consultants)} consultants)")

if __name__ == '__main__':
    posts, pages, downloads, consultants = extract_content()

    print(f"\n\nExtraction Summary:")
    print(f"==================")
    print(f"Blog Posts: {len(posts)}")
    print(f"Pages: {len(pages)}")
    print(f"Downloads: {len(downloads)}")
    print(f"Consultants: {len(consultants)}")

    save_to_files(posts, pages, downloads, consultants)

    print("\n✓ Extraction complete!")
