#!/usr/bin/env python3
"""
Process the most valuable resources from the WordPress archive
Focus on key categories and create a manageable dataset
"""

import json
import re
from pathlib import Path

def process_ghost_posts():
    """Extract blog posts from Ghost export with proper parsing"""
    ghost_file = "/Volumes/SANDISK/public_html_copy/wp-content/uploads/ghost-exports/wp_ghost_export.json"

    try:
        with open(ghost_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        posts = []
        if 'data' in data and 'posts' in data['data']:
            for post in data['data']['posts']:
                if post.get('status') == 'published':  # Only published posts
                    # Clean HTML content
                    content = post.get('html', '')
                    # Remove HTML tags for excerpt
                    clean_content = re.sub(r'<[^>]+>', '', content)
                    excerpt = clean_content[:300] + "..." if len(clean_content) > 300 else clean_content

                    posts.append({
                        'id': post.get('id'),
                        'title': post.get('title'),
                        'slug': post.get('slug'),
                        'excerpt': excerpt,
                        'content': content[:1000] + "..." if len(content) > 1000 else content,  # Truncate for size
                        'published_at': post.get('published_at'),
                        'updated_at': post.get('updated_at'),
                        'visibility': post.get('visibility'),
                        'url': f"https://www.habitsofmindinstitute.org/{post.get('slug', '')}/"
                    })

        # Sort by date, most recent first
        posts.sort(key=lambda x: x.get('published_at', ''), reverse=True)
        return posts[:50]  # Top 50 most recent posts

    except Exception as e:
        print(f"Error processing Ghost export: {e}")
        return []

def load_complete_archive():
    """Load the complete archive and filter key resources"""
    with open('/Users/tuckerpeters/HabitsOfMind2/complete_archive_resources.json', 'r') as f:
        data = json.load(f)

    return data

def filter_high_value_files(files, category, max_files=20):
    """Filter to the most valuable files in each category"""

    # Sort by file size (larger files likely more valuable) and recent dates
    sorted_files = sorted(files, key=lambda f: (
        f.get('year') or '2000',  # Recent files first, handle None
        -f.get('size_kb', 0)      # Larger files first
    ), reverse=True)

    # Category-specific filtering
    if category == 'assessments':
        # Prioritize rubrics and evaluation tools
        priority_files = [f for f in sorted_files if any(word in f['filename'].lower()
                         for word in ['rubric', 'evaluation', 'assessment', 'checklist'])]
        return priority_files[:max_files]

    elif category == 'research':
        # Prioritize research papers and studies
        priority_files = [f for f in sorted_files if any(word in f['filename'].lower()
                         for word in ['research', 'study', 'paper', 'thesis', 'analysis'])]
        return priority_files[:max_files]

    elif category == 'articles':
        # Prioritize articles and whitepapers
        priority_files = [f for f in sorted_files if f['format'] in ['PDF', 'DOC', 'DOCX']
                         and f.get('size_kb', 0) > 50]  # Skip very small files
        return priority_files[:max_files]

    elif category == 'languages':
        # Include all language resources
        return sorted_files[:max_files]

    elif category == 'conference':
        # Conference materials
        return sorted_files[:max_files]

    elif category == 'multimedia':
        # Images, videos, presentations
        priority_files = [f for f in sorted_files if f['format'] in ['PDF', 'PPT', 'PPTX', 'JPG', 'PNG']
                         and f.get('size_kb', 0) > 100]
        return priority_files[:max_files]

    return sorted_files[:max_files]

def create_focused_resources():
    """Create a focused, high-value resource collection"""

    print("Processing Ghost blog posts...")
    blog_posts = process_ghost_posts()
    print(f"Extracted {len(blog_posts)} blog posts")

    print("Loading complete archive...")
    archive_data = load_complete_archive()

    # Process key categories
    key_categories = ['assessments', 'research', 'articles', 'languages', 'conference', 'multimedia']

    focused_resources = {
        "extraction_info": {
            "source": "WordPress Archive - High Value Resources",
            "date": "2025-09-22",
            "focus": "Most valuable educational content from all categories"
        },
        "blog_posts": blog_posts,
        "resources": {}
    }

    total_resources = 0

    for category in key_categories:
        if category in archive_data['categories']:
            category_files = archive_data['categories'][category]['files']
            filtered_files = filter_high_value_files(category_files, category)

            if filtered_files:
                focused_resources['resources'][category] = {
                    'count': len(filtered_files),
                    'total_size_kb': sum(f['size_kb'] for f in filtered_files),
                    'files': filtered_files
                }
                total_resources += len(filtered_files)
                print(f"{category}: {len(filtered_files)} high-value files")

    focused_resources['extraction_info']['total_resources'] = total_resources

    return focused_resources

if __name__ == "__main__":
    resources = create_focused_resources()

    # Save focused resources
    output_file = "/Users/tuckerpeters/HabitsOfMind2/focused_archive_resources.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(resources, f, indent=2, ensure_ascii=False)

    print(f"\n=== FOCUSED EXTRACTION COMPLETE ===")
    print(f"Blog posts: {len(resources['blog_posts'])}")
    print(f"Resource categories: {len(resources['resources'])}")
    print(f"Total resources: {resources['extraction_info']['total_resources']}")
    print(f"Saved to: {output_file}")

    # Show summary
    for category, data in resources['resources'].items():
        print(f"  {category}: {data['count']} files ({data['total_size_kb']:.0f} KB)")