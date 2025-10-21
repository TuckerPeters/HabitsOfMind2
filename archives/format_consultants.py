#!/usr/bin/env python3
"""
Format extracted consultants for the About page
"""
import json
import re
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

# Load consultants
with open('/Users/tuckerpeters/HabitsOfMind2/extracted_content/consultants.json', 'r', encoding='utf-8') as f:
    consultants = json.load(f)

print("Found", len(consultants), "consultants\n")
print("=" * 80)
print("\nCONSULTANT PROFILES FOR ABOUT PAGE")
print("=" * 80)
print("\nAdd these to the 'leadership' array in /frontend/src/routes/about/+page.svelte")
print("(They should go AFTER the existing Art Costa, Bena Kallick, and Allison Zmuda)\n")

# Sort by name
consultants_sorted = sorted(consultants, key=lambda x: x['title'].split()[-1])

output_lines = []

for consultant in consultants_sorted:
    name = consultant['title']
    bio_html = consultant['content']
    bio_clean = strip_tags(bio_html).strip()

    # Clean up bio - remove extra whitespace
    bio_clean = re.sub(r'\s+', ' ', bio_clean)

    # Truncate if too long
    if len(bio_clean) > 300:
        bio_clean = bio_clean[:297] + '...'

    # Skip if already in leadership (Art, Bena, Allison)
    if name in ['Art Costa', 'Bena Kallick', 'Allison Zmuda']:
        continue

    # Determine role
    if 'consultant' in bio_clean.lower() or 'consulting' in bio_clean.lower():
        role = 'Consultant'
    elif 'director' in bio_clean.lower():
        role = 'Educational Director'
    elif 'teacher' in bio_clean.lower():
        role = 'Educator'
    elif 'trainer' in bio_clean.lower() or 'training' in bio_clean.lower():
        role = 'Professional Development Trainer'
    else:
        role = 'Expert Practitioner'

    output = f"""{{
    name: '{name}',
    role: '{role}',
    bio: '{bio_clean}',
    img: '/images/team/{consultant['slug']}.jpg'
}},"""

    output_lines.append(output)

    print(output)
    print()

print("\n" + "=" * 80)
print(f"\nTotal: {len(output_lines)} consultant profiles ready to add")
print("\nNOTE: You'll need to add placeholder images or actual photos at:")
print("/frontend/static/images/team/[consultant-slug].jpg")
print("\n" + "=" * 80)

# Also save to a file for easy copy-paste
with open('/Users/tuckerpeters/HabitsOfMind2/consultants_formatted.txt', 'w', encoding='utf-8') as f:
    f.write("\n".join(output_lines))

print("\n✓ Also saved to: consultants_formatted.txt")
