#!/usr/bin/env python3
"""
AWS S3 Upload Script
Reads file list from logs/gdb_updates.log_maps_aws and uploads files to S3.
Credentials are loaded from aws_credentials.json (not in version control).
"""

import os
import json
import sys
import argparse
import boto3
from botocore.exceptions import NoCredentialsError, ClientError


def load_credentials(credentials_file='aws_credentials.json'):
    """Load AWS credentials from a JSON file."""
    if not os.path.exists(credentials_file):
        print(f"Error: Credentials file '{credentials_file}' not found.")
        print(f"Please create {credentials_file} with the following structure:")
        print("""{
    "aws_access_key_id": "YOUR_ACCESS_KEY",
    "aws_secret_access_key": "YOUR_SECRET_KEY",
    "bucket_name": "YOUR_BUCKET_NAME",
    "region": "eu-north-1"
}""")
        sys.exit(1)
    
    try:
        with open(credentials_file, 'r') as f:
            credentials = json.load(f)
        
        required_keys = ['aws_access_key_id', 'aws_secret_access_key', 'bucket_name']
        for key in required_keys:
            if key not in credentials:
                print(f"Error: Missing required key '{key}' in credentials file.")
                sys.exit(1)
        
        # Strip whitespace from credentials
        credentials['aws_access_key_id'] = credentials['aws_access_key_id'].strip()
        credentials['aws_secret_access_key'] = credentials['aws_secret_access_key'].strip()
        credentials['bucket_name'] = credentials['bucket_name'].strip()
        
        # Validate credentials format
        if credentials['aws_access_key_id'].startswith('YOUR_') or 'YOUR_' in credentials['aws_access_key_id']:
            print("Error: Placeholder credentials detected. Please replace with actual AWS credentials.")
            sys.exit(1)
        
        if not credentials['aws_access_key_id'].startswith(('AKIA', 'ASIA')):
            print(f"Warning: AWS Access Key ID should typically start with 'AKIA' or 'ASIA'.")
            print(f"Got: {credentials['aws_access_key_id'][:8]}...")
        
        if len(credentials['aws_access_key_id']) != 20:
            print(f"Warning: AWS Access Key ID should be 20 characters. Got {len(credentials['aws_access_key_id'])} characters.")
        
        if len(credentials['aws_secret_access_key']) != 40:
            print(f"Warning: AWS Secret Access Key should be 40 characters. Got {len(credentials['aws_secret_access_key'])} characters.")
        
        return credentials
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in credentials file: {e}")
        sys.exit(1)


def read_log_file(log_file, force_upload=False):
    """Read the log file and return list of files to upload and all original lines."""
    if not os.path.exists(log_file):
        print(f"Error: Log file '{log_file}' not found.")
        sys.exit(1)
    
    files_to_upload = []
    all_lines = []
    skipped_count = 0
    
    # Determine which statuses to include
    if force_upload:
        valid_statuses = ['new', 'updated', 'uploaded']
    else:
        valid_statuses = ['new', 'updated']
    
    with open(log_file, 'r') as f:
        for line_num, line in enumerate(f, 1):
            original_line = line.rstrip('\n')  # Keep line but remove newline
            all_lines.append(original_line)
            
            line_stripped = line.strip()
            if not line_stripped:
                continue
            
            parts = line_stripped.split(',')
            if len(parts) >= 5:
                event_name = parts[0].strip()
                file_type = parts[1].strip()
                file_path = parts[2].strip()
                timestamp = parts[3].strip()
                status = parts[4].strip().lower()  # Strip and lowercase for comparison
                
                # Upload files based on status and force flag
                if status in valid_statuses:
                    files_to_upload.append({
                        'event': event_name,
                        'type': file_type,
                        'path': file_path,
                        'timestamp': timestamp,
                        'status': status,
                        'line_num': line_num - 1  # Store 0-based index for all_lines
                    })
                else:
                    skipped_count += 1
            else:
                if line_stripped:  # Only warn if non-empty
                    print(f"Warning: Skipping malformed line {line_num}: {line_stripped}")
    
    if force_upload:
        print(f"Filtered {skipped_count} file(s) (status not 'new', 'updated', or 'uploaded')")
    else:
        print(f"Filtered {skipped_count} file(s) (status not 'new' or 'updated')")
    return files_to_upload, all_lines


def upload_file_to_s3(s3_client, local_file, bucket_name, s3_key):
    """Upload a single file to S3."""
    try:
        with open(local_file, 'rb') as f:
            s3_client.upload_fileobj(f, bucket_name, s3_key)
        return True
    except FileNotFoundError:
        print(f"  Error: Local file not found: {local_file}")
        return False
    except ClientError as e:
        print(f"  Error uploading to S3: {e}")
        return False


def update_log_file(log_file, all_lines, uploaded_indices):
    """Update the log file, marking uploaded files with 'uploaded' status."""
    if not uploaded_indices:
        return
    
    updated_count = 0
    for line_idx in uploaded_indices:
        line = all_lines[line_idx]
        parts = line.split(',')
        if len(parts) >= 5:
            # Replace the last part (status) with 'uploaded'
            parts[-1] = 'uploaded'
            all_lines[line_idx] = ','.join(parts)
            updated_count += 1
    
    # Write updated content back to file
    with open(log_file, 'w') as f:
        for line in all_lines:
            f.write(line + '\n')
    
    print(f"Updated {updated_count} line(s) in log file with 'uploaded' status")


def main():
    parser = argparse.ArgumentParser(
        description='Upload files to AWS S3 based on log file'
    )
    parser.add_argument(
        '-l', '--logfile',
        dest='logfile',
        type=str,
        default='logs/gdb_updates.log_maps_aws',
        help='Log file containing list of files to upload [Default: logs/gdb_updates.log_maps_aws]'
    )
    parser.add_argument(
        '-c', '--credentials',
        dest='credentials',
        type=str,
        default='aws_credentials.json',
        help='JSON file containing AWS credentials [Default: aws_credentials.json]'
    )
    parser.add_argument(
        '-v', '--verbose',
        dest='verbose',
        action='store_true',
        default=False,
        help='Print verbose output'
    )
    parser.add_argument(
        '-n', '--dry-run',
        dest='dry_run',
        action='store_true',
        default=False,
        help='Show what would be uploaded without actually uploading'
    )
    parser.add_argument(
        '-f', '--force',
        dest='force',
        action='store_true',
        default=False,
        help='Force upload of files that were already uploaded (status="uploaded")'
    )
    
    args = parser.parse_args()
    
    # Load credentials
    print(f"Loading credentials from {args.credentials}...")
    credentials = load_credentials(args.credentials)
    
    # Read log file
    print(f"Reading log file {args.logfile}...")
    if args.force:
        print("Force mode enabled: will also upload files with 'uploaded' status")
    files_to_upload, all_lines = read_log_file(args.logfile, force_upload=args.force)
    
    if not files_to_upload:
        if args.force:
            print("No files to upload (only 'new', 'updated', or 'uploaded' files are uploaded with --force).")
        else:
            print("No files to upload (only 'new' or 'updated' files are uploaded).")
        return
    
    print(f"Found {len(files_to_upload)} file(s) to upload.")
    
    if args.dry_run:
        print("\n=== DRY RUN MODE - No files will be uploaded ===\n")
    
    # Initialize S3 client
    try:
        s3 = boto3.client(
            's3',
            aws_access_key_id=credentials['aws_access_key_id'],
            aws_secret_access_key=credentials['aws_secret_access_key'],
            region_name=credentials.get('region', 'eu-north-1')
        )
    except Exception as e:
        print(f"Error initializing S3 client: {e}")
        sys.exit(1)
    
    # Upload files
    success_count = 0
    error_count = 0
    uploaded_indices = []  # Track which lines to update
    
    for i, file_info in enumerate(files_to_upload, 1):
        local_path = file_info['path']
        # Remove 'data/' prefix for S3 key if present
        s3_key = local_path.replace('data/', '', 1) if local_path.startswith('data/') else local_path
        
        status_str = f"[{i}/{len(files_to_upload)}]"
        print(f"{status_str} {local_path} -> s3://{credentials['bucket_name']}/{s3_key}")
        
        if args.verbose:
            print(f"  Event: {file_info['event']}, Type: {file_info['type']}, Status: {file_info['status']}")
        
        if not args.dry_run:
            if upload_file_to_s3(s3, local_path, credentials['bucket_name'], s3_key):
                success_count += 1
                uploaded_indices.append(file_info['line_num'])
                if args.verbose:
                    print("  ✓ Upload successful")
            else:
                error_count += 1
        else:
            print("  (dry run - skipped)")
    
    # Update log file with 'uploaded' status for successful uploads
    if not args.dry_run and uploaded_indices:
        print(f"\nUpdating log file...")
        update_log_file(args.logfile, all_lines, uploaded_indices)
    
    # Summary
    print(f"\n=== Upload Summary ===")
    if not args.dry_run:
        print(f"Successful: {success_count}")
        print(f"Failed: {error_count}")
        print(f"Total: {len(files_to_upload)}")
    else:
        print(f"Would upload {len(files_to_upload)} file(s) (dry run)")


if __name__ == '__main__':
    main()