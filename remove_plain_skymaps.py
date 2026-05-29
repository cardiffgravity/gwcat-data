#!/usr/bin/env python3
"""
Script to remove skymap-plain entries without 'files' from the links section.
Removes entries where:
- type is "skymaps-plain" OR "skymap-plain"
- AND no "files" key exists
"""

import json
import sys
from pathlib import Path


def remove_plain_skymaps_without_files(json_content):
    """
    Remove plain skymap entries without 'files' from the links section.
    
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
            
        # Filter out entries matching the criteria
        filtered_links = []
        
        for link in event_links:
            # Check if this entry should be removed
            if (isinstance(link, dict) and 
                link.get("type") in ["skymaps-plain", "skymap-plain"] and
                "files" not in link):
                count_removed += 1
                print(f"  Removing {link.get('type')} without files from {event_name}")
            else:
                filtered_links.append(link)
        
        # Update the links for this event
        links[event_name] = filtered_links
    
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
    
    print(f"Processing links...")
    
    # Remove the plain skymap entries without files
    modified_content, count_removed = remove_plain_skymaps_without_files(json_content)
    
    print(f"\nRemoved {count_removed} plain skymap entries without 'files'")
    
    if count_removed > 0:
        # Create output filename
        output_file = input_path.parent / f"{input_path.stem}_no_plain_skymaps{input_path.suffix}"
        
        print(f"Writing to {output_file}...")
        
        # Save the modified JSON
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(modified_content, f, indent=4)
        
        print(f"Done! Output saved to: {output_file}")
        print(f"\nTo replace the original file, run:")
        print(f"  mv {output_file} {input_file}")
    else:
        print("No entries found to remove.")


if __name__ == "__main__":
    main()
