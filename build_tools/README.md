# HYDRA GUI Build Tools

This folder contains all the tools and configurations needed to build standalone executables of the HYDRA Chip Configuration GUI.

## Contents

- `build_exe.py` - Main build script with interactive options
- `build_config.py` - Build configuration classes for different deployment scenarios
- `create_icon.py` - Icon creation script for HYDRA dragon branding
- `BUILD_INSTRUCTIONS.md` - Detailed build instructions and troubleshooting

## Quick Start

### From Project Root
```bash
# Run the convenient batch file (Windows)
build.bat

# Or manually:
cd build_tools
python build_exe.py
```

### Build Options
1. **One-file executable** - Single .exe file (~50-100MB)
   - Best for distribution
   - Slower startup (extracts to temp)
   - No external dependencies

2. **Directory distribution** - Folder with multiple files
   - Faster startup
   - Smaller individual files  
   - Copy entire folder to deploy

3. **Debug build** - For troubleshooting
   - Console output enabled
   - No compression
   - Detailed error messages

## HYDRA Dragon Icon

The build system automatically includes the HYDRA dragon icon:
1. Save the dragon image as `hydra_dragon.png` in the project root
2. Run `python create_icon.py` to create the .ico file
3. Build process will automatically use the icon

## Output Locations

All build outputs go to the `dist/` folder in the project root:

```
../dist/
├── HYDRA_GUI.exe                     # One-file build
├── HYDRA_GUI/                        # Directory build
│   ├── HYDRA_GUI.exe
│   └── _internal/
└── HYDRA_GUI_Debug/                  # Debug build
    ├── HYDRA_GUI_Debug.exe
    └── _internal/
```

## Git Integration

The following patterns are automatically ignored by Git:
- `build/` - PyInstaller build cache
- `dist/` - Distribution outputs  
- `*.spec` - PyInstaller spec files
- Build logs and temporary files

## Dependencies

The build process automatically handles:
- PyInstaller installation
- Hidden import detection
- Data file inclusion
- Module exclusions for size optimization

## Troubleshooting

### Common Issues

1. **Import errors**: Add modules to `HIDDEN_IMPORTS` in `build_config.py`
2. **Missing files**: Add to `DATA_FILES` in `build_config.py`
3. **Large file size**: Add unused modules to `EXCLUDED_MODULES`

### Debug Process

1. Use debug build configuration
2. Check console output for errors
3. Test on clean machine without Python
4. Verify all GUI functions work

## Customization

Edit `build_config.py` to:
- Add/remove hidden imports
- Include additional data files
- Exclude unused modules
- Change app metadata
- Modify build settings

## Distribution

### Single File
- Copy `HYDRA_GUI.exe` to target machine
- No other files needed

### Directory 
- Copy entire `HYDRA_GUI/` folder
- Maintain folder structure
- Run from main executable

### Requirements for Target Machines
- Windows 10/11 (64-bit)
- Arduino CLI (for upload features)
- ESP32 USB drivers (CP210x)
