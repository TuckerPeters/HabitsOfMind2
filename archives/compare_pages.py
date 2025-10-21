#!/usr/bin/env python3
"""
Compare old site pages with new site structure to identify gaps
"""
import csv
import os
import json

# Pages/routes in NEW website
NEW_SITE_PAGES = {
    'Main Pages': [
        '/', '/about', '/blog', '/events', '/certification', '/consulting',
        '/resources', '/premium-tools', '/contact', '/account', '/privacy-policy'
    ],
    'Habits Pages': [
        '/habits',
        '/habits/students', '/habits/teachers', '/habits/leaders',
        '/habits/parents', '/habits/employers'
    ],
    'Individual Habits': [
        # These exist as individual habit pages in /habits
        'persisting', 'managing-impulsivity', 'listening-with-understanding-and-empathy',
        'thinking-flexibly', 'metacognition', 'striving-for-accuracy',
        'questioning-and-posing-problems', 'applying-past-knowledge',
        'thinking-and-communicating-with-clarity-and-precision',
        'gathering-data-through-all-senses', 'creating-imagining-innovating',
        'responding-with-wonderment-and-awe', 'taking-responsible-risks',
        'finding-humor', 'thinking-interdependently',
        'remaining-open-to-continuous-learning'
    ],
    'Blog/Content': [
        # Dynamic blog posts
        '/blog/*'
    ]
}

def load_old_pages():
    """Load pages from extracted CSV"""
    pages = []
    with open('/Users/tuckerpeters/HabitsOfMind2/extracted_content/all_pages.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            pages.append(row)
    return pages

def categorize_missing(old_pages):
    """Identify potentially missing pages"""

    # Flatten new site pages for comparison
    all_new_slugs = set()
    for category, pages in NEW_SITE_PAGES.items():
        for page in pages:
            slug = page.strip('/').lower()
            all_new_slugs.add(slug)

    missing_critical = []
    missing_minor = []
    exists = []

    for page in old_pages:
        title = page['title']
        slug = page['slug'].lower()

        # Check if exists in new site
        if slug in all_new_slugs:
            exists.append(page)
            continue

        # Check for habit-specific pages (numbered)
        if slug.startswith(('1-', '2-', '3-', '4-', '5-', '6-', '7-', '8-', '9-', '10-', '11-', '12-', '13-', '14-', '15-', '16-')):
            exists.append(page)  # Individual habits exist
            continue

        # Categorize missing pages by importance
        title_lower = title.lower()

        # Critical pages
        if any(keyword in title_lower for keyword in [
            'certification', 'certified school', 'certified practitioner',
            'conference', 'event registration',
            'professional learning', 'professional development',
            'consulting', 'consultant'
        ]):
            missing_critical.append(page)

        # Potentially important
        elif any(keyword in title_lower for keyword in [
            'resource', 'assessment', 'bibliography', 'multimedia',
            'quotes', 'articles', 'research',
            'parents', 'students', 'teachers', 'leaders'
        ]):
            missing_minor.append(page)

        else:
            # Everything else (likely old/outdated)
            pass

    return missing_critical, missing_minor, exists

def generate_report(old_pages, missing_critical, missing_minor, exists):
    """Generate comparison report"""

    output_file = '/Users/tuckerpeters/HabitsOfMind2/extracted_content/pages_comparison_report.txt'

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("OLD SITE vs NEW SITE - PAGE COMPARISON REPORT\n")
        f.write("=" * 80 + "\n\n")

        f.write(f"Total Old Pages: {len(old_pages)}\n")
        f.write(f"Pages that exist in new site: {len(exists)}\n")
        f.write(f"Potentially missing (CRITICAL): {len(missing_critical)}\n")
        f.write(f"Potentially missing (MINOR): {len(missing_minor)}\n\n")

        f.write("=" * 80 + "\n")
        f.write("CRITICAL MISSING PAGES\n")
        f.write("=" * 80 + "\n")
        f.write("These pages should be reviewed for integration:\n\n")

        for page in missing_critical:
            f.write(f"  ❌ {page['title']}\n")
            f.write(f"      Old URL: /{page['slug']}\n")
            f.write(f"      Date: {page['date']}\n\n")

        f.write("\n" + "=" * 80 + "\n")
        f.write("POTENTIALLY IMPORTANT MISSING PAGES\n")
        f.write("=" * 80 + "\n")
        f.write("Review these to see if content should be migrated:\n\n")

        for page in missing_minor[:30]:  # First 30
            f.write(f"  ⚠️  {page['title']}\n")
            f.write(f"      Old URL: /{page['slug']}\n\n")

        if len(missing_minor) > 30:
            f.write(f"\n  ... and {len(missing_minor) - 30} more\n")

        f.write("\n" + "=" * 80 + "\n")
        f.write("RECOMMENDATIONS\n")
        f.write("=" * 80 + "\n\n")

        f.write("1. CERTIFICATION PAGES\n")
        f.write("   Review: Certified Schools by region, Individual Practitioner Certification\n")
        f.write("   Action: Ensure all certification info is in /certification\n\n")

        f.write("2. PROFESSIONAL LEARNING\n")
        f.write("   Review: Professional Learning Options, Training programs\n")
        f.write("   Action: Add or link from /consulting or create /professional-development\n\n")

        f.write("3. EVENT REGISTRATION\n")
        f.write("   Review: Conference registration, event forms\n")
        f.write("   Action: Ensure /events has current event registration info\n\n")

        f.write("4. RESOURCES\n")
        f.write("   Review: Assessments, Multimedia Examples, Bibliography\n")
        f.write("   Action: Verify all exist in /resources or add missing ones\n\n")

        f.write("5. CONSULTANT PROFILES\n")
        f.write("   Review: Individual consultant pages\n")
        f.write("   Action: Already have in /about - verify completeness\n\n")

    print(f"\n✓ Comparison report saved to: {output_file}")

    # Also create JSON for programmatic access
    comparison_data = {
        'critical_missing': [{'title': p['title'], 'slug': p['slug'], 'date': p['date']} for p in missing_critical],
        'minor_missing': [{'title': p['title'], 'slug': p['slug']} for p in missing_minor[:50]],
        'total_old': len(old_pages),
        'exists_in_new': len(exists),
        'critical_count': len(missing_critical),
        'minor_count': len(missing_minor)
    }

    with open('/Users/tuckerpeters/HabitsOfMind2/extracted_content/pages_comparison.json', 'w', encoding='utf-8') as f:
        json.dump(comparison_data, f, indent=2)

    return output_file

if __name__ == '__main__':
    print("Loading old site pages...")
    old_pages = load_old_pages()

    print("Comparing with new site structure...")
    missing_critical, missing_minor, exists = categorize_missing(old_pages)

    print(f"\nAnalysis Complete:")
    print(f"  ✓ Pages in new site: {len(exists)}")
    print(f"  ❌ Critical missing: {len(missing_critical)}")
    print(f"  ⚠️  Minor missing: {len(missing_minor)}")

    report_file = generate_report(old_pages, missing_critical, missing_minor, exists)

    print(f"\n✓ Full report available: {report_file}")
