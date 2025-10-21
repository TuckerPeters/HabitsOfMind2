#!/usr/bin/env python3
"""
Scraper for certified individual practitioners from Habits of Mind Institute website
"""

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

def scrape_certified_practitioners():
    url = "https://www.habitsofmindinstitute.org/certification/certified-individual-practitioners/"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        practitioners = []

        # Look for practitioner listings - they seem to be in a specific format
        # Try different selectors to find the practitioner data

        # Method 1: Look for contact information patterns
        emails = soup.find_all(string=lambda text: text and '@' in text and '.' in text)

        # Method 2: Look for name/email pairs in text content
        text_content = soup.get_text()
        lines = [line.strip() for line in text_content.split('\n') if line.strip()]

        current_region = None
        current_practitioner = {}

        for line in lines:
            # Check if this is a region header
            if any(region in line for region in ['Africa', 'Asia', 'Caribbean', 'Central America', 'Europe', 'North America', 'Oceania', 'South America']):
                current_region = line.strip()
                continue

            # Check if line contains an email
            if '@' in line and '.' in line and 'Email:' not in line:
                # This might be a practitioner name followed by location
                parts = line.split('(')
                if len(parts) >= 2:
                    name = parts[0].strip()
                    location = parts[1].replace(')', '').strip()
                    current_practitioner = {
                        'name': name,
                        'location': location,
                        'region': current_region,
                        'email': None
                    }
            elif 'Email:' in line or ('@' in line and current_practitioner and not current_practitioner.get('email')):
                # Extract email
                email = line.replace('Email:', '').strip()
                if '@' in email:
                    current_practitioner['email'] = email
                    practitioners.append(current_practitioner.copy())
                    current_practitioner = {}

        # Alternative method: Find all email addresses and try to associate with names
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        import re

        found_emails = re.findall(email_pattern, text_content)

        # Try to find structured data
        contact_sections = soup.find_all('div', class_=['contact', 'practitioner', 'member'])

        if not practitioners and found_emails:
            # Fallback: create basic entries from found emails
            for i, email in enumerate(found_emails[:20]):  # Limit to first 20 to avoid spam
                practitioners.append({
                    'name': f'Practitioner {i+1}',
                    'email': email,
                    'region': 'Global',
                    'location': 'Various'
                })

        return {
            'scraped_at': datetime.now().isoformat(),
            'source_url': url,
            'total_practitioners': len(practitioners),
            'practitioners': practitioners,
            'emails_found': found_emails[:20]  # For debugging
        }

    except Exception as e:
        print(f"Error scraping practitioners: {e}")
        return {
            'error': str(e),
            'scraped_at': datetime.now().isoformat(),
            'practitioners': []
        }

if __name__ == '__main__':
    print("Scraping certified practitioners...")
    data = scrape_certified_practitioners()

    with open('certified_practitioners.json', 'w') as f:
        json.dump(data, f, indent=2)

    print(f"Found {data['total_practitioners']} practitioners")
    print("Data saved to certified_practitioners.json")

    if data['practitioners']:
        print("\nSample practitioners:")
        for p in data['practitioners'][:5]:
            print(f"- {p['name']} ({p['location']}) - {p['email']}")