#!/usr/bin/env python3
"""
Script to remove marginal detection events from the data section.
Removes entries where: "detType": {"best": "Marginal"}
"""

import json
import sys
from pathlib import Path


def remove_marginal_detections(json_content):
    """
    Remove marginal detection entries from the data section.
    
    Args:
        json_content: The parsed JSON content
        
    Returns:
        tuple: (modified_content, count_removed, removed_events)
    """
    count_removed = 0
    removed_events = []
    
    if "data" not in json_content:
        print("Warning: 'data' key not found in JSON")
        return json_content, 0, []
    
    data_section = json_content["data"]
    
    # Create a new dict with only non-marginal events
    filtered_data = {}
    
    for event_name, event_info in data_section.items():
        # Check if this event should be removed
        if (isinstance(event_info, dict) and 
            "detType" in event_info and
            isinstance(event_info["detType"], dict) and
            event_info["detType"].get("best") == "Marginal"):
            count_removed += 1
            removed_events.append(event_name)
            print(f"  Removing marginal event: {event_name}")
        else:
            filtered_data[event_name] = event_info
    
    # Update the data section
    json_content["data"] = filtered_data
    
    return json_content, count_removed, removed_events


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
    
    print(f"Processing data section...")
    
    # Remove the marginal detection entries
    modified_content, count_removed, removed_events = remove_marginal_detections(json_content)
    
    print(f"\nRemoved {count_removed} marginal detection events")
    
    if count_removed > 0:
        # Create output filename
        output_file = input_path.parent / f"{input_path.stem}_no_marginal{input_path.suffix}"
        
        print(f"Writing to {output_file}...")
        
        # Save the modified JSON
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(modified_content, f, indent=4)
        
        print(f"Done! Output saved to: {output_file}")
        print(f"\nRemoved events: {', '.join(removed_events)}")
        print(f"\nTo replace the original file, run:")
        print(f"  mv {output_file} {input_file}")
    else:
        print("No marginal detection events found to remove.")


if __name__ == "__main__":
    main()
