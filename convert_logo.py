#!/usr/bin/env python3
import json
import os

# Read your existing logo file
logo_path = os.path.expanduser("~/.config/fastfetch/logo.txt")

with open(logo_path, 'r') as f:
    lines = [line.rstrip('\n') for line in f]

# Define your color mapping
# Change these to match your desired colors
color_mapping = {
    '@': '#0000FF',   # Blue for @
    '%': '#FF0000',   # Red for %
    # Add more characters if needed:
    # '#': '#00FF00',  # Green for #
    # '&': '#FFFF00',  # Yellow for &
    # '*': '#FF00FF',  # Magenta for *
}

# Create the config
config = {
    'logo': {
        'source': 'ascii',
        'ascii': {
            'lines': lines,
            'colorMapping': color_mapping
        }
    }
}

# Save the config
config_path = os.path.expanduser("~/.config/fastfetch/config.jsonc")
with open(config_path, 'w') as f:
    json.dump(config, f, indent=4)

print(f"Config created at {config_path}")
print(f"Using {len(lines)} lines from your logo")
print(f"Color mapping: {color_mapping}")
