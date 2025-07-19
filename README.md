# GUI ESP32 - Chip Configuration Tool

A Python GUI application for configuring and programming ESP32 devices with custom serial protocol for chip register control.

## Overview

This project provides a graphical interface for configuring 128-bit chip parameters and uploading the configuration to an ESP32 microcontroller. The ESP32 acts as a master device that communicates with a target chip using SPI-based custom serial protocol.

## Features

- **PySimpleGUI Interface**: Organized parameter sections with real-time console logging
- **128-bit Register Configuration**: Configure multiple parameter groups (CSH_EN, PI_EN, delay controls, current controls, filters, etc.)
- **Dual Transfer Methods**: 
  - **TRANSFER DATA**: Fast serial communication for real-time updates
  - **UPLOAD DATA**: Full Arduino firmware upload with new configuration
- **Advanced Settings Panel**: Clock frequency (50kHz-2MHz), serial port auto-detection, console output
- **State Management**: Save and load configuration presets
- **Non-blocking Operations**: Threaded uploads prevent GUI freezing

## Project Structure

```
GUI_ESP32/
├── GUI.py                 # Main application entry point
├── requirements.txt       # Python dependencies
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

## Installation

1. **Install Python Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Install Arduino CLI**:
   - Download and install Arduino CLI from [official website](https://arduino.github.io/arduino-cli/)
   - Install ESP32 board support:
     ```bash
     arduino-cli core install esp32:esp32
     ```

3. **Hardware Setup**:
   - Connect ESP32 to your computer via USB
   - Ensure proper GPIO connections as defined in the code

## Usage

### Running the Application

```bash
python GUI.py
```

### Operation Modes

1. **TRANSFER DATA**: Send configuration via serial (fast, for testing)
2. **UPLOAD DATA**: Program ESP32 firmware with configuration (permanent)
3. **RESET**: Send reset signal to target chip

### Configuration Steps

1. Set parameters using GUI controls
2. Optional: Adjust clock frequency in Advanced Settings (default: 100kHz)
3. Choose transfer method (TRANSFER for testing, UPLOAD for permanent)
4. Monitor progress in console output

## Hardware Configuration

**ESP32 GPIO Pins** (defined in `main.ino`):
- Clock: GPIO 18 (SPI CLK)
- Data: GPIO 23 (SPI MOSI)  
- Shift: GPIO 26
- Reset: GPIO 33

**Clock Frequencies**: 50kHz - 2MHz (default: 100kHz)

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
GUI_ESP32/
├── GUI.py                    # Main entry point
├── main/main.ino            # ESP32 firmware
├── codes/
│   ├── complete_gui.py      # GUI event handling
│   ├── gui_parameters.py    # Layout definitions  
│   ├── register_assignment.py # 128-bit register mapping
│   ├── Analog2Bits.py       # GUI → integer conversion
│   ├── register2arduino.py  # Serial communication
│   └── upload2Arduino.py    # ESP32 programming
├── states/                  # Configuration presets
└── WRITTEN_TO_CHIP.txt     # Last configuration log
```

## Architecture

- **GUI Layer**: PySimpleGUI interface with parameter controls
- **Conversion Layer**: GUI values → 128-bit register mapping  
- **Communication Layer**: Serial protocol + Arduino CLI integration
- **Hardware Layer**: ESP32 SPI-based transmission to target chip

## Key Dependencies

- `PySimpleGUI`: GUI framework
- `pyserial`: Serial communication
- `arduino-cli`: ESP32 programming
- `in_place`: File modification

## Troubleshooting

- **Port Detection**: Use "Refresh" in Advanced Settings
- **Upload Errors**: Check ESP32 connection and Arduino CLI installation  
- **Serial Issues**: Verify ESP32 is programmed and connected
- **Clock Compatibility**: Adjust frequency for target hardware requirements

## License

This project is for educational/research purposes. Please check with the original authors for usage or development concerns.