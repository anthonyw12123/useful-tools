import os
import shutil
from datetime import datetime
from pathlib import Path

def import_photos(input_folder, output_folder="~/Pictures"):
    """
    Imports photos from the input folder, organizes them into year/month/day folders,
    and renames them according to the specified scheme.
    """

    for filename in os.listdir(input_folder):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.arw', '.raw')):
            filepath = os.path.join(input_folder, filename)

            # Get the date the photo was taken (from file creation date)
            creation_time = os.path.getctime(filepath)
            date_taken = datetime.fromtimestamp(creation_time)

            # Create the year/month/day folder structure
            year_folder = date_taken.strftime("%Y")
            # month_folder = date_taken.strftime("%Y-%m")
            day_folder = date_taken.strftime("%Y-%m-%d")
            output_path = os.path.expanduser(output_folder) / year_folder / f"{day_folder}"
            output_path.mkdir(parents=True, exist_ok=True)

            # Rename the file
            new_filename = date_taken.strftime("%Y-%m-%d-") + filename
            counter = 1
            while (output_path / new_filename).exists():
                new_filename = date_taken.strftime("%Y-%m-%d-") + filename.split('.')[0] + f"({counter})." + filename.split('.')[-1]
                counter += 1

            # Move and rename the file
            shutil.move(filepath, output_path / new_filename)

def import_videos(input_folder, output_folder="~/Pictures"):
    return

if __name__ == "__main__":
    driveName = ""
    input_folder = f"/Volumes/Untitled 1/DCIM/100MSDCF"  # Replace with your actual input folder path
    import_photos(input_folder)