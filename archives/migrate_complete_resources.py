#!/usr/bin/env python3
"""
Migrate all extracted resources to the new website structure
"""

import json
import shutil
import os
from pathlib import Path

def create_directories():
    """Create the directory structure for resources"""
    base_path = "/Users/tuckerpeters/HabitsOfMind2/frontend/static"

    # Create main categories
    categories = ['blog', 'research', 'assessments', 'multimedia', 'languages', 'conference', 'articles', 'books', 'quotes']

    for category in categories:
        category_path = os.path.join(base_path, 'resources', category)
        os.makedirs(category_path, exist_ok=True)
        print(f"Created directory: {category_path}")

def copy_file_safely(source, destination):
    """Copy a file with error handling"""
    try:
        # Create destination directory if it doesn't exist
        os.makedirs(os.path.dirname(destination), exist_ok=True)

        # Copy the file
        shutil.copy2(source, destination)
        return True
    except Exception as e:
        print(f"Error copying {source} to {destination}: {e}")
        return False

def migrate_resources():
    """Migrate all extracted resources"""

    # Create directory structure
    create_directories()

    # Load the focused resources
    with open('/Users/tuckerpeters/HabitsOfMind2/focused_archive_resources.json', 'r') as f:
        data = json.load(f)

    print("Starting resource migration...")

    # Process each resource category
    successful_copies = 0
    failed_copies = 0

    for category, category_data in data['resources'].items():
        print(f"\nProcessing {category} ({category_data['count']} files)...")

        for file_info in category_data['files']:
            source_path = file_info['filepath']

            # Create destination path
            dest_filename = file_info['filename']
            dest_path = f"/Users/tuckerpeters/HabitsOfMind2/frontend/static/resources/{category}/{dest_filename}"

            # Copy the file
            if os.path.exists(source_path):
                if copy_file_safely(source_path, dest_path):
                    successful_copies += 1
                    # Update the file info with new path
                    file_info['new_path'] = f"/resources/{category}/{dest_filename}"
                else:
                    failed_copies += 1
            else:
                print(f"Source file not found: {source_path}")
                failed_copies += 1

    print(f"\nMigration complete:")
    print(f"Successfully copied: {successful_copies} files")
    print(f"Failed copies: {failed_copies} files")

    # Create the final comprehensive resources JSON
    final_resources = {
        "metadata": {
            "title": "Comprehensive Habits of Mind Resources",
            "description": "Complete collection of resources extracted from WordPress archive",
            "source": "WordPress Archive Migration",
            "date": "2025-09-22",
            "total_blog_posts": len(data['blog_posts']),
            "total_resources": sum(cat['count'] for cat in data['resources'].values()),
            "categories": list(data['resources'].keys())
        },
        "blog_posts": data['blog_posts'],
        "resources": data['resources']
    }

    # Save the final resources file
    output_path = "/Users/tuckerpeters/HabitsOfMind2/frontend/static/comprehensive_resources.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(final_resources, f, indent=2, ensure_ascii=False)

    print(f"\nFinal resources JSON saved to: {output_path}")

    return final_resources

def create_category_summaries(resources):
    """Create individual category files for easier loading"""

    base_path = "/Users/tuckerpeters/HabitsOfMind2/frontend/static"

    # Create blog posts file
    blog_data = {
        "metadata": {
            "category": "Blog Posts",
            "count": len(resources['blog_posts']),
            "description": "Blog posts from Habits of Mind Institute"
        },
        "posts": resources['blog_posts']
    }

    with open(f"{base_path}/blog_posts.json", 'w', encoding='utf-8') as f:
        json.dump(blog_data, f, indent=2, ensure_ascii=False)

    # Create individual category files
    for category, data in resources['resources'].items():
        category_data = {
            "metadata": {
                "category": category.title(),
                "count": data['count'],
                "total_size_kb": data['total_size_kb'],
                "description": f"{category.title()} resources from Habits of Mind Institute"
            },
            "resources": data['files']
        }

        with open(f"{base_path}/resources_{category}.json", 'w', encoding='utf-8') as f:
            json.dump(category_data, f, indent=2, ensure_ascii=False)

        print(f"Created {category}.json with {data['count']} resources")

if __name__ == "__main__":
    print("=== COMPREHENSIVE RESOURCE MIGRATION ===")

    # Migrate all resources
    final_resources = migrate_resources()

    # Create category-specific files
    print("\nCreating category-specific JSON files...")
    create_category_summaries(final_resources)

    # Print summary
    print(f"\n=== MIGRATION SUMMARY ===")
    print(f"Blog Posts: {final_resources['metadata']['total_blog_posts']}")
    print(f"Resource Files: {final_resources['metadata']['total_resources']}")
    print(f"Categories: {len(final_resources['metadata']['categories'])}")

    for category in final_resources['metadata']['categories']:
        count = final_resources['resources'][category]['count']
        size_kb = final_resources['resources'][category]['total_size_kb']
        print(f"  {category.title()}: {count} files ({size_kb:.0f} KB)")

    print("\nAll resources have been migrated to the new website structure!")