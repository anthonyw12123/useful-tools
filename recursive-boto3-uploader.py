import os
import botocore.exceptions
import boto3
import numpy as np
import time
import sys
from pathlib import Path
import re

def validate_time():
  current_time = time.localtime()
  hour = current_time.tm_hour
  # Check if it's 8 AM
  if hour >= 8 and hour <= 17:
    print("It's during normal work hours. Exiting.")
    sys.exit()

def passes_whitelist(path):
  if os.path.splitext(path)[1].lower() not in (".arw", ".jpg", ".rw2", ".mp4", ".dng", ".heic"): #png, mov omitted
    return False
  return True

def passes_blacklist(path):
  if "screen" in path.lower():
    return False
  if(".ds_store" in path.lower()):
    return False
  if os.path.splitext(path)[1].lower() in (".rsls", ".rslv", ".rslc"):
    return False
  return True

def is_valid_path(file):
  if not os.path.isfile(file):
    return False
  return passes_whitelist(file) and passes_blacklist(file)

def is_valid_s3_path(s3_client, local_file, s3_key, log):
  try:
    s3_client.head_object(Bucket=bucket_name, Key=s3_key)
    print(f"{local_file} already exists in S3, skipping upload.\n")
    log.write(f"{local_file}\n")
    return False
  except botocore.exceptions.ClientError as e:
    if e.response['Error']['Code'] == "404":
      return True
  return False

def upload_file(s3_client, bucket_name, local_file, s3_key, log, max_retries=2):
  if not is_valid_s3_path(s3_client, local_file, s3_key, log):
    return True
  for attempt in range(max_retries + 1):
    try:
      s3_client.upload_file(
        local_file, 
        bucket_name, 
        s3_key, 
        ExtraArgs={'Metadata': {'uploadedBy': 'boto3'}, 'StorageClass': 'INTELLIGENT_TIERING'})
      log.write(f"{local_file}\n")
      return True
    except botocore.exceptions.ClientError as e:
      if attempt == max_retries:
        print(f"Error uploading {local_file} to S3 after {max_retries+1} attempts: {e}")
        return False
      else:
        print(f"Attempt {attempt+1}/{max_retries+1}: Error uploading {local_file} to S3. Retrying...")

def upload_directory(s3_client, bucket_name, local_dir, s3_prefix=""):
  log_directory = os.path.join(os.path.expanduser(local_dir), os.pardir)
  local_dirname = os.path.basename(os.path.expanduser(local_dir))
  log_file_path = os.path.join(log_directory, f"upload_log_{local_dirname}.txt")

  processed_files = set()
  if os.path.exists(log_file_path):
    with open(log_file_path, "r") as log_file:
      processed_files = {line.strip() for line in log_file}

  all_files = set()
  for root, _, files in os.walk(os.path.expanduser(local_dir)):
     for file in files:
        all_files.add(os.path.join(root, file))
  
  pending_files = all_files.difference(processed_files)

  with open(log_file_path, "a") as f:
    print("beginning run")
    s3_path = os.path.join(s3_prefix, local_dirname)
    expanded_dir = os.path.expanduser(local_dir)
    relative_path_start = str.index(expanded_dir,local_dirname)
    
    for file_path in pending_files:
      validate_time()
      if not is_valid_path(file_path):
          print(f"skipping path {file_path}")
          continue
      if file_path in processed_files:
          print(f"skipping {file_path}")
          continue
      s3_path = s3_path = os.path.join(root[relative_path_start:], file)
      if os.path.basename(root).startswith("_"):
          print(f"skipping file {root} - directory is to be skipped")
          continue
      print(f"uploading {file_path}...", end="")
      upload_file(s3_client, bucket_name, file_path, s3_path, f)
      print("successfully")
      f.flush()

if __name__ == "__main__":
  # Configure AWS credentials (e.g., environment variables, boto3 config)
  s3_client = boto3.client("s3")
  bucket_name = "woody-photo-archive"
  s3_prefix = ""
  base_directory = os.path.expanduser("/Volumes/Lightroom")

  folders = sorted(filter(lambda x: os.path.isdir(os.path.join(base_directory, x)) and re.match(r"^\d{4}$", x),
                        os.listdir(base_directory) ) , reverse=True)

  for item in folders:
        year_folder_path = os.path.join(base_directory, item)
        try:
            print(f"Processing year folder: {year_folder_path}")
            upload_directory(s3_client, bucket_name, year_folder_path, s3_prefix)
        except Exception as e:
            print(f"Error processing year folder {year_folder_path}: {e}")
  print(f"Upload completed.")
