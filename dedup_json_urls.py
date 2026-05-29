#!/usr/bin/env python3
"""
Script to remove duplicate json-url entries, keeping only the highest version.
For entries with type "json-url", extracts version from URL (e.g., /v3, /v4)
and keeps only the entry with the highest version number.
"""

import json
import sys
import re
from pathlib import Path


def extract_version(url):
    """
    Extract version number from URL ending in /vN.
    Returns the version number as an integer, or 0 if not found.
    """
    match = re.search(r'/v(\d+)$', url)
    if match:
        return int(match.group(1))
    return 0


def remove_duplicate_json_urls(json_content):
    """
    Remove duplicate json-url entries, keeping only the highest version.
    
    Args:
        json_content: The parsed JSON content
        
    Returns:
        tuple: (modified_content, count_removed)
    """
    count_removed = 0
    
    if "links" not in json_content:
        print("Warning: 'links' key not found in JSON")
        return json_content, 0
    
    links = json_content["links"]
    
    for event_name, event_links in links.items():
        if not isinstance(event_links, list):
            continue
        
        # Find all json-url entries
        json_url_entries = []
        other_entries = []
        
        for link in event_links:
            if isinstance(link, dict) and link.get("type") == "json-url":
                json_url_entries.append(link)
            else:
                other_entries.append(link)
        
        # If there are multiple json-url entries, keep only the highest version
        if len(json_url_entries) > 1:
            # Find the entry with the highest version
            max_version = -1
            max_entry = None
            
            for entry in json_url_entries:
                url = entry.get("url", "")
                version = extract_version(url)
                if version > max_version:
                    max_version = version
                    max_entry = entry
            
            # Keep only the highest version entry
            if max_entry:
                removed_count = len(json_url_entries) - 1
                count_removed += removed_count
                print(f"  Keeping v{max_version} json-url in {event_name}, removed {removed_count} duplicate(s)")
                other_entries.append(max_entry)
            else:
                # If no version found, keep all
                other_entries.extend(json_url_entries)
        else:
            # Keep the single entry or none
            other_entries.extend(json_url_entries)
        
        # Update the links for this event
        links[event_name] = other_entries
    
    return json_content, count_removed


def main():
    # Default file path
    input_file = "data/gwosc_gracedb.json"
    
    # Allow command-line argument to override
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    
    input_path = Path(input_file)
    
    if not input_path.exists():
        print(f"Error: File not found: {input_file}")
        sys.exit(1)
    
    print(f"Reading {input_file}...")
    
    # Load the JSON file
    with open(input_path, 'r', encoding='utf-8') as f:
        json_content = json.load(f)
    
    print(f"Processing json-url duplicates...")
    
    # Remove duplicate json-url entries
    modified_content, count_removed = remove_duplicate_json_urls(json_content)
    
    print(f"\nRemoved {count_removed} duplicate json-url entries")
    
    if count_removed > 0:
        # Create output filename
        output_file = input_path.parent / f"{input_path.stem}_dedup_json_urls{input_path.suffix}"
        
        print(f"Writing to {output_file}...")
        
        # Save the modified JSON
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(modified_content, f, indent=4)
        
        print(f"Done! Output saved to: {output_file}")
        print(f"\nTo replace the original file, run:")
        print(f"  mv {output_file} {input_file}")
    else:
        print("No duplicate json-url entries found to remove.")


if __name__ == "__main__":
    main()
