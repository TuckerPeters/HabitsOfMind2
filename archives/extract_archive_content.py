#!/usr/bin/env python3
"""
Extract all content from WordPress archive for Habits of Mind resources
"""

import os
import json
import re
from pathlib import Path
from collections import defaultdict
import mimetypes

def extract_file_metadata(filepath):
    """Extract metadata from a file path"""
    path = Path(filepath)
    name = path.name

    # Extract date from path if possible (WordPress uploads are organized by year/month)
    date_match = re.search(r'/(\d{4})/(\d{2})/', str(filepath))
    year = date_match.group(1) if date_match else None
    month = date_match.group(2) if date_match else None

    # Get file size
    try:
        size_bytes = os.path.getsize(filepath)
        size_kb = round(size_bytes / 1024, 1)
    except:
        size_kb = 0

    # Determine category based on filename patterns
    name_lower = name.lower()
    category = "uncategorized"

    if any(word in name_lower for word in ['assessment', 'rubric', 'evaluation', 'checklist']):
        category = "assessments"
    elif any(word in name_lower for word in ['research', 'study', 'thesis', 'paper', 'analysis']):
        category = "research"
    elif any(word in name_lower for word in ['poster', 'infographic', 'visual', 'chart', 'graphic']):
        category = "multimedia"
    elif any(word in name_lower for word in ['book', 'bibliography', 'reading', 'literature']):
        category = "books"
    elif any(word in name_lower for word in ['spanish', 'french', 'chinese', 'arabic', 'maori', 'portuguese']):
        category = "languages"
    elif any(word in name_lower for word in ['quote', 'saying', 'wisdom']):
        category = "quotes"
    elif any(word in name_lower for word in ['conference', 'presentation', 'workshop', 'flyer']):
        category = "conference"
    elif name_lower.endswith(('.pdf', '.doc', '.docx', '.ppt', '.pptx')):
        category = "articles"

    return {
        "filename": name,
        "filepath": str(path),
        "relative_path": filepath.replace('/Volumes/SANDISK/public_html_copy/wp-content/uploads/', ''),
        "year": year,
        "month": month,
        "category": category,
        "format": path.suffix.lower().replace('.', '').upper() if path.suffix else 'UNKNOWN',
        "size_kb": size_kb,
        "mime_type": mimetypes.guess_type(str(path))[0]
    }

def scan_uploads_directory():
    """Scan wp-content/uploads for all files"""
    uploads_path = "/Volumes/SANDISK/public_html_copy/wp-content/uploads"
    files_by_category = defaultdict(list)
    total_files = 0

    print("Scanning uploads directory...")

    # Find all document and media files
    for root, dirs, files in os.walk(uploads_path):
        for file in files:
            if file.lower().endswith(('.pdf', '.doc', '.docx', '.ppt', '.pptx', '.txt', '.rtf',
                                     '.jpg', '.jpeg', '.png', '.gif', '.mp4', '.mov', '.avi',
                                     '.xls', '.xlsx', '.csv')):
                filepath = os.path.join(root, file)
                metadata = extract_file_metadata(filepath)
                files_by_category[metadata['category']].append(metadata)
                total_files += 1

                if total_files % 50 == 0:
                    print(f"Processed {total_files} files...")

    print(f"Total files found: {total_files}")
    return files_by_category

def extract_ghost_posts():
    """Extract blog posts from Ghost export"""
    ghost_file = "/Volumes/SANDISK/public_html_copy/wp-content/uploads/ghost-exports/wp_ghost_export.json"

    if not os.path.exists(ghost_file):
        print("Ghost export file not found")
        return []

    print("Extracting Ghost export posts...")

    # Since the file is large, we'll process it in chunks
    posts = []
    try:
        with open(ghost_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Parse JSON
        data = json.loads(content)

        if 'db' in data and isinstance(data['db'], list):
            for db_entry in data['db']:
                if 'data' in db_entry and 'posts' in db_entry['data']:
                    for post in db_entry['data']['posts']:
                        if isinstance(post, dict) and 'title' in post:
                            posts.append({
                                'id': post.get('id'),
                                'title': post.get('title'),
                                'slug': post.get('slug'),
                                'content': post.get('html', ''),
                                'excerpt': post.get('custom_excerpt') or post.get('excerpt'),
                                'published_at': post.get('published_at'),
                                'created_at': post.get('created_at'),
                                'updated_at': post.get('updated_at'),
                                'status': post.get('status'),
                                'visibility': post.get('visibility'),
                                'tags': post.get('tags', []),
                                'authors': post.get('authors', [])
                            })

    except Exception as e:
        print(f"Error processing Ghost export: {e}")
        return []

    print(f"Extracted {len(posts)} blog posts from Ghost export")
    return posts

def create_comprehensive_resources():
    """Create comprehensive resources structure"""
    print("Starting comprehensive archive extraction...")

    # Scan all files
    files_by_category = scan_uploads_directory()

    # Extract blog posts
    blog_posts = extract_ghost_posts()

    # Create comprehensive structure
    resources = {
        "archive_info": {
            "source": "Complete WordPress Archive from /Volumes/SANDISK/public_html_copy",
            "extraction_date": "2025-09-22",
            "total_files": sum(len(files) for files in files_by_category.values()),
            "total_blog_posts": len(blog_posts)
        },
        "blog_posts": blog_posts[:50],  # First 50 posts for now
        "categories": {}
    }

    # Organize files by category
    for category, files in files_by_category.items():
        if files:  # Only include categories with files
            resources["categories"][category] = {
                "count": len(files),
                "total_size_kb": sum(f['size_kb'] for f in files),
                "files": files
            }

    # Print summary
    print("\n=== EXTRACTION SUMMARY ===")
    print(f"Total blog posts: {len(blog_posts)}")
    print(f"Total files: {resources['archive_info']['total_files']}")

    for category, data in resources["categories"].items():
        print(f"{category}: {data['count']} files ({data['total_size_kb']:.1f} KB)")

    return resources

if __name__ == "__main__":
    resources = create_comprehensive_resources()

    # Save to JSON file
    output_file = "/Users/tuckerpeters/HabitsOfMind2/complete_archive_resources.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(resources, f, indent=2, ensure_ascii=False)

    print(f"\nComplete archive resources saved to: {output_file}")