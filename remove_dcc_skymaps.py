#!/usr/bin/env python3
"""
Remove skymap-fits entries with dcc.ligo.org URLs from the JSON catalog.

This script processes a gravitational wave catalog JSON file and removes
entries from the links section where type="skymap-fits" and the URL 
contains "dcc.ligo.org".

Usage:
    python remove_dcc_skymaps.py [input_file]

Arguments:
    input_file: Path to the input JSON file (default: data/gwosc_gracedb.json)

Output:
    Creates a new file with suffix '_no_dcc_skymaps.json'
"""

import json
import sys
from pathlib import Path


def remove_dcc_skymaps(json_content):
    """
    Remove skymap-fits entries with dcc.ligo.org URLs from the JSON content.
    
    Args:
        json_content: Dictionary containing the JSON data
        
    Returns:
        tuple: (modified_content, removed_count, affected_events)
    """
    modified_content = json_content.copy()
    removed_count = 0
    affected_events = []
    
    # Process links section
    if "links" in modified_content:
        for event_name, links in modified_content["links"].items():
            if not isinstance(links, list):
                continue
            
            original_length = len(links)
            
            # Filter out skymap-fits entries with dcc.ligo.org URLs
            filtered_links = [
                entry for entry in links
                if not (
                    entry.get("type") == "skymap-fits" and
                    "dcc.ligo.org" in entry.get("url", "")
                )
            ]
            
            removed_from_event = original_length - len(filtered_links)
            if removed_from_event > 0:
                modified_content["links"][event_name] = filtered_links
                removed_count += removed_from_event
                affected_events.append(event_name)
    
    return modified_content, removed_count, affected_events


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
    output_file = input_file.parent / f"{input_file.stem}_no_dcc_skymaps.json"
    
    print(f"Reading from: {input_file}")
    
    # Load the JSON file
    try:
        with open(input_file, 'r') as f:
            json_content = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Failed to parse JSON file: {e}")
        sys.exit(1)
    
    # Process the content
    modified_content, removed_count, affected_events = remove_dcc_skymaps(json_content)
    
    # Save the modified content
    with open(output_file, 'w') as f:
        json.dump(modified_content, f, indent=4)
    
    # Print summary
    print(f"\nRemoval complete!")
    print(f"Removed {removed_count} skymap-fits entries with dcc.ligo.org URLs")
    print(f"Affected {len(affected_events)} events")
    
    if affected_events:
        print(f"\nAffected events:")
        for event in sorted(affected_events):
            print(f"  - {event}")
    
    print(f"\nOutput saved to: {output_file}")


if __name__ == "__main__":
    main()
