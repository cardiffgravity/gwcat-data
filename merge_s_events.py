#!/usr/bin/env python3
"""
Script to merge events starting with 'S' from gwosc_gracedb_inc-gracedb.json
into gwosc_gracedb.json
"""

import json
from datetime import datetime
from pathlib import Path

def load_json(filepath):
    """Load JSON file"""
    with open(filepath, 'r') as f:
        return json.load(f)

def save_json(data, filepath, backup=True):
    """Save JSON file with optional backup"""
    if backup and Path(filepath).exists():
        backup_path = f"{filepath}.backup"
        print(f"Creating backup: {backup_path}")
        Path(filepath).rename(backup_path)
    
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4)
    print(f"Saved: {filepath}")

def merge_s_events(inc_file, main_file, output_file=None):
    """
    Merge events starting with 'S' from incremental file into main file
    
    Args:
        inc_file: Path to gwosc_gracedb_inc-gracedb.json
        main_file: Path to gwosc_gracedb.json
        output_file: Optional output path (defaults to updating main_file)
    """
    print(f"Loading incremental file: {inc_file}")
    inc_data = load_json(inc_file)
    
    print(f"Loading main file: {main_file}")
    main_data = load_json(main_file)
    
    # Extract S-events from data section
    s_events_data = {}
    if 'data' in inc_data:
        for event_name, event_data in inc_data['data'].items():
            if event_name.startswith('S'):
                s_events_data[event_name] = event_data
    
    print(f"\nFound {len(s_events_data)} S-events in incremental file data section")
    
    # Extract S-events from links section (if any)
    s_events_links = {}
    if 'links' in inc_data:
        for event_name, event_links in inc_data['links'].items():
            if event_name.startswith('S'):
                s_events_links[event_name] = event_links
    
    print(f"Found {len(s_events_links)} S-events in incremental file links section")
    
    # Check for existing events
    existing_data = []
    new_data = []
    
    if 'data' not in main_data:
        main_data['data'] = {}
    
    for event_name, event_data in s_events_data.items():
        if event_name in main_data['data']:
            existing_data.append(event_name)
        else:
            main_data['data'][event_name] = event_data
            new_data.append(event_name)
    
    print(f"\nData section:")
    print(f"  - Already existing: {len(existing_data)}")
    print(f"  - Newly added: {len(new_data)}")
    
    if existing_data:
        print(f"  - Existing events: {', '.join(sorted(existing_data)[:5])}{'...' if len(existing_data) > 5 else ''}")
    if new_data:
        print(f"  - New events: {', '.join(sorted(new_data)[:10])}{'...' if len(new_data) > 10 else ''}")
    
    # Merge links section
    existing_links = []
    new_links = []
    
    if 'links' not in main_data:
        main_data['links'] = {}
    
    for event_name, event_links in s_events_links.items():
        if event_name in main_data['links']:
            existing_links.append(event_name)
        else:
            main_data['links'][event_name] = event_links
            new_links.append(event_name)
    
    print(f"\nLinks section:")
    print(f"  - Already existing: {len(existing_links)}")
    print(f"  - Newly added: {len(new_links)}")
    
    if new_links:
        print(f"  - New links: {', '.join(sorted(new_links)[:10])}{'...' if len(new_links) > 10 else ''}")
    
    # Update metadata
    if 'meta' in main_data:
        main_data['meta']['created'] = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]
    
    # Save result
    output_path = output_file if output_file else main_file
    save_json(main_data, output_path, backup=True)
    
    print(f"\n✓ Merge complete!")
    print(f"  Total S-events in data section: {len([k for k in main_data['data'].keys() if k.startswith('S')])}")
    print(f"  Total S-events in links section: {len([k for k in main_data['links'].keys() if k.startswith('S')])}")

if __name__ == '__main__':
    # File paths
    data_dir = Path(__file__).parent / 'data'
    inc_file = data_dir / 'gwosc_gracedb_inc-gracedb.json'
    main_file = data_dir / 'gwosc_gracedb.json'
    output_file = data_dir / 'gwosc_gracedb_new-inc-gracedb.json'
    
    # Verify files exist
    if not inc_file.exists():
        print(f"Error: Incremental file not found: {inc_file}")
        exit(1)
    
    if not main_file.exists():
        print(f"Error: Main file not found: {main_file}")
        exit(1)
    
    # Run merge
    merge_s_events(inc_file, main_file,output_file=output_file)
