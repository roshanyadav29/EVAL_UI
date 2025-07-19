"""
HYDRA GUI Executable Builder

This script creates a standalone executable (.exe) for the HYDRA chip configuration GUI
using PyInstaller. It handles all dependencies, icons, and data files needed for
the application to run independently on Windows systems.

Usage:
    cd build_tools
    python build_exe.py

Output:
    - Creates '../dist/HYDRA_GUI.exe' - Standalone executable
    - Creates '../build/' folder with build artifacts
    - Includes all Python dependencies and GUI assets

Requirements:
    - PyInstaller (pip install pyinstaller)
    - All project dependencies from requirements.txt
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from build_config import BUILD_CONFIGS

# Ensure we're in the project root for building
PROJECT_ROOT = Path(__file__).parent.parent
os.chdir(PROJECT_ROOT)

def check_pyinstaller():
    """Check if PyInstaller is installed and install if needed."""
    try:
        subprocess.run([sys.executable, "-c", "import PyInstaller"], 
                      check=True, capture_output=True)
        print("✓ PyInstaller is installed")
        return True
    except (ImportError, subprocess.CalledProcessError):
        print("Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✓ PyInstaller installed successfully")
        return True

def build_with_config(config_name):
    """Build executable using specified configuration."""
    if config_name not in BUILD_CONFIGS:
        print(f"✗ Unknown configuration: {config_name}")
        print(f"Available configurations: {list(BUILD_CONFIGS.keys())}")
        return False
    
    config = BUILD_CONFIGS[config_name]
    print(f"Building with {config.BUILD_TYPE} configuration...")
    
    try:
        # Prepare PyInstaller command
        cmd = [sys.executable, "-m", "PyInstaller"] + config.get_pyinstaller_args()
        
        print(f"Command: {' '.join(cmd)}")
        print("This may take several minutes...")
        
        # Run PyInstaller
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        print("✓ Build completed successfully!")
        
        # Show output location
        if config.BUILD_TYPE == "onefile":
            exe_path = PROJECT_ROOT / "dist" / f"{config.APP_NAME}.exe"
            print(f"Executable: {exe_path}")
        else:
            dir_path = PROJECT_ROOT / "dist" / config.APP_NAME
            print(f"Distribution folder: {dir_path}")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"✗ Build failed!")
        print(f"Error: {e}")
        if e.stdout:
            print(f"Output: {e.stdout}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
def cleanup_build_files():
    """Clean up build artifacts."""
    build_dirs = [PROJECT_ROOT / 'build', PROJECT_ROOT / '__pycache__']
    
    for dir_path in build_dirs:
        if dir_path.exists():
            shutil.rmtree(dir_path)
            print(f"✓ Cleaned up {dir_path.name}")
    
    # Clean up spec files
    for spec_file in PROJECT_ROOT.glob("*.spec"):
        spec_file.unlink()
        print(f"✓ Removed {spec_file.name}")

def main():
    """Main build process."""
    print("HYDRA GUI Executable Builder")
    print("=" * 40)
    
    # Check current directory and files
    if not (PROJECT_ROOT / "GUI.py").exists():
        print("✗ Error: GUI.py not found. Please ensure script is in build_tools folder.")
        return
    
    # Check PyInstaller
    if not check_pyinstaller():
        return
    
    # Show available configurations
    print("\nAvailable build configurations:")
    for name, config in BUILD_CONFIGS.items():
        print(f"  {name}: {config.__doc__.strip() if config.__doc__ else 'No description'}")
    
    # Ask user for build method
    print("\nBuild options:")
    print("1. One-file executable (recommended for distribution)")
    print("2. Directory distribution (faster startup)")
    print("3. Debug build (for troubleshooting)")
    print("4. All builds")
    
    choice = input("Choose build type (1/2/3/4): ").strip()
    
    # Map choices to configurations
    choice_map = {
        '1': ['onefile'],
        '2': ['directory'], 
        '3': ['debug'],
        '4': ['onefile', 'directory', 'debug']
    }
    
    if choice not in choice_map:
        print("✗ Invalid choice")
        return
    
    configs_to_build = choice_map[choice]
    success_count = 0
    
    # Build each configuration
    for config_name in configs_to_build:
        print(f"\n{'='*20} Building {config_name} {'='*20}")
        if build_with_config(config_name):
            success_count += 1
        else:
            print(f"✗ Failed to build {config_name}")
    
    # Final status
    print("\n" + "=" * 40)
    if success_count == len(configs_to_build):
        print("ALL BUILDS COMPLETED SUCCESSFULLY!")
        print("=" * 40)
        print(f"Build outputs in: {PROJECT_ROOT / 'dist'}")
        print("\nDistribution notes:")
        print("- One-file: Copy .exe to target machine")
        print("- Directory: Copy entire folder to target machine") 
        print("- Debug: Use for troubleshooting build issues")
        print("\nTarget machine requirements:")
        print("- Windows 10/11")
        print("- Arduino CLI (for upload features)")
        print("- ESP32 USB drivers (CP210x)")
    else:
        print(f"PARTIAL SUCCESS: {success_count}/{len(configs_to_build)} builds completed")
        print("=" * 40)
    
    # Ask about cleanup
    cleanup = input("\nClean up build artifacts? (y/n): ").strip().lower()
    if cleanup == 'y':
        cleanup_build_files()

if __name__ == "__main__":
    main()
