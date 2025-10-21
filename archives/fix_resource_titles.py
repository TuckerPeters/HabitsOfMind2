#!/usr/bin/env python3
"""
Fix truncated and odd resource titles in comprehensive_resources.json
"""
import json
import re

# Load the resources file
with open('/Users/tuckerpeters/HabitsOfMind2/frontend/static/comprehensive_resources.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Title fixes mapping
TITLE_FIXES = {
    'The_Impact_of_Habits_of_Mind_HoM_based_S.doc': 'The Impact of Habits of Mind - Research Study',
    'The_Impact_of_Habits_of_Mind_HoM_based_S': 'The Impact of Habits of Mind - Research Study',
}

def clean_filename_to_title(filename):
    """Convert filename to readable title"""
    # Remove extension
    title = re.sub(r'\.(doc|docx|pdf|png|jpg)$', '', filename, flags=re.IGNORECASE)

    # Replace underscores and hyphens with spaces
    title = title.replace('_', ' ').replace('-', ' ')

    # Remove dimension suffixes like "500 x 500", "128x72"
    title = re.sub(r'\s*\d+\s*x\s*\d+\s*$', '', title, flags=re.IGNORECASE)

    # Remove size suffixes
    title = re.sub(r'\s*\d+x\d+\s*$', '', title)

    # Title case (but preserve acronyms)
    words = title.split()
    title = ' '.join(word if word.isupper() and len(word) > 1 else word.capitalize() for word in words)

    return title.strip()

fixed_count = 0

# Process articles
if 'articles' in data:
    for article in data['articles']:
        filename = article.get('filename', '')

        # Apply specific fixes
        if filename in TITLE_FIXES:
            article['title'] = TITLE_FIXES[filename]
            fixed_count += 1
            print(f"✓ Fixed: {filename} → {article['title']}")

        # If no title exists, generate from filename
        elif 'title' not in article or not article['title'] or article['title'] == filename:
            article['title'] = clean_filename_to_title(filename)
            fixed_count += 1
            print(f"✓ Generated: {filename} → {article['title']}")

# Process research items
if 'research' in data:
    for item in data['research']:
        filename = item.get('filename', '')

        # Apply specific fixes
        if filename in TITLE_FIXES:
            item['title'] = TITLE_FIXES[filename]
            fixed_count += 1
            print(f"✓ Fixed: {filename} → {item['title']}")

        # If no title exists, generate from filename
        elif 'title' not in item or not item['title'] or item['title'] == filename:
            item['title'] = clean_filename_to_title(filename)
            fixed_count += 1
            print(f"✓ Generated: {filename} → {item['title']}")

# Save the updated file
with open('/Users/tuckerpeters/HabitsOfMind2/frontend/static/comprehensive_resources.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"\n✅ Fixed {fixed_count} resource titles")
print(f"✅ Updated: /frontend/static/comprehensive_resources.json")
