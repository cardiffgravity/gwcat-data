#!/usr/bin/env python3
"""
Remove all events starting with "GW" from the JSON catalog.

This script processes a gravitational wave catalog JSON file and removes
all entries from both the "data" and "links" sections where the event name
(key) begins with "GW".

Usage:
    python remove_gw_events.py [input_file]

Arguments:
    input_file: Path to the input JSON file (default: data/gwosc_gracedb.json)

Output:
    Creates a new file with suffix '_no_gw.json'
"""

import json
import sys
from pathlib import Path


def remove_gw_events(json_content):
    """
    Remove all events starting with "GW" from the JSON content.
    
    Args:
        json_content: Dictionary containing the JSON data
        
    Returns:
        tuple: (modified_content, removed_from_data, removed_from_links, removed_events)
    """
    modified_content = json_content.copy()
    removed_events = []
    removed_from_data = 0
    removed_from_links = 0
    
    # Process data section
    if "data" in modified_content:
        data_keys_to_remove = [
            key for key in modified_content["data"].keys()
            if key.startswith("GW")
        ]
        
        for key in data_keys_to_remove:
            del modified_content["data"][key]
            removed_from_data += 1
            if key not in removed_events:
                removed_events.append(key)
    
    # Process links section
    if "links" in modified_content:
        links_keys_to_remove = [
            key for key in modified_content["links"].keys()
            if key.startswith("GW")
        ]
        
        for key in links_keys_to_remove:
            del modified_content["links"][key]
            removed_from_links += 1
            if key not in removed_events:
                removed_events.append(key)
    
    return modified_content, removed_from_data, removed_from_links, removed_events


def main():
    """Main function to process the JSON file."""
    # Get input file from command line or use default
    if len(sys.argv) > 1:
        input_file = Path(sys.argv[1])
    else:
        input_file = Path("data/gwosc_gracedb.json")
    
    if not input_file.exists():
        print(f"Error: Input file '{input_file}' not found.")
        sys.exit(1)
    
    # Create output filename
    output_file = input_file.parent / f"{input_file.stem}_no_gw.json"
    
    print(f"Reading from: {input_file}")
    
    # Load the JSON file
    try:
        with open(input_file, 'r') as f:
            json_content = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Failed to parse JSON file: {e}")
        sys.exit(1)
    
    # Process the content
    modified_content, removed_from_data, removed_from_links, removed_events = remove_gw_events(json_content)
    
    # Save the modified content
    with open(output_file, 'w') as f:
        json.dump(modified_content, f, indent=4)
    
    # Print summary
    print(f"\nRemoval complete!")
    print(f"Removed {removed_from_data} events from 'data' section")
    print(f"Removed {removed_from_links} events from 'links' section")
    print(f"Total unique events removed: {len(removed_events)}")
    
    if removed_events:
        print(f"\nRemoved events (showing first 20):")
        for event in sorted(removed_events)[:20]:
            print(f"  - {event}")
        if len(removed_events) > 20:
            print(f"  ... and {len(removed_events) - 20} more")
    
    print(f"\nOutput saved to: {output_file}")


if __name__ == "__main__":
    main()
