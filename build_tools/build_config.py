"""
ESP32 GUI Build Configuration

This module contains all build settings and configurations for creating
the ESP32 Configuration GUI executable. It provides different build profiles
for various deployment scenarios.
"""

import os
from pathlib import Path

# Get project root directory (parent of build_tools)
PROJECT_ROOT = Path(__file__).parent.parent

class BuildConfig:
    """Configuration settings for different build types."""
    
    # Application metadata
    APP_NAME = "HYDRA GUI"
    APP_VERSION = "1.0.0"
    APP_DESCRIPTION = "HYDRA Chip Configuration Interface"
    APP_AUTHOR = "Roshan Yadav"
    
    # Build paths
    MAIN_SCRIPT = str(PROJECT_ROOT / "GUI.py")
    OUTPUT_DIR = str(PROJECT_ROOT / "dist")
    BUILD_DIR = str(PROJECT_ROOT / "build")
    SPEC_FILE = str(PROJECT_ROOT / f"{APP_NAME}.spec")
    ICON_PATH = str(PROJECT_ROOT / "hydra_icon.ico")  # HYDRA dragon icon
    
    # Data files to include (source, destination)
    DATA_FILES = [
        (str(PROJECT_ROOT / "codes"), "codes"),
        (str(PROJECT_ROOT / "main"), "main"),
        (str(PROJECT_ROOT / "states"), "states"),
        (str(PROJECT_ROOT / "README.md"), "."),
        (str(PROJECT_ROOT / "requirements.txt"), "."),
    ]
    
    # Hidden imports (modules not automatically detected)
    HIDDEN_IMPORTS = [
        'PySimpleGUI',
        'serial',
        'serial.tools.list_ports',
        'jaraco.windows.api.memory',
        'jaraco.windows.filesystem',
        'jaraco.classes',
        'jaraco.collections',
        'jaraco.context',
        'jaraco.functools',
        'jaraco.structures',
        'jaraco.text',
        'jaraco.ui',
        'jaraco.windows',
    ]
    
    # Modules to exclude (reduce file size)
    EXCLUDED_MODULES = [
        'matplotlib',
        'numpy',
        'scipy',
        'pandas',
        'jupyter',
        'notebook',
        'IPython',
        'tkinter.test',
        'test',
        'unittest',
        'pdb',
        'doctest',
    ]

class OneFileConfig(BuildConfig):
    """Configuration for single-file executable."""
    
    BUILD_TYPE = "onefile"
    CONSOLE = False  # Hide console window
    UPX = False      # Disable UPX compression for compatibility
    
    @classmethod
    def get_pyinstaller_args(cls):
        """Generate PyInstaller command arguments."""
        args = [
            '--onefile',
            '--clean',
            f'--name={cls.APP_NAME}',
            f'--distpath={cls.OUTPUT_DIR}',
            f'--workpath={cls.BUILD_DIR}',
        ]
        
        # Add console option
        if not cls.CONSOLE:
            args.append('--windowed')
        
        # Add UPX compression (disabled for compatibility)
        # if cls.UPX:
        #     args.append('--upx-dir=upx')  # Requires UPX in PATH
        
        # Add data files
        for src, dst in cls.DATA_FILES:
            args.append(f'--add-data={src};{dst}')
        
        # Add hidden imports
        for module in cls.HIDDEN_IMPORTS:
            args.append(f'--hidden-import={module}')
        
        # Add excluded modules
        for module in cls.EXCLUDED_MODULES:
            args.append(f'--exclude-module={module}')
        
        # Add icon if it exists
        if hasattr(cls, 'ICON_PATH') and Path(cls.ICON_PATH).exists():
            args.append(f'--icon={cls.ICON_PATH}')
        
        # Add main script
        args.append(cls.MAIN_SCRIPT)
        
        return args

class DirectoryConfig(BuildConfig):
    """Configuration for directory-based distribution."""
    
    BUILD_TYPE = "directory"
    CONSOLE = True   # Show console for debugging
    UPX = False     # Don't compress (faster startup)
    
    @classmethod
    def get_pyinstaller_args(cls):
        """Generate PyInstaller command arguments."""
        args = [
            '--onedir',
            '--clean',
            f'--name={cls.APP_NAME}',
            f'--distpath={cls.OUTPUT_DIR}',
            f'--workpath={cls.BUILD_DIR}',
        ]
        
        # Add console option
        if not cls.CONSOLE:
            args.append('--windowed')
        
        # Add data files
        for src, dst in cls.DATA_FILES:
            args.append(f'--add-data={src};{dst}')
        
        # Add hidden imports
        for module in cls.HIDDEN_IMPORTS:
            args.append(f'--hidden-import={module}')
        
        # Add excluded modules
        for module in cls.EXCLUDED_MODULES:
            args.append(f'--exclude-module={module}')
        
        # Add icon if it exists
        if hasattr(cls, 'ICON_PATH') and Path(cls.ICON_PATH).exists():
            args.append(f'--icon={cls.ICON_PATH}')
        
        # Add main script
        args.append(cls.MAIN_SCRIPT)
        
        return args

class DebugConfig(BuildConfig):
    """Configuration for debugging builds."""
    
    BUILD_TYPE = "debug"
    CONSOLE = True   # Always show console for debugging
    UPX = False     # No compression for faster builds
    DEBUG = True    # Enable debug output
    
    @classmethod
    def get_pyinstaller_args(cls):
        """Generate PyInstaller command arguments."""
        args = [
            '--onedir',
            '--debug=all',  # Enable debug output
            '--clean',
            f'--name={cls.APP_NAME}_Debug',
            f'--distpath={cls.OUTPUT_DIR}',
            f'--workpath={cls.BUILD_DIR}',
        ]
        
        # Add data files
        for src, dst in cls.DATA_FILES:
            args.append(f'--add-data={src};{dst}')
        
        # Add hidden imports
        for module in cls.HIDDEN_IMPORTS:
            args.append(f'--hidden-import={module}')
        
        # Don't exclude modules in debug mode
        
        # Add icon if it exists
        if hasattr(cls, 'ICON_PATH') and Path(cls.ICON_PATH).exists():
            args.append(f'--icon={cls.ICON_PATH}')
        
        # Add main script
        args.append(cls.MAIN_SCRIPT)
        
        return args

# Available build configurations
BUILD_CONFIGS = {
    'onefile': OneFileConfig,
    'directory': DirectoryConfig, 
    'debug': DebugConfig,
}
