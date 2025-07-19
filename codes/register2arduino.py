"""
ESP32 Communication Interface Module

This module implements the master side of the custom serial protocol for ESP32 
chip configuration. It provides two communication methods: Arduino IDE upload 
and direct serial communication for transferring 128-bit register configurations.

Key Features:
- Arduino .ino file modification for upload-based transfers
- Direct serial communication for real-time configuration
- GPIO pin configuration management
- SPI protocol parameter handling
- Error handling and timeout management

Communication Methods:
1. Upload Method: Modifies main.ino file with register data for Arduino IDE upload
2. Serial Method: Direct UART communication with ESP32 for immediate transfer

Dependencies:
- in_place: For safe Arduino file modification
- serial: For UART communication with ESP32
- time: For timing control and timeouts

File Targets:
- main/main.ino: Arduino sketch for ESP32 SPI configuration
"""

import in_place
import serial
import time

def reg2ino(Data, clk_freq_khz):
    """
    Modify Arduino .ino file with register configuration data (Upload Method).
    
    This function updates the main.ino file with new register data, clock frequency,
    and GPIO pin assignments. The modified file can then be uploaded to ESP32 via
    Arduino IDE for persistent configuration storage.
    
    Args:
        Data (list): 16-byte register configuration array from RegisterAssignment
        clk_freq_khz (int): SPI clock frequency in kHz (500, 1000, 5000, 10000)
    
    Technical Details:
        - Modifies specific marker comments in main.ino
        - Updates GPIO pin definitions for SPI communication
        - Changes setup() function to call data transfer instead of reset
        - Preserves existing Arduino code structure
    
    GPIO Pin Mapping:
        - Clock: GPIO 18 (SPI CLK)
        - Data: GPIO 23 (SPI MOSI) 
        - Shift: GPIO 26 (Transfer control signal)
        - Reset: GPIO 33 (Chip reset control)
    """
    # === SPI GPIO PIN CONFIGURATION ===
    # GPIO pin assignments - MUST match main.ino SPI configuration
    clock_pin = 18  # SPI CLK pin - Hardware SPI clock signal
    data_pin = 23   # SPI MOSI pin - Master Out Slave In data line
    shift_pin = 26  # Transfer control - High during data transmission
    reset_pin = 33  # Chip reset control - Low during transmission, high normally

    print(f"Clock frequency: {clk_freq_khz} kHz")
    print(f"GPIO pins - Clock: {clock_pin}, Data: {data_pin}, Shift: {shift_pin}, Reset: {reset_pin}")

    # === ARDUINO FILE MODIFICATION STRINGS ===
    # === ARDUINO FILE MODIFICATION STRINGS ===
    # Prepare replacement strings for different sections of main.ino
    
    # Data array section - 16-byte register configuration
    str1 = "/*MODIFY DATA HERE*/ byte Data[16] = {"
    str2 = ",".join(str(x) for x in Data)  # Convert list to comma-separated values
    str3 = "};"

    # Clock frequency section - SPI timing control
    str4 = "/*MODIFY CLK_FREQ HERE*/ int clk_freq_khz = "
    str5 = str(clk_freq_khz)
    str6 = ";"

    # GPIO pin definitions section - Complete pin configuration block
    str7 = "/*MODIFY GPIO PINS HERE*/ \nconst int CLOCK_PIN = "
    str8 = str(clock_pin)
    str9 = ";     // Clock GPIO pin\nconst int DATA_PIN = "
    str10 = str(data_pin)
    str11 = ";      // Data GPIO pin  \nconst int SHIFT_PIN = "
    str12 = str(shift_pin)
    str13 = ";      // Shift GPIO pin (high during data transmission)\nconst int RESET_PIN = "
    str14 = str(reset_pin)
    str15 = ";     // Reset GPIO pin (low during transmission, high normally)\nconst int LED_BUILTIN = 2;    // Built-in LED pin (usually GPIO 2 on ESP32)"

    # === ARDUINO FILE PROCESSING ===
    # In-place modification of main.ino with error-safe file handling
    with in_place.InPlace("main/main.ino") as file:
        skip_gpio_lines = False
        in_setup_function = False
        
        for line in file:
            # Track if we're in the setup() function for context-aware replacements
            if line.strip().startswith("void setup()"):
                in_setup_function = True
            elif line.strip() == "}" and in_setup_function:
                in_setup_function = False
                
            # Replace register data array
            if line.startswith('/*MODIFY DATA HERE*/'):
                line = str1 + str2 + str3 + "\n"
                print(line)

            # Replace clock frequency setting
            if line.startswith('/*MODIFY CLK_FREQ HERE*/'):
                line = str4 + str5 + str6 + "\n"
                print(line)

            # Update GPIO pin definitions block
            if line.startswith('/*MODIFY GPIO PINS HERE*/'):
                line = str7 + str8 + str9 + str10 + str11 + str12 + str13 + str14 + str15 + "\n"
                print("Updated GPIO pin definitions")
                skip_gpio_lines = True
            elif skip_gpio_lines and line.strip().startswith('const int LED_BUILTIN'):
                skip_gpio_lines = False
                continue  # Skip this line as it's included in the GPIO replacement
            elif skip_gpio_lines and (line.strip().startswith('const int CLOCK_PIN') or 
                                     line.strip().startswith('const int DATA_PIN') or 
                                     line.strip().startswith('const int SHIFT_PIN') or 
                                     line.strip().startswith('const int RESET_PIN')):
                continue  # Skip existing GPIO pin lines to avoid duplicates

            # Switch from reset mode to data transfer mode in setup() function
            if in_setup_function and line.strip() == "sendResetSequence();":
                line = "  sendDataSequence();\n"
                print("Changed to data transfer mode in setup()")

            file.write(line)

def serial_transfer_data(Data, port_name, timeout=5):
    """
    Transfer register data to ESP32 via direct serial communication (Serial Method).
    
    This function provides fast, real-time configuration transfer without requiring
    Arduino IDE upload. It sends the 128-bit register configuration directly to
    the ESP32 via UART and waits for confirmation.
    
    Args:
        Data (list): 16-byte register configuration array from RegisterAssignment
        port_name (str): Serial port identifier (e.g., 'COM3', '/dev/ttyUSB0')
        timeout (int): Communication timeout in seconds (default: 5)
    
    Returns:
        bool: True if transfer successful, False if failed
    
    Protocol Format:
        Send: <byte1><byte2>...<byte16>
        Receive: ESP32 status messages ending with "TRANSFER_COMPLETE" or "ERROR"
    
    Technical Details:
        - Baud rate: 115200 (standard ESP32 UART speed)
        - Buffer clearing for clean communication
        - Response parsing with timeout handling
        - Error detection and reporting
    """
    try:
        # Establish serial connection with ESP32
        with serial.Serial(port_name, 115200, timeout=timeout) as ser:
            print(f"Serial transfer to {port_name} - Data: {Data}")
            
            # Connection stabilization delay
            time.sleep(0.1)
            
            # Clear communication buffers for clean transfer
            ser.reset_input_buffer()
            ser.reset_output_buffer()
            
            # Send data packet with protocol delimiters: <data>
            data_packet = b'<' + bytes(Data) + b'>'
            ser.write(data_packet)
            
            print(f"Sent data packet: {data_packet}")
            
            # === RESPONSE MONITORING LOOP ===
            # Wait for ESP32 confirmation with timeout protection
            start_time = time.time()
            responses = []
            
            while time.time() - start_time < timeout:
                if ser.in_waiting > 0:
                    response = ser.readline().decode('utf-8').strip()
                    if response:
                        responses.append(response)
                        print(f"ESP32 response: {response}")
                        
                        # Check for successful completion
                        if "TRANSFER_COMPLETE" in response:
                            print("Serial data transfer completed successfully!")
                            return True
                        elif "ERROR" in response:
                            print(f"ESP32 reported error: {response}")
                            return False
                
                time.sleep(0.01)  # Prevent busy waiting, allow other processes
            
            print("Timeout waiting for ESP32 response")
            return False
            
    except serial.SerialException as e:
        print(f"Serial communication error: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error during serial transfer: {e}")
        return False

def serial_reset(port_name, timeout=3):
    """
    Send reset command to ESP32 via direct serial communication.
    
    This function sends a reset command to the ESP32 to restore default
    chip configuration or clear previous settings. Useful for returning
    the chip to a known state before new configuration.
    
    Args:
        port_name (str): Serial port identifier (e.g., 'COM3', '/dev/ttyUSB0')
        timeout (int): Communication timeout in seconds (default: 3)
    
    Returns:
        bool: True if reset successful, False if failed
    
    Protocol Format:
        Send: R (single byte reset command)
        Receive: ESP32 status messages ending with "RESET_COMPLETE" or "ERROR"
    
    Technical Details:
        - Reset command is single byte 'R'
        - Shorter timeout since reset is faster than data transfer
        - ESP32 will restore chip to default register values
        - Buffer clearing ensures clean reset operation
    """
    try:
        # Establish serial connection with ESP32
        with serial.Serial(port_name, 115200, timeout=timeout) as ser:
            print(f"Serial reset to {port_name}")
            
            # Connection stabilization delay
            time.sleep(0.1)
            
            # Clear communication buffers for clean reset
            ser.reset_input_buffer()
            ser.reset_output_buffer()
            
            # Send single-byte reset command
            ser.write(b'R')
            
            print("Sent reset command: R")
            
            # === RESET RESPONSE MONITORING ===
            # Wait for ESP32 reset confirmation
            start_time = time.time()
            responses = []
            
            while time.time() - start_time < timeout:
                if ser.in_waiting > 0:
                    response = ser.readline().decode('utf-8').strip()
                    if response:
                        responses.append(response)
                        print(f"ESP32 response: {response}")
                        
                        # Check for successful reset completion
                        if "RESET_COMPLETE" in response:
                            print("Serial reset completed successfully!")
                            return True
                        elif "ERROR" in response:
                            print(f"ESP32 reported error: {response}")
                            return False
                
                time.sleep(0.01)  # Prevent busy waiting
            
            print("Timeout waiting for ESP32 reset response")
            return False
            
    except serial.SerialException as e:
        print(f"Serial communication error: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error during serial reset: {e}")
        return False


