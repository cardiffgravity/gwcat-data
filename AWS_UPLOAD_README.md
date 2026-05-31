# AWS PNG Upload Scripts

Scripts to check and upload PNG skymap files to AWS S3.

## Files

- `check_aws_pngs.py` - Main script to check which files exist on AWS
- `upload_missing_pngs.sh` - Batch upload script using the generated list
- `missing_pngs.txt` - Generated list of files missing from AWS (created by check script)

## Prerequisites

```bash
# Install AWS CLI if not already installed
# For Ubuntu/Debian:
sudo apt-get install awscli

# For macOS:
brew install awscli

# Configure AWS credentials (one time setup)
aws configure
```

## Usage

### 1. Check all PNG files

```bash
python check_aws_pngs.py
```

### 2. Check files for a specific event

```bash
python check_aws_pngs.py --event GW150914
```

### 3. Check only _moll files

```bash
python check_aws_pngs.py --moll-only
```

### 4. Check _moll files for a specific event

```bash
python check_aws_pngs.py --event GW150914 --moll-only
```

### 5. Check and show what would be uploaded (dry run)

```bash
python check_aws_pngs.py --event GW150914 --moll-only
```

### 6. Actually upload missing files

```bash
python check_aws_pngs.py --event GW150914 --moll-only --upload
```

### 7. Just save list of missing files (no upload attempt)

```bash
python check_aws_pngs.py --list-only
```

### 8. Upload from saved list (alternative method)

```bash
./upload_missing_pngs.sh
```

## Examples

### Check one event's _moll files and upload if missing

```bash
python check_aws_pngs.py --event GW230529_181500 --moll-only --upload
```

### Check all files, save list, review, then upload later

```bash
# Step 1: Check and save list
python check_aws_pngs.py --list-only

# Step 2: Review missing_pngs.txt file
cat missing_pngs.txt

# Step 3: Upload using bash script
./upload_missing_pngs.sh
```

### Dry run to see what would be uploaded

```bash
python check_aws_pngs.py --event GW150914
# This shows which files are missing but doesn't upload
```

## Configuration

Edit these variables in the scripts if needed:

**check_aws_pngs.py:**
- `AWS_BASE_URL` - URL to check files (default: https://data.cardiffgravity.org/gwcat-data/png/)
- `AWS_BUCKET` - S3 bucket name
- `AWS_PREFIX` - Prefix/path in bucket (default: png/)
- `LOCAL_PNG_DIR` - Local directory (default: data/png)

**upload_missing_pngs.sh:**
- `BUCKET` - S3 bucket name
- `PREFIX` - Prefix/path in bucket

## Output Files

- `missing_pngs.txt` - List of files missing from AWS (one per line)

## Notes

- By default, the script does a **dry run** - use `--upload` to actually upload
- Files are uploaded with `--acl public-read` for public access
- The script uses `requests.head()` to check file existence (faster than full download)
- Upload uses AWS CLI for reliability
