# HYDRA GUI - Chip Configuration Tool

A Python GUI application for configuring and programming HYDRA chip via ESP32 devices with custom serial protocol for precise register control.

## Overview

This project provides a graphical interface for configuring 128-bit HYDRA chip parameters and uploading the configuration to an ESP32 microcontroller. The ESP32 acts as a master device that communicates with the HYDRA chip using SPI-based custom serial protocol.

## Features

- **PySimpleGUI Interface**: Organized parameter sections with real-time console logging
- **128-bit HYDRA Register Configuration**: Configure multiple parameter groups (CSH_EN, PI_EN, delay controls, current controls, filters, etc.)
- **Dual Transfer Methods**: 
  - **TRANSFER DATA**: Fast serial communication for real-time updates
  - **UPLOAD DATA**: Full Arduino firmware upload with new configuration
- **Advanced Settings Panel**: Clock frequency (50kHz-2MHz), serial port auto-detection, console output
- **State Management**: Save and load configuration presets
- **Non-blocking Operations**: Threaded uploads prevent GUI freezing
- **Standalone Executable**: Build system creates HYDRA_GUI.exe with dragon icon

## Project Structure

```
HYDRA_GUI/
├── GUI.py                 # Main application entry point
├── requirements.txt       # Python dependencies
├── build.bat             # Quick build script for HYDRA_GUI.exe
├── build_tools/          # Executable build system
│   ├── build_exe.py      # Interactive build script
│   ├── build_config.py   # Build configurations
│   ├── create_icon.py    # HYDRA dragon icon creator
│   └── README.md         # Build documentation
├── main/
│   └── main.ino          # Arduino code for ESP32
├── codes/
│   ├── complete_gui.py   # Main GUI logic and event handling
│   ├── gui_parameters.py # GUI layout and parameter definitions
│   ├── register_assignment.py # Register bit mapping and assignment
│   ├── register2arduino.py # Arduino code generation
│   ├── Analog2Bits.py    # GUI value to bit conversion
│   ├── upload2Arduino.py # ESP32 upload functionality
│   └── utils.py          # Utility functions
├── states/               # Saved configuration states
└── WRITTEN_TO_CHIP.txt   # Last uploaded configuration log
```

## Installation & Usage

### Option 1: Use Pre-built Executable (Recommended)
1. **Download**: Get `HYDRA_GUI.exe` from the releases
2. **Run**: Double-click to launch the HYDRA configuration interface
3. **Connect**: Plug in your ESP32 with HYDRA chip setup
4. **Configure**: Set parameters and upload to HYDRA chip

### Option 2: Build from Source

1. **Install Python Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Build Executable** (creates HYDRA_GUI.exe with dragon icon):
   ```bash
   # Quick build
   build.bat
   
   # Or detailed build options
   cd build_tools
   python build_exe.py
   ```

3. **Install Arduino CLI** (for upload features):
   - Download from [Arduino CLI official website](https://arduino.github.io/arduino-cli/)
   - Install ESP32 board support:
     ```bash
     arduino-cli core install esp32:esp32
     ```

### Option 3: Run from Source
```bash
python GUI.py
```

### HYDRA Chip Operation

1. **TRANSFER DATA**: Send configuration via serial (fast, for testing)
2. **UPLOAD DATA**: Program ESP32 firmware with configuration (permanent)
3. **RESET**: Send reset signal to HYDRA chip

### Configuration Steps

1. Set HYDRA parameters using GUI controls
2. Optional: Adjust clock frequency in Advanced Settings (default: 100kHz)
3. Choose transfer method (TRANSFER for testing, UPLOAD for permanent)
4. Monitor progress in console output

## Hardware Configuration

**ESP32 to HYDRA Chip Connections** (defined in `main.ino`):
- Clock: GPIO 18 (SPI CLK)
- Data: GPIO 23 (SPI MOSI)  
- Shift: GPIO 26
- Reset: GPIO 33

**Clock Frequencies**: 50kHz - 10MHz (default: 100kHz)

## Serial Protocol

Custom SPI-based protocol for 128-bit data transmission:

1. **Reset Phase**: RESET low for initialization
2. **Data Transmission**: SHIFT high during 128-bit transfer (MSB first)
3. **Completion**: SHIFT low, additional cycles for status save

Key characteristics:
- MSB-first transmission (bit 127 → bit 0)
- SHIFT signal indicates active data transmission
- SPI hardware acceleration for reliable timing

## Project Structure

```
HYDRA_GUI/
├── GUI.py                    # Main entry point
├── main/main.ino            # ESP32 firmware for HYDRA communication
├── codes/
│   ├── complete_gui.py      # GUI event handling
│   ├── gui_parameters.py    # Layout definitions  
│   ├── register_assignment.py # HYDRA 128-bit register mapping
│   ├── Analog2Bits.py       # GUI → integer conversion
│   ├── register2arduino.py  # Serial communication to ESP32
│   └── upload2Arduino.py    # ESP32 programming
├── build_tools/             # Executable build system
│   ├── build_exe.py         # Interactive build script
│   ├── build_config.py      # Build configuration
│   └── create_icon.py       # HYDRA dragon icon generator
├── states/                  # HYDRA configuration presets
├── dist/                    # Built executables (HYDRA_GUI.exe)
└── WRITTEN_TO_CHIP.txt     # Last HYDRA configuration log
```

## Architecture

- **GUI Layer**: PySimpleGUI interface with HYDRA parameter controls
- **Conversion Layer**: GUI values → HYDRA 128-bit register mapping  
- **Communication Layer**: Serial protocol + Arduino CLI integration
- **Hardware Layer**: ESP32 SPI-based transmission to HYDRA chip

## Key Dependencies

- `PySimpleGUI`: GUI framework
- `pyserial`: Serial communication
- `arduino-cli`: ESP32 programming

## Troubleshooting

- **Port Detection**: Use "Refresh" in Advanced Settings
- **Upload Errors**: Check ESP32 connection and Arduino CLI installation  
- **Serial Issues**: Verify ESP32 is programmed and connected
- **Clock Compatibility**: Adjust frequency for target hardware requirements

## License

This project is for educational/research purposes. Please check with the original authors for usage or development concerns.

**Contact**: 30005500@iitb.ac.in