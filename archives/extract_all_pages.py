#!/usr/bin/env python3
"""
Extract ALL page titles from database and categorize them
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
        self.convert_charrefs = True
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

def parse_wp_record(line):
    """Parse a single WordPress page record"""
    try:
        # Extract fields - focusing on title and slug
        pattern = r'\((\d+),\s*\d+,\s*\'([^\']*)\',\s*\'([^\']*)\',\s*\'((?:[^\']|\\\')*)\',\s*\'((?:[^\']|\\\')*)\''

        match = re.search(pattern, line, re.DOTALL)
        if not match:
            return None

        post_id, date, date_gmt, content_start, title = match.groups()

        # Clean up title
        title = title.replace("\\'", "'").replace("\\\"", '"')
        title = strip_tags(title).strip()

        # Extract slug
        slug_match = re.search(r"'([a-z0-9-]+)',\s*'',\s*'',\s*'[^']*',\s*'[^']*',\s*'',\s*\d+,\s*'[^']*',\s*\d+,\s*'page'", line)
        slug = slug_match.group(1) if slug_match else f"page-{post_id}"

        return {
            'id': post_id,
            'date': date,
            'title': title[:200],
            'slug': slug,
            'url': f'/{slug}'
        }
    except Exception as e:
        return None

def extract_all_pages():
    """Extract all page titles"""

    sql_file = '/Volumes/SANDISK/public_html_copy/localhost.sql'
    pages = []

    print("Extracting all page titles from database...")

    with open(sql_file, 'r', encoding='utf-8', errors='ignore') as f:
        for i, line in enumerate(f):
            if "'publish'" not in line or "'page'" not in line:
                continue

            if len(line) > 100:
                record = parse_wp_record(line)
                if record and record['title'] and record not in pages:
                    pages.append(record)
                    if len(pages) % 50 == 0:
                        print(f"Found {len(pages)} pages...")

            if i % 500000 == 0 and i > 0:
                print(f"Scanned {i:,} lines...")

    return pages

def categorize_pages(pages):
    """Categorize pages by type"""

    categories = {
        'habits': [],
        'certification': [],
        'events': [],
        'consulting': [],
        'resources': [],
        'about': [],
        'other': []
    }

    for page in pages:
        title_lower = page['title'].lower()
        slug_lower = page['slug'].lower()

        # Categorize by keywords
        if any(habit in title_lower or habit in slug_lower for habit in ['persisting', 'impulsivity', 'listening', 'flexibly', 'metacognition', 'accuracy', 'questioning', 'knowledge', 'clarity', 'data', 'imagining', 'wonderment', 'risks', 'humor', 'interdependently', 'learning']):
            categories['habits'].append(page)
        elif 'certif' in title_lower or 'certif' in slug_lower:
            categories['certification'].append(page)
        elif 'event' in title_lower or 'workshop' in title_lower or 'conference' in title_lower:
            categories['events'].append(page)
        elif 'consult' in title_lower or 'consult' in slug_lower:
            categories['consulting'].append(page)
        elif 'resource' in title_lower or 'download' in title_lower or 'book' in title_lower:
            categories['resources'].append(page)
        elif 'about' in title_lower or 'team' in title_lower or 'contact' in title_lower:
            categories['about'].append(page)
        else:
            categories['other'].append(page)

    return categories

def save_results(pages, categories):
    """Save results to files"""

    output_dir = '/Users/tuckerpeters/HabitsOfMind2/extracted_content'

    # Save all pages as CSV
    with open(f'{output_dir}/all_pages.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['id', 'date', 'title', 'slug', 'url'])
        writer.writeheader()
        writer.writerows(pages)

    # Save categorized pages
    with open(f'{output_dir}/pages_categorized.json', 'w', encoding='utf-8') as f:
        json.dump(categories, f, indent=2, ensure_ascii=False)

    # Create summary report
    with open(f'{output_dir}/pages_summary.txt', 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("PAGE EXTRACTION SUMMARY\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Total Pages Found: {len(pages)}\n\n")

        for category, items in categories.items():
            f.write(f"\n{category.upper()} ({len(items)} pages)\n")
            f.write("-" * 80 + "\n")
            for item in items[:20]:  # First 20 in each category
                f.write(f"  - {item['title']}\n")
            if len(items) > 20:
                f.write(f"  ... and {len(items) - 20} more\n")

    print(f"\n✓ Saved results to {output_dir}/")
    print(f"  - all_pages.csv ({len(pages)} pages)")
    print(f"  - pages_categorized.json")
    print(f"  - pages_summary.txt")

if __name__ == '__main__':
    pages = extract_all_pages()

    print(f"\n{'=' * 80}")
    print(f"Total Pages Found: {len(pages)}")
    print(f"{'=' * 80}\n")

    categories = categorize_pages(pages)

    print("\nCategorization:")
    for category, items in categories.items():
        print(f"  {category.capitalize()}: {len(items)} pages")

    save_results(pages, categories)

    print("\n✓ Page extraction complete!")
