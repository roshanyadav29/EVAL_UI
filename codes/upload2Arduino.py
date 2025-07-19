"""
Arduino CLI Upload Interface Module

This module provides automated Arduino sketch compilation and upload functionality
for ESP32 chip configuration. It handles the upload method of transferring register
configurations to the ESP32 by compiling and flashing the main.ino Arduino sketch.

Key Features:
- Automated ESP32 port detection via CP210x USB-to-serial drivers
- Cross-platform Arduino CLI command execution
- Compilation error detection and reporting
- Upload status verification and error handling
- Fallback port configuration for reliable operation

Technical Context:
- Uses Arduino CLI for ESP32 toolchain management
- Targets esp32:esp32:esp32 board configuration
- Integrates with register2arduino.py for complete upload workflow
- Provides persistent configuration storage on ESP32 flash memory

Dependencies:
- arduino-cli: Command-line Arduino development environment
- serial.tools.list_ports: For automatic port detection
- os: For system command execution and path handling

Hardware Requirements:
- ESP32 development board with USB connection
- CP210x USB-to-serial bridge (common on ESP32 boards)
- Arduino IDE ESP32 board package installed
"""

import os
import serial.tools.list_ports


def upload(file, port=None):
    """
    Compile and upload Arduino sketch to ESP32 using Arduino CLI.
    
    This function automates the complete Arduino development workflow for ESP32
    configuration upload. It handles port detection, sketch compilation, and
    firmware upload with comprehensive error checking and status reporting.
    
    Args:
        file (str): Arduino sketch file path (typically "main/main.ino")
        port (str, optional): Specific COM port to use. If None, auto-detects ESP32
    
    Returns:
        bool: True if compilation and upload successful, False if any step failed
    
    Process Flow:
        1. Auto-detect ESP32 port (or use provided port)
        2. Compile Arduino sketch for ESP32 target
        3. Upload compiled firmware to ESP32 flash memory
        4. Verify upload completion and report status
    
    Technical Details:
        - Board FQBN: esp32:esp32:esp32 (generic ESP32 configuration)
        - Verbose output enabled for debugging (-v flag)
        - Cross-platform path handling for file operations
        - CP210x driver detection for ESP32 identification
    
    Error Handling:
        - Compilation errors: Syntax, library, or configuration issues
        - Upload errors: Connection, port, or hardware problems
        - Port detection: Fallback to default port if auto-detection fails
    """

    # === ESP32 PORT DETECTION AND CONFIGURATION ===
    # Use provided port or auto-detect ESP32's communication port
    if port:
        PORT = port
        print(f"Using specified port: {PORT}")
    else:
        PORT = "COM3"  # Default fallback port for Windows systems
        
        # Auto-detect ESP32 via CP210x USB-to-serial bridge driver
        ports = list(serial.tools.list_ports.comports())
        for p in ports:
            # CP210x is the common USB-to-serial chip on ESP32 dev boards
            if "Silicon Labs CP210x" in str(p) or "CP210x" in str(p):
                PORT = str(p.device)
                print(f"Auto-detected ESP32 on port: {PORT}")
                break  # Use first ESP32 found
        
        if PORT == "COM3":  # No ESP32 auto-detected
            print(f"No ESP32 auto-detected. Using fallback port: {PORT}")

    # === FILE PATH PREPARATION ===
    # === FILE PATH PREPARATION ===
    # Handle cross-platform path construction for Arduino sketch
    cwd = os.getcwd()  # Current working directory
    file_path = os.path.join(cwd, file)  # Cross-platform path joining (Windows/Linux/Mac)

    # === ARDUINO CLI COMMAND PREPARATION ===
    # Prepare compilation and upload commands with verbose output
    compile_cmd = f'arduino-cli compile --fqbn esp32:esp32:esp32 -v "{file_path}"'
    upload_cmd = f'arduino-cli upload -p {PORT} --fqbn esp32:esp32:esp32 -v "{file_path}"'

    print(f"Using port: {PORT}")
    print(f"Target file: {file_path}")
    
    # === COMPILATION PHASE ===
    # Compile Arduino sketch for ESP32 target architecture
    print("Compiling the ESP32 code...")
    # === COMPILATION PHASE ===
    # Compile Arduino sketch for ESP32 target architecture
    print("Compiling the ESP32 code...")
    print(f"Compile command: {compile_cmd}")
    compile_status = os.system(compile_cmd)

    # === UPLOAD PHASE ===
    # Check compilation result and proceed with upload if successful
    if compile_status == 0:  # Compilation successful (exit code 0)
        print("✓ Compilation successful. Uploading to ESP32...")
        print(f"Upload command: {upload_cmd}")
        upload_status = os.system(upload_cmd)
        
        # Verify upload completion
        if upload_status == 0:  # Upload successful (exit code 0)
            print("✓ Program successfully uploaded to ESP32!")
            print("ESP32 is now configured with new register settings.")
            return True
        else:
            print("✗ Error: Upload failed. Check your ESP32 connection and try again.")
            print("Troubleshooting tips:")
            print("  - Verify ESP32 is connected via USB")
            print("  - Check if correct port is detected")
            print("  - Ensure ESP32 is not in use by other applications")
            print("  - Try pressing ESP32 reset button before upload")
            return False
    else:
        print("✗ Error: Compilation failed. Please check your code for errors.")
        print("Common compilation issues:")
        print("  - Missing Arduino ESP32 board package")
        print("  - Syntax errors in main.ino")
        print("  - Missing or incorrect library dependencies")
        print("  - Invalid board configuration (FQBN)")
        return False
