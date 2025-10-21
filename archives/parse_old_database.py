#!/usr/bin/env python3
"""
Parse old WordPress database to extract content for migration
"""
import re
import json
import sys

def extract_wp_posts(sql_file):
    """Extract published posts, pages, and downloads from wp_posts table"""

    posts = []
    pages = []
    downloads = []
    consultants = []

    print("Reading SQL file...")
    with open(sql_file, 'r', encoding='utf-8', errors='ignore') as f:
        in_wp_posts = False
        buffer = ""

        for line_num, line in enumerate(f):
            # Track when we're in wp_posts INSERT statements
            if 'INSERT INTO `wp_posts`' in line:
                in_wp_posts = True
                buffer = line
                continue

            if in_wp_posts:
                buffer += line

                # Stop when we hit another table
                if line.startswith('CREATE TABLE') or (line.startswith('INSERT INTO') and 'wp_posts' not in line):
                    in_wp_posts = False
                    break

            # Process buffer every 1000 lines to avoid memory issues
            if in_wp_posts and len(buffer) > 100000:
                process_buffer(buffer, posts, pages, downloads, consultants)
                buffer = ""

            if line_num % 100000 == 0:
                print(f"Processed {line_num:,} lines... Found {len(posts)} posts, {len(pages)} pages, {len(downloads)} downloads")

        # Process remaining buffer
        if buffer:
            process_buffer(buffer, posts, pages, downloads, consultants)

    return posts, pages, downloads, consultants

def process_buffer(buffer, posts, pages, downloads, consultants):
    """Process a buffer of INSERT statements"""

    # Split on ),( to get individual records
    # This is a simplified parser - may need refinement
    records = re.findall(r'\((\d+),\s*(\d+),\s*\'([^\']*)\',\s*\'([^\']*)\',\s*\'(.*?)\',\s*\'(.*?)\',\s*\'(.*?)\',\s*\'(.*?)\',', buffer, re.DOTALL)

    for record in records:
        try:
            id_val, author, post_date, post_date_gmt, content_start = record[:5]

            # Extract more fields - need to handle escaping
            # Looking for: post_content, post_title, post_excerpt, post_status, ..., post_type

            # For now, let's use a simpler regex for complete records
            full_pattern = r'\((\d+),.*?\'([^\']+)\',\s*\'([^\']+)\',.*?\'(.*?)\',\s*\'(.*?)\',\s*\'.*?\',\s*\'(publish)\',.*?\'(post|page|dlm_download|consultant)\''

        except Exception as e:
            continue

def simple_extract(sql_file, output_dir):
    """Simpler extraction using grep-like approach"""

    print("Extracting blog posts...")
    with open(sql_file, 'r', encoding='utf-8', errors='ignore') as f:
        line_buffer = []
        for i, line in enumerate(f):
            if "'post'" in line and "'publish'" in line:
                line_buffer.append(line.strip())
            elif "'page'" in line and "'publish'" in line:
                line_buffer.append(line.strip())
            elif "'dlm_download'" in line and "'publish'" in line:
                line_buffer.append(line.strip())
            elif "'consultant'" in line and "'publish'" in line:
                line_buffer.append(line.strip())

            if i % 50000 == 0:
                print(f"Scanned {i:,} lines, found {len(line_buffer)} items")

            # Limit to first 10000 matches to avoid memory issues
            if len(line_buffer) > 10000:
                break

    # Parse these lines more carefully
    posts = []
    pages = []
    downloads = []
    consultants = []

    for line in line_buffer:
        # Extract ID and post_title at minimum
        # Pattern: (ID, author, date, date_gmt, content, title, ...)
        match = re.search(r'\((\d+),\s*\d+,.*?\'([^\']*)\',.*?\'([^\']*)\',', line)
        if match:
            item_id, date, title_or_content = match.groups()

            # Determine type
            if "'post'" in line:
                posts.append({'id': item_id, 'line': line[:500]})
            elif "'page'" in line:
                pages.append({'id': item_id, 'line': line[:500]})
            elif "'dlm_download'" in line:
                downloads.append({'id': item_id, 'line': line[:500]})
            elif "'consultant'" in line:
                consultants.append({'id': item_id, 'line': line[:500]})

    # Save summaries
    with open(f'{output_dir}/posts_summary.json', 'w') as f:
        json.dump(posts[:100], f, indent=2)

    with open(f'{output_dir}/pages_summary.json', 'w') as f:
        json.dump(pages[:100], f, indent=2)

    with open(f'{output_dir}/downloads_summary.json', 'w') as f:
        json.dump(downloads[:100], f, indent=2)

    with open(f'{output_dir}/consultants_summary.json', 'w') as f:
        json.dump(consultants[:100], f, indent=2)

    print(f"\nResults:")
    print(f"  Posts: {len(posts)}")
    print(f"  Pages: {len(pages)}")
    print(f"  Downloads: {len(downloads)}")
    print(f"  Consultants: {len(consultants)}")

    return posts, pages, downloads, consultants

if __name__ == '__main__':
    sql_file = '/Volumes/SANDISK/public_html_copy/localhost.sql'
    output_dir = '/Users/tuckerpeters/HabitsOfMind2'

    posts, pages, downloads, consultants = simple_extract(sql_file, output_dir)

    print("\nExtraction complete! Check output files for summaries.")
