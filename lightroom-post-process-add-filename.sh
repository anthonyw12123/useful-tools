# This uses ImageMagick to add filename
# Get the input file path from the argument
input_file="$1"

# Extract the filename without extension
filename=$(basename "$input_file" .png)

# Use ImageMagick to add the filename to the image
convert "$input_file" -gravity southeast -font Arial -pointsize 20 -fill black -annotate +10+10 "$filename" "$input_file"