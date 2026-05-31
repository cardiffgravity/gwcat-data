#!/usr/bin/env python3
"""
Check PNG files in data/png directory against AWS and upload missing files.

Usage:
    python check_aws_pngs.py                          # Check all files
    python check_aws_pngs.py --event GW150914         # Check specific event
    python check_aws_pngs.py --moll-only              # Check only _moll files
    python check_aws_pngs.py --upload                 # Actually upload missing files
    python check_aws_pngs.py --event GW150914 --moll-only --upload
"""

import os
import argparse
import requests
from pathlib import Path
import subprocess
import sys

# AWS configuration
AWS_BASE_URL = "https://gwcat-data.s3.eu-north-1.amazonaws.com/png/"
AWS_BUCKET = "gwcat-data"  # Update with your actual bucket name
AWS_PREFIX = "png/"

# Local configuration
LOCAL_PNG_DIR = "data/png"


def check_file_exists_on_aws(filename, verbose=False):
    """Check if a file exists on AWS by attempting to download it.
    
    Args:
        filename: Name of the file to check
        verbose: Print detailed output
        
    Returns:
        bool: True if file exists (200), False if not found (404)
    """
    url = AWS_BASE_URL + filename
    try:
        response = requests.head(url, timeout=10)
        if response.status_code == 200:
            if verbose:
                print(f"  ✓ Exists: {filename}")
            return True
        elif response.status_code == 404:
            if verbose:
                print(f"  ✗ Missing: {filename}")
            return False
        else:
            print(f"  ? Unknown status {response.status_code}: {filename}")
            return False
    except requests.RequestException as e:
        print(f"  ! Error checking {filename}: {e}")
        return False


def upload_file_to_aws(local_path, filename, dry_run=True):
    """Upload a file to AWS S3.
    
    Args:
        local_path: Path to local file
        filename: Name of file (for S3 key)
        dry_run: If True, only print what would be uploaded
        
    Returns:
        bool: True if upload successful (or would be), False otherwise
    """
    s3_key = AWS_PREFIX + filename
    
    if dry_run:
        print(f"  [DRY RUN] Would upload: {local_path} -> s3://{AWS_BUCKET}/{s3_key}")
        return True
    
    try:
        # Try using AWS CLI (more reliable than boto3 for simple uploads)
        cmd = [
            "aws", "s3", "cp",
            local_path,
            f"s3://{AWS_BUCKET}/{s3_key}"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"  ✓ Uploaded: {filename}")
            return True
        else:
            print(f"  ✗ Upload failed: {filename}")
            print(f"    Error: {result.stderr}")
            return False
            
    except FileNotFoundError:
        print(f"  ! AWS CLI not found. Install it or use --list-only mode")
        return False
    except Exception as e:
        print(f"  ! Error uploading {filename}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Check PNG files against AWS and upload missing ones"
    )
    parser.add_argument(
        "--event",
        help="Filter by event name (e.g., GW150914)",
        default=None
    )
    parser.add_argument(
        "--moll-only",
        action="store_true",
        help="Only check _moll.png files"
    )
    parser.add_argument(
        "--thumb-only",
        action="store_true",
        help="Only check thumbnail files"
    )
    parser.add_argument(
        "--upload",
        action="store_true",
        help="Actually upload missing files (default: dry run)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Print detailed output"
    )
    parser.add_argument(
        "--list-only",
        action="store_true",
        help="Only list missing files, don't attempt upload"
    )
    
    args = parser.parse_args()
    
    # Check if local directory exists
    if not os.path.exists(LOCAL_PNG_DIR):
        print(f"Error: Directory {LOCAL_PNG_DIR} not found")
        sys.exit(1)
    
    # Get list of PNG files
    png_files = []
    for filename in sorted(os.listdir(LOCAL_PNG_DIR)):
        if not filename.endswith('.png'):
            continue
            
        # Filter by event if specified
        if args.event and not filename.startswith(args.event):
            continue
            
        # Filter by _moll if specified
        if args.moll_only and '_moll.' not in filename:
            continue
            
        # Filter by thumbnail if specified
        if args.thumb_only and '.thumb.png' not in filename:
            continue
            
        png_files.append(filename)
    
    if not png_files:
        print("No PNG files found matching criteria")
        sys.exit(0)
    
    print(f"Checking {len(png_files)} files...")
    if args.event:
        print(f"  Event filter: {args.event}")
    if args.moll_only:
        print(f"  Type filter: _moll only")
    print()
    
    # Check each file
    missing_files = []
    existing_files = []
    
    for filename in png_files:
        if check_file_exists_on_aws(filename, verbose=args.verbose):
            existing_files.append(filename)
        else:
            missing_files.append(filename)
    
    # Print summary
    print()
    print("=" * 60)
    print(f"Summary:")
    print(f"  Total checked: {len(png_files)}")
    print(f"  Existing on AWS: {len(existing_files)}")
    print(f"  Missing from AWS: {len(missing_files)}")
    print("=" * 60)
    
    if missing_files:
        print()
        print("Missing files:")
        for filename in missing_files:
            print(f"  - {filename}")
        
        # Upload or save list
        if args.list_only:
            # Save to file
            list_file = "missing_pngs.txt"
            with open(list_file, 'w') as f:
                for filename in missing_files:
                    local_path = os.path.join(LOCAL_PNG_DIR, filename)
                    f.write(f"{local_path}\n")
            print()
            print(f"Missing files list saved to: {list_file}")
        else:
            # Upload files
            print()
            if args.upload:
                print("Uploading missing files...")
            else:
                print("DRY RUN - use --upload to actually upload files")
            print()
            
            uploaded = 0
            failed = 0
            
            for filename in missing_files:
                local_path = os.path.join(LOCAL_PNG_DIR, filename)
                if upload_file_to_aws(local_path, filename, dry_run=not args.upload):
                    uploaded += 1
                else:
                    failed += 1
            
            print()
            print("Upload summary:")
            print(f"  Successful: {uploaded}")
            print(f"  Failed: {failed}")
            
            if not args.upload:
                print()
                print("This was a DRY RUN. Use --upload to actually upload files.")
    else:
        print()
        print("All files exist on AWS! ✓")
    
    # Save missing list to file for later use
    if missing_files and not args.list_only:
        list_file = "missing_pngs.txt"
        with open(list_file, 'w') as f:
            for filename in missing_files:
                f.write(f"{filename}\n")
        print()
        print(f"Missing files list saved to: {list_file}")


if __name__ == "__main__":
    main()
