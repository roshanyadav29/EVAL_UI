# ESP32 Configuration GUI - Distribution Setup

## Quick Build Instructions

### Option 1: Automated Build Script (Recommended)
```bash
# Run the automated build script
python build_exe.py
```

### Option 2: Manual PyInstaller Commands

#### Step 1: Install PyInstaller
```bash
pip install pyinstaller
```

#### Step 2: Simple One-File Build
```bash
pyinstaller --onefile --windowed --add-data "codes;codes" --add-data "main;main" --add-data "states;states" --hidden-import PySimpleGUI --hidden-import serial --hidden-import serial.tools.list_ports --hidden-import in_place --name ESP32_Config_GUI GUI.py
```

#### Step 3: Advanced Build (Multiple Files)
```bash
pyinstaller --add-data "codes;codes" --add-data "main;main" --add-data "states;states" --hidden-import PySimpleGUI --hidden-import serial --hidden-import serial.tools.list_ports --hidden-import in_place --name ESP32_Config_GUI GUI.py
```

## Distribution Options

### Single File Executable
- **File**: `dist/ESP32_Config_GUI.exe`
- **Size**: Larger (~50-100MB)
- **Distribution**: Copy single .exe file
- **Startup**: Slower (extracts to temp)

### Directory Distribution
- **Folder**: `dist/ESP32_Config_GUI/`
- **Size**: Smaller individual files
- **Distribution**: Copy entire folder
- **Startup**: Faster

## Troubleshooting

### Common Issues

1. **Missing Modules Error**
   ```bash
   # Add hidden imports for missing modules
   --hidden-import module_name
   ```

2. **File Not Found Errors**
   ```bash
   # Add data files and folders
   --add-data "source_path;dest_path"
   ```

3. **PySimpleGUI Issues**
   ```bash
   # Make sure PySimpleGUI is properly included
   --hidden-import PySimpleGUI
   ```

### Dependencies Check
Run before building:
```bash
python -c "import PySimpleGUI, serial, in_place; print('All dependencies OK')"
```

## Deployment Requirements

### Target Machine Requirements
- Windows 10/11 (64-bit)
- Arduino CLI (if using upload features)
- ESP32 drivers (CP210x USB to UART Bridge)

### Optional Additions
- Custom icon: Add `--icon icon.ico`
- Version info: Add `--version-file version.txt`
- Console hiding: Use `--windowed` (remove for debugging)

## Build Performance Tips

1. **Exclude unused modules**: Use `--exclude-module` for large unused packages
2. **UPX compression**: Add `--upx-dir path/to/upx` for smaller files
3. **Clean builds**: Use `--clean` to remove cached files

## Testing the Executable

1. Test on clean machine without Python
2. Verify all GUI functions work
3. Test ESP32 communication features
4. Check file operations (save/load states)

## File Structure After Build

```
dist/
├── ESP32_Config_GUI.exe (if --onefile)
└── ESP32_Config_GUI/ (if directory build)
    ├── ESP32_Config_GUI.exe
    ├── _internal/
    ├── codes/
    ├── main/
    └── states/
```
