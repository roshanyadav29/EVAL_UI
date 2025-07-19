"""
For MASTER part of the Custom Serial Protocol
Writes the register values into the .ino file
File location : main/main.ino
"""

import in_place
import serial
import time

def reg2ino(Data, clk_freq_khz):
    """ 
    Input: 
    - Data: 16 bytes of Data in a list 
    - clk_freq_khz: Clock frequency in kHz (500, 1000, 5000, 10000)
    """
    # GPIO pin assignments - MUST match main.ino SPI configuration
    clock_pin = 18  # SPI CLK pin
    data_pin = 23   # SPI MOSI pin 
    shift_pin = 26  # Keep same
    reset_pin = 33  # Keep same

    print(f"Clock frequency: {clk_freq_khz} kHz")
    print(f"GPIO pins - Clock: {clock_pin}, Data: {data_pin}, Shift: {shift_pin}, Reset: {reset_pin}")

    # Prepare strings for data array
    str1 = "/*MODIFY DATA HERE*/ byte Data[16] = {"
    str2 = ",".join(str(x) for x in Data)
    str3 = "};"

    # Prepare strings for clock frequency
    str4 = "/*MODIFY CLK_FREQ HERE*/ int clk_freq_khz = "
    str5 = str(clk_freq_khz)
    str6 = ";"

    # Prepare strings for GPIO pins
    str7 = "/*MODIFY GPIO PINS HERE*/ \nconst int CLOCK_PIN = "
    str8 = str(clock_pin)
    str9 = ";     // Clock GPIO pin\nconst int DATA_PIN = "
    str10 = str(data_pin)
    str11 = ";      // Data GPIO pin  \nconst int SHIFT_PIN = "
    str12 = str(shift_pin)
    str13 = ";      // Shift GPIO pin (high during data transmission)\nconst int RESET_PIN = "
    str14 = str(reset_pin)
    str15 = ";     // Reset GPIO pin (low during transmission, high normally)\nconst int LED_BUILTIN = 2;    // Built-in LED pin (usually GPIO 2 on ESP32)"

    with in_place.InPlace("main/main.ino") as file:
        skip_gpio_lines = False
        in_setup_function = False
        for line in file:
            # Track if we're in the setup() function
            if line.strip().startswith("void setup()"):
                in_setup_function = True
            elif line.strip() == "}" and in_setup_function:
                in_setup_function = False
                
            if line.startswith('/*MODIFY DATA HERE*/'):
                line = str1 + str2 + str3 + "\n"
                print(line)

            if line.startswith('/*MODIFY CLK_FREQ HERE*/'):
                line = str4 + str5 + str6 + "\n"
                print(line)

            # Update GPIO pin definitions
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
                continue  # Skip existing GPIO pin lines

            # Only replace function call in setup(), not in other functions
            if in_setup_function and line.strip() == "sendResetSequence();":
                line = "  sendDataSequence();\n"
                print("Changed to data transfer mode in setup()")

            file.write(line)

def serial_transfer_data(Data, port_name, timeout=5):
    """
    Transfer data to ESP32 via serial communication (fast method)
    
    Input:
    - Data: 16 bytes of Data in a list
    - port_name: Serial port name (e.g., 'COM3')
    - timeout: Timeout in seconds
    
    Returns:
    - True if successful, False if failed
    """
    try:
        # Open serial connection
        with serial.Serial(port_name, 115200, timeout=timeout) as ser:
            print(f"Serial transfer to {port_name} - Data: {Data}")
            
            # Wait a moment for connection to stabilize
            time.sleep(0.1)
            
            # Clear any existing data in buffers
            ser.reset_input_buffer()
            ser.reset_output_buffer()
            
            # Send data packet: <byte1><byte2>...<byte16>>
            data_packet = b'<' + bytes(Data) + b'>'
            ser.write(data_packet)
            
            print(f"Sent data packet: {data_packet}")
            
            # Wait for response
            start_time = time.time()
            responses = []
            
            while time.time() - start_time < timeout:
                if ser.in_waiting > 0:
                    response = ser.readline().decode('utf-8').strip()
                    if response:
                        responses.append(response)
                        print(f"ESP32 response: {response}")
                        
                        # Check for completion
                        if "TRANSFER_COMPLETE" in response:
                            print("Serial data transfer completed successfully!")
                            return True
                        elif "ERROR" in response:
                            print(f"ESP32 reported error: {response}")
                            return False
                
                time.sleep(0.01)  # Small delay to prevent busy waiting
            
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
    Send reset command to ESP32 via serial communication (fast method)
    
    Input:
    - port_name: Serial port name (e.g., 'COM3')
    - timeout: Timeout in seconds
    
    Returns:
    - True if successful, False if failed
    """
    try:
        # Open serial connection
        with serial.Serial(port_name, 115200, timeout=timeout) as ser:
            print(f"Serial reset to {port_name}")
            
            # Wait a moment for connection to stabilize
            time.sleep(0.1)
            
            # Clear any existing data in buffers
            ser.reset_input_buffer()
            ser.reset_output_buffer()
            
            # Send reset command: R
            ser.write(b'R')
            
            print("Sent reset command: R")
            
            # Wait for response
            start_time = time.time()
            responses = []
            
            while time.time() - start_time < timeout:
                if ser.in_waiting > 0:
                    response = ser.readline().decode('utf-8').strip()
                    if response:
                        responses.append(response)
                        print(f"ESP32 response: {response}")
                        
                        # Check for completion
                        if "RESET_COMPLETE" in response:
                            print("Serial reset completed successfully!")
                            return True
                        elif "ERROR" in response:
                            print(f"ESP32 reported error: {response}")
                            return False
                
                time.sleep(0.01)  # Small delay to prevent busy waiting
            
            print("Timeout waiting for ESP32 reset response")
            return False
            
    except serial.SerialException as e:
        print(f"Serial communication error: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error during serial reset: {e}")
        return False


