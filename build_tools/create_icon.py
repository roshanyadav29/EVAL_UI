"""
Icon Creation Script for HYDRA GUI

This script processes the HYDRA dragon image and creates a Windows .ico file
for use as the application icon in the executable.
"""

import os
from pathlib import Path

# Try to import PIL for image processing
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

def install_pillow():
    """Install Pillow for image processing."""
    import subprocess
    import sys
    
    print("Installing Pillow for image processing...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow"])
        print("✓ Pillow installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("✗ Failed to install Pillow")
        return False

def create_icon_from_image(image_path, icon_path):
    """Convert image to .ico format with multiple sizes."""
    try:
        from PIL import Image
        
        # Open the source image
        with Image.open(image_path) as img:
            # Convert to RGBA if needed
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            
            # Create multiple sizes for the icon
            icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
            
            # Resize and save as ICO
            img.save(icon_path, format='ICO', sizes=icon_sizes)
            print(f"✓ Icon created: {icon_path}")
            return True
            
    except Exception as e:
        print(f"✗ Error creating icon: {e}")
        return False

def main():
    """Main icon creation process."""
    print("HYDRA GUI Icon Creator")
    print("=" * 30)
    
    project_root = Path(__file__).parent.parent
    build_tools_dir = Path(__file__).parent
    
    # Look for the dragon image in both project root and build_tools folder
    possible_names = [
        "hydra_dragon.png",
        "hydra.png", 
        "dragon.png",
        "hydra_dragon.jpg",
        "hydra.jpg",
        "dragon.jpg"
    ]
    
    image_path = None
    
    # First check the build_tools directory (current folder)
    print("Checking build_tools folder...")
    for name in possible_names:
        test_path = build_tools_dir / name
        if test_path.exists():
            image_path = test_path
            print(f"Found in build_tools: {name}")
            break
    
    # If not found, check project root
    if not image_path:
        print("Checking project root folder...")
        for name in possible_names:
            test_path = project_root / name
            if test_path.exists():
                image_path = test_path
                print(f"Found in project root: {name}")
                break
    
    if not image_path:
        print("Dragon image not found. Please save the HYDRA dragon image as:")
        print("- hydra_dragon.png (recommended)")
        print("- hydra.png")  
        print("- dragon.png")
        print("\nPlace it in either:")
        print(f"  - Project root: {project_root}")
        print(f"  - Build tools folder: {build_tools_dir}")
        return False
    
    print(f"Found image: {image_path}")
    
    # Check if PIL is available
    if not PIL_AVAILABLE:
        if not install_pillow():
            return False
    
    # Create icon
    icon_path = project_root / "hydra_icon.ico"
    if create_icon_from_image(image_path, icon_path):
        print(f"\n✓ HYDRA icon created successfully!")
        print(f"Icon location: {icon_path}")
        
        # Update build config to use the icon
        update_build_config_with_icon(icon_path)
        return True
    else:
        return False

def update_build_config_with_icon(icon_path):
    """Update the build configuration to use the new icon."""
    config_path = Path(__file__).parent / "build_config.py"
    
    try:
        with open(config_path, 'r') as f:
            content = f.read()
        
        # Add icon path to the BuildConfig class
        if "ICON_PATH" not in content:
            # Find the line with SPEC_FILE and add ICON_PATH after it
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if 'SPEC_FILE =' in line:
                    lines.insert(i + 1, f'    ICON_PATH = "{icon_path}"')
                    break
            
            content = '\n'.join(lines)
            
            with open(config_path, 'w') as f:
                f.write(content)
            
            print("✓ Build configuration updated with icon path")
    
    except Exception as e:
        print(f"Warning: Could not update build config automatically: {e}")
        print(f"Please add this line to build_config.py in the BuildConfig class:")
        print(f'    ICON_PATH = "{icon_path}"')

if __name__ == "__main__":
    main()
