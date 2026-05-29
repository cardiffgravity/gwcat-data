#!/usr/bin/env python3
"""
Script to simplify 'files' structure in skymap entries.
Converts the 'files' dict to a list of keys for entries with type:
- "skymaps-plot"
- "skymaps-plain"  
- "skymaps-thumb"

Example:
    {"moll": {"file": "...", "text": "..."}, "moll_pretty": {...}}
    becomes: ["moll", "moll_pretty"]
"""

import json
import sys
from pathlib import Path


def simplify_skymap_files(json_content):
    """
    Simplify files structure in skymap entries to just list of keys.
    
    Args:
        json_content: The parsed JSON content
        
    Returns:
        tuple: (modified_content, count_modified)
    """
    count_modified = 0
    
    if "links" not in json_content:
        print("Warning: 'links' key not found in JSON")
        return json_content, 0
    
    links = json_content["links"]
    target_types = ["skymaps-plot", "skymaps-plain", "skymaps-thumb"]
    
    for event_name, event_links in links.items():
        if not isinstance(event_links, list):
            continue
            
        for link in event_links:
            # Check if this entry should be modified
            if (isinstance(link, dict) and 
                link.get("type") in target_types and
                "files" in link and
                isinstance(link["files"], dict)):
                
                # Convert dict to list of keys
                old_files = link["files"]
                new_files = list(old_files.keys())
                link["files"] = new_files
                
                count_modified += 1
                print(f"  Simplified {link.get('type')} files in {event_name}: {len(new_files)} entries")
    
    return json_content, count_modified


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
    
    print(f"Processing skymap files structures...")
    
    # Simplify the skymap files structures
    modified_content, count_modified = simplify_skymap_files(json_content)
    
    print(f"\nModified {count_modified} skymap entries")
    
    if count_modified > 0:
        # Create output filename
        output_file = input_path.parent / f"{input_path.stem}_simplified_files{input_path.suffix}"
        
        print(f"Writing to {output_file}...")
        
        # Save the modified JSON
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(modified_content, f, indent=4)
        
        print(f"Done! Output saved to: {output_file}")
        print(f"\nTo replace the original file, run:")
        print(f"  mv {output_file} {input_file}")
    else:
        print("No entries found to modify.")


if __name__ == "__main__":
    main()
