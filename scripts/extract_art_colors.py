from PIL import Image
import numpy as np
from sklearn.cluster import KMeans
import json
import os

def is_vivid_color(rgb, saturation_threshold=30, brightness_range=(40, 240)):
    """Check if a color is vivid (not white, black, or gray)"""
    r, g, b = rgb
    
    # Calculate saturation (difference between max and min RGB values)
    max_val = max(r, g, b)
    min_val = min(r, g, b)
    saturation = max_val - min_val
    
    # Calculate brightness (average of RGB)
    brightness = (r + g + b) / 3
    
    # Filter out low saturation (grays) and extreme brightness (white/black)
    if saturation < saturation_threshold:
        return False
    if brightness < brightness_range[0] or brightness > brightness_range[1]:
        return False
    
    return True

def extract_palette(image_path, n_colors=12, target_colors=8):
    """Extract dominant VIVID colors from an image"""
    print(f"Processing: {os.path.basename(image_path)}")
    
    img = Image.open(image_path)
    img = img.convert('RGB')
    img = img.resize((150, 150))
    
    img_array = np.array(img)
    pixels = img_array.reshape(-1, 3)
    
    # Extract more colors than needed, then filter
    kmeans = KMeans(n_clusters=n_colors, random_state=42, n_init=10)
    kmeans.fit(pixels)
    
    colors = kmeans.cluster_centers_.astype(int)
    
    # Filter for vivid colors only
    vivid_colors = [color for color in colors if is_vivid_color(color)]
    
    # Take the target number of vivid colors
    vivid_colors = vivid_colors[:target_colors]
    
    # If we don't have enough vivid colors, lower the threshold and try again
    if len(vivid_colors) < target_colors:
        print(f"  Warning: Only found {len(vivid_colors)} vivid colors, relaxing constraints...")
        vivid_colors = [color for color in colors if is_vivid_color(color, saturation_threshold=20, brightness_range=(30, 245))]
        vivid_colors = vivid_colors[:target_colors]
    
    print(f"  Found {len(vivid_colors)} vivid colors")
    
    # Convert to RGB strings and hex codes
    rgb_colors = [f"rgb({c[0]}, {c[1]}, {c[2]})" for c in vivid_colors]
    hex_colors = [f"#{c[0]:02x}{c[1]:02x}{c[2]:02x}" for c in vivid_colors]
    
    return {
        "rgb": rgb_colors,
        "hex": hex_colors
    }

# List of your image files in chronological order
image_files = [
    "8.12.25.jpeg",
    "9.18.25.jpeg",
    "9.25.25.jpeg",
    "10.9.25.jpeg",
    "10.16.25.jpeg",
    "10.23.25.jpeg",
    "11.6.25.jpeg",
    "11.13.25.jpeg",
    "11.20.25.jpeg",
    "12.11.25.jpeg"
]

print("Extracting VIVID color palettes from art therapy drawings...")
print("(Filtering out whites, grays, and near-blacks)")
print("="*60)

palette_data = {}

for img_file in image_files:
    img_path = f'assets/atdrawings/{img_file}'
    
    if os.path.exists(img_path):
        palette = extract_palette(img_path, n_colors=12, target_colors=8)
        # Use date as key (remove .jpeg extension)
        date_key = img_file.replace('.jpeg', '')
        palette_data[date_key] = palette
    else:
        print(f"Warning: {img_path} not found")

print("="*60)
print(f"✓ Extracted palettes from {len(palette_data)} drawings")

# Save to JSON for frontend use
output_path = 'assets/art_palettes.json'
with open(output_path, 'w') as f:
    json.dump(palette_data, f, indent=2)

print(f"✓ Saved color data to: {output_path}")

# Preview all palettes
print("\nPreview of extracted vivid colors:")
for drawing_name, palette in palette_data.items():
    print(f"\n{drawing_name}:")
    print(f"  {', '.join(palette['hex'][:6])}")