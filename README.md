# GUI ESP32 - Chip Configuration Tool

A Python GUI application for configuring and programming ESP32 devices with custom serial protocol for chip register control.

## Overview

This project provides a graphical interface for configuring various chip parameters and uploading the configuration to an ESP32 microcontroller. The ESP32 acts as a master device that communicates with a target chip using a custom serial protocol.

## Features

- **Intuitive GUI**: PySimpleGUI-based interface with organized parameter sections
- **Register Configuration**: Configure 128-bit register values across multiple parameter groups
- **Advanced Settings Panel**: Toggleable panel with clock frequency control, serial port selection, and console output
- **Adjustable Clock Frequency**: Configure clock frequency from 50kHz to 2MHz (default: 100kHz)
- **Serial Port Management**: Auto-detection of Silicon Labs CP210x devices with manual port selection
- **Real-time Console**: Monitor operations, uploads, and errors in real-time with concise logging
- **Non-blocking Upload**: Threaded upload operations prevent GUI freezing during ESP32 programming
- **State Management**: Save and load configuration states
- **ESP32 Programming**: Automatic compilation and upload to ESP32 using Arduino CLI
- **Custom Serial Protocol**: Implements clock, data, shift, and reset signal control
- **Enhanced Error Handling**: Comprehensive error detection and user-friendly error messages

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

### Configuration Workflow

1. **Set Parameters**: Use the GUI to configure all required parameters
2. **Advanced Settings** (Optional): Click the `>` button to access:
   - Clock frequency adjustment (50kHz - 2MHz)
   - Serial port selection
   - Real-time console output
3. **Save State** (Optional): Save current configuration for future use
4. **Transfer Data**: Click "TRANSFER DATA" to upload configuration to ESP32 (non-blocking)
5. **Reset**: Click "RESET" to perform reset-only operation (non-blocking)

### Upload Process

The upload process is now non-blocking and user-friendly:

1. **Immediate Feedback**: Console shows "Uploading to ESP32..." message
2. **GUI Remains Responsive**: Interface stays interactive during upload
3. **Progress Indication**: Clear status messages throughout the process
4. **Completion Notification**: Success or failure messages when upload completes
5. **Error Handling**: Detailed error messages for troubleshooting

### Advanced Settings Panel

The advanced settings panel can be toggled by clicking the `>` button and includes:

- **Clock Frequency Control**: Adjustable from 50kHz to 2MHz (default: 100kHz)
- **Serial Port Selection**: Auto-detects Silicon Labs CP210x devices, manual selection available
- **Console Output**: Real-time logging of operations, uploads, and error messages with concise formatting
- **Port Refresh**: Update available serial ports without restarting the application
- **Console Clear**: Clear console output for better readability

### Non-blocking Operations

The application now features threaded upload operations that prevent GUI freezing:

- **Responsive Interface**: GUI remains interactive during ESP32 programming
- **Upload Progress**: Clear feedback when upload operations are in progress
- **Concurrent Protection**: Prevents multiple simultaneous uploads
- **Error Recovery**: Proper error handling without blocking the interface

### GPIO Pin Configuration

Current ESP32 pin assignments (as defined in [`main.ino`](main/main.ino)):
- **Clock Pin**: GPIO 13
- **Data Pin**: GPIO 14
- **Shift Pin**: GPIO 12
- **Reset Pin**: GPIO 27

### Clock Frequency

Default clock frequency is now set to 100 kHz and can be adjusted through the Advanced Settings panel. Available frequencies:
- 50 kHz
- 100 kHz (default)
- 200 kHz
- 500 kHz
- 1 MHz
- 2 MHz

Custom frequencies can be entered directly in the frequency field.

## Serial Protocol

The ESP32 implements a custom serial protocol with the following sequence:

1. **Reset Phase**: RESET low for 2 clock cycles (preparation)
2. **Start Phase**: SHIFT high for 1 clock cycle (start transmission signal)
3. **Data Phase**: RESET and SHIFT both high, transmit 128 bits MSB first
4. **End Phase**: SHIFT low (end of transmission), 2 additional clock cycles to save shift status
5. **Idle Phase**: All signals return to idle state

**Key Points:**
- SHIFT remains HIGH during the entire 128-bit data transmission
- Data is transmitted MSB first (bit 127 to bit 0)
- Data changes on clock falling edge, sampled on rising edge
- SHIFT signal indicates when valid data transmission is occurring

## Files Generated

- **[`WRITTEN_TO_CHIP.txt`](WRITTEN_TO_CHIP.txt)**: Log of the last configuration uploaded
- **State Files**: Saved configurations in `states/` directory

## Dependencies

Key Python packages (see [`requirements.txt`](requirements.txt)):
- PySimpleGUI: GUI framework
- pyserial: Serial communication
- in_place: File modification utilities
- Various jaraco packages for Windows compatibility

## Development

The project uses a modular architecture:

- **[`complete_gui.py`](codes/complete_gui.py)**: Main GUI event loop and logic
- **[`gui_parameters.py`](codes/gui_parameters.py)**: GUI layout definitions
- **[`register_assignment.py`](codes/register_assignment.py)**: Maps GUI values to 128-bit register
- **[`register2arduino.py`](codes/register2arduino.py)**: Generates Arduino code
- **[`upload2Arduino.py`](codes/upload2Arduino.py)**: Handles ESP32 programming

## Hardware Requirements

- ESP32 development board
- USB cable for programming
- Target chip with compatible serial interface
- Proper GPIO connections between ESP32 and target

## Troubleshooting

1. **Upload Issues**: Check ESP32 connection and ensure Arduino CLI is properly installed
2. **Port Detection**: Use the "Refresh" button in Advanced Settings to update available ports
3. **Clock Frequency**: Ensure the selected frequency is compatible with your target hardware
4. **Console Errors**: Check the console output in Advanced Settings for detailed error messages
5. **Compilation Errors**: Verify ESP32 board support is installed in Arduino CLI
6. **GUI Freezing**: If GUI becomes unresponsive, restart the application (upload operations are now non-blocking)
7. **Multiple Uploads**: If you see "Upload already in progress", wait for current upload to complete
8. **CP210x Detection**: Ensure Silicon Labs CP210x drivers are installed for automatic port detection

## Recent Improvements

- **Enhanced Logging**: Concise, user-friendly console messages
- **Threaded Uploads**: Non-blocking upload operations prevent GUI freezing
- **Better Error Handling**: Improved error detection and user feedback
- **Port Detection**: Enhanced Silicon Labs CP210x device detection
- **UI Polish**: Cleaner interface with better visual feedback
- **Concurrent Upload Protection**: Prevents multiple simultaneous uploads

## License

This project is for educational/research purposes. Please check with the original authors for usage or development concerns.