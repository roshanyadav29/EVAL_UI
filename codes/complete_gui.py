"""
ESP32 Configuration GUI - Main Application Module

This module provides the main GUI application for configuring ESP32-based chip control.
It handles user interactions, data processing, and communication with the ESP32 device
through both serial transfer and firmware upload methods.

Key Features:
- Real-time configuration of 128-bit register values
- Dual transfer modes: Serial (fast) and Upload (permanent)
- Threaded operations to prevent GUI freezing
- State management for configuration presets
- Advanced settings with clock frequency control
"""

def RUN():
    """
    Main application entry point - initializes and runs the GUI event loop.
    
    This function sets up the PySimpleGUI interface, initializes helper functions,
    and manages the main event loop for user interactions. It handles all GUI
    events including data transfer, upload operations, and state management.
    """

    import PySimpleGUI as sg
    import tkinter as tk
    from tkinter import filedialog
    from codes.gui_parameters import make_layout, get_available_ports
    from codes.register2arduino import reg2ino, serial_transfer_data, serial_reset
    from codes.register_assignment import RegisterAssignment
    from codes.Analog2Bits import An2Bits
    from codes.upload2Arduino import upload

    import os
    import ast
    import datetime
    import traceback
    import threading
    import time

    # Initialize main GUI window
    window = sg.Window('GUI ESP32 Configuration', make_layout(), default_element_size=(50, 1), 
                      finalize=True, use_default_focus=False)
    
    window.refresh()  # Let window size itself initially
    
    def log_to_console(message):
        """
        Add timestamped message to the console output with auto-scroll.
        
        Features:
        - Automatic timestamping
        - Text length management (prevents memory issues)
        - Auto-scroll to bottom for latest messages
        
        Args:
            message (str): Message to display in console
        """
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        console_text = f"[{timestamp}] {message}"
        current_text = window['_CONSOLE_OUTPUT_'].get()
        
        # Prevent excessive memory usage by trimming old text
        if len(current_text) > 10000:  # Keep last 10k characters
            current_text = current_text[-8000:]
        
        # Add proper line formatting
        if current_text:
            new_text = current_text + "\n" + console_text
        else:
            new_text = console_text
            
        window['_CONSOLE_OUTPUT_'].update(new_text)
        window['_CONSOLE_OUTPUT_'].set_vscroll_position(1.0)  # Auto-scroll to bottom
    
    def save_bits_to_file(Data, filename="WRITTEN_TO_CHIP.txt"):
        """
        Export 128-bit configuration to CSV format for easy editing.
        
        Creates a simple CSV file with:
        - Bit Number: Sequential from 1 to 128
        - PBit: Position bit from 127 down to 0 (MSB first)
        - Value: 0 or 1
        
        Args:
            Data (list): 16-byte list representing 128-bit configuration
            filename (str): Output filename (default: "WRITTEN_TO_CHIP.txt")
            
        Returns:
            bool: True if successful, False if error occurred
        """
        try:
            with open(filename, "w+") as f:
                # Write CSV header
                f.write("Bit Number,PBit,Value\n")
                
                bit_number = 1
                for byte_index, byte_val in enumerate(Data):
                    # Convert byte to 8 bits (MSB first)
                    for bit_pos in range(7, -1, -1):  # 7, 6, 5, 4, 3, 2, 1, 0
                        bit_value = (byte_val >> bit_pos) & 1
                        pbit = 127 - (bit_number - 1)  # PBit starts at 127 and decreases
                        f.write(f"{bit_number},{pbit},{bit_value}\n")
                        bit_number += 1
            
        except Exception as e:
            log_to_console(f"Error saving bits to file: {str(e)}")
            return False
        
        return True
    
    # Thread management for non-blocking operations
    upload_in_progress = False
    upload_thread = None
    serial_in_progress = False
    serial_thread = None
    
    def threaded_upload(file_name, port, operation_type="transfer"):
        """
        Execute ESP32 firmware upload in separate thread to prevent GUI freezing.
        
        Uses Arduino CLI to compile and upload firmware with embedded configuration.
        This is the "permanent" method that programs the ESP32 with new firmware.
        
        Args:
            file_name (str): Arduino project directory name
            port (str): Serial port for ESP32 communication
            operation_type (str): Type of operation for logging purposes
        """
        global upload_in_progress
        upload_in_progress = True
        
        try:
            if operation_type == "transfer":
                log_to_console("Uploading to ESP32...")
            else:
                log_to_console("Uploading reset to ESP32...")
            
            # Execute Arduino CLI upload process
            result = upload(file_name, port)
            
            if result:
                if operation_type == "transfer":
                    log_to_console("Upload successful!")
                else:
                    log_to_console("Reset successful!")
            else:
                if operation_type == "transfer":
                    log_to_console("Upload failed - check connection")
                else:
                    log_to_console("Reset failed - check connection")
        
        except Exception as e:
            log_to_console(f"Upload error: {str(e)}")
        
        finally:
            upload_in_progress = False
    
    def threaded_serial_operation(operation_type, port, data=None):
        """
        Execute serial communication in separate thread to prevent GUI freezing.
        
        Handles fast serial transfer of configuration data to already-programmed ESP32.
        This is the "temporary" method for testing configurations quickly.
        
        Args:
            operation_type (str): "data_transfer" or "reset"
            port (str): Serial port for communication
            data (list, optional): 16-byte configuration data for transfer
        """
        global serial_in_progress
        serial_in_progress = True
        
        try:
            if operation_type == "data_transfer":
                log_to_console("Serial data transfer...")
                result = serial_transfer_data(data, port)
                if result:
                    log_to_console("Serial data transfer successful!")
                else:
                    log_to_console("Serial data transfer failed")
            elif operation_type == "reset":
                log_to_console("Serial reset...")
                result = serial_reset(port)
                if result:
                    log_to_console("Serial reset successful!")
                else:
                    log_to_console("Serial reset failed")
        
        except Exception as e:
            log_to_console(f"Serial operation error: {str(e)}")
        
        finally:
            serial_in_progress = False
    
    log_to_console("ESP32 Configuration Tool - Ready")

    # ============================================================================
    # MAIN EVENT LOOP - Process GUI events until window is closed
    # ============================================================================
    while True:
        event, values = window.read()
        
        # ========================================
        # Advanced Settings Panel Events
        # ========================================
        
        if event == '_CLEAR_CONSOLE_':
            window['_CONSOLE_OUTPUT_'].update('')
            log_to_console("Console cleared")
        
        if event == '_REFRESH_PORTS_':
            port_list, default_port = get_available_ports(logger=log_to_console)
            window['_SERIAL_PORT_'].update(values=port_list, value=default_port)
            log_to_console(f"Ports refreshed ({len(port_list)} found)")
        
        # ========================================
        # Development/Debug Events
        # ========================================
        
        if (event == 'SHOW DICT VALUES') or (event == 'PARAMETERS'):
            print(values)  # Debug: Print all GUI values to console

        # ========================================
        # State Management Events
        # ========================================
        
        if (event == 'LOAD_STATE'):
            loadfile = filedialog.askopenfilename()
            if(loadfile):
                try:
                    f = open(loadfile)
                    state = f.read()
                    state_dict = ast.literal_eval(state)
                    f.close()
                    for key in state_dict:
                        elem = window[key] if key in window.AllKeysDict else None
                        if elem is not None:
                            elem.update(state_dict[key])
                    log_to_console(f"Config loaded: {os.path.basename(loadfile)}")
                except Exception as e:
                    log_to_console(f"Load error: {str(e)}")
            else:
                log_to_console("Load cancelled")

        if(event == 'SAVE_STATE'):
            savefile = filedialog.asksaveasfilename(initialdir = "/",title = "Select file",defaultextension = '.state')
            if(savefile):
                try:
                    f = open(savefile,"w+")
                    f.write(str(values))        
                    f.close()
                    log_to_console(f"Config saved: {os.path.basename(savefile)}")
                except Exception as e:
                    log_to_console(f"Save error: {str(e)}")
            else:
                log_to_console("Save cancelled")
        
        # ========================================
        # Data Transfer Operations
        # ========================================
        
        if (event == 'TRANSFER DATA'):
            """
            TRANSFER DATA: Fast serial method for testing configurations.
            Sends configuration directly to already-programmed ESP32 via serial protocol.
            Changes are temporary and lost on ESP32 reset.
            """
            log_to_console("Starting serial data transfer...")
            
            try:
                # Extract only chip configuration values (exclude GUI settings)
                control_values = {}
                settings_keys = ['_CLOCK_FREQ_', '_SERIAL_PORT_', '_CONSOLE_OUTPUT_', '_ADVANCED_FRAME_', '_ADVANCED_COLUMN_', '_REFRESH_PORTS_', '_CLEAR_CONSOLE_']
                
                for key, value in values.items():
                    if key not in settings_keys:
                        control_values[key] = value
                
                # Process configuration: GUI values → integers → 128-bit register
                bit_dict = An2Bits(control_values)
                Data = RegisterAssignment(bit_dict)  # Returns 16-byte list
                selected_port = values.get('_SERIAL_PORT_', 'COM3')
                
                log_to_console(f"Port: {selected_port}, Data: {Data}")
                
                # Generate detailed configuration file for analysis
                filename = "WRITTEN_TO_CHIP.txt"
                if save_bits_to_file(Data, filename):
                    log_to_console(f"128-bit config saved to {filename}")
                else:
                    log_to_console(f"Error saving config to {filename}")
                
                # Execute serial transfer in background thread
                if serial_in_progress:
                    log_to_console("Serial operation already in progress, please wait...")
                else:
                    serial_thread = threading.Thread(target=threaded_serial_operation, args=("data_transfer", selected_port, Data))
                    serial_thread.start()
                    
            except Exception as e:
                log_to_console(f"Serial transfer error: {str(e)}")

        if (event == 'UPLOAD DATA'):
            """
            UPLOAD DATA: Permanent firmware method for production configurations.
            Embeds configuration into ESP32 firmware and uploads via Arduino CLI.
            Changes are permanent and survive ESP32 reset.
            """
            log_to_console("Starting data upload...")
            
            try:
                # Extract only chip configuration values (exclude GUI settings)
                control_values = {}
                settings_keys = ['_CLOCK_FREQ_', '_SERIAL_PORT_', '_CONSOLE_OUTPUT_', '_ADVANCED_FRAME_', '_ADVANCED_COLUMN_', '_REFRESH_PORTS_', '_CLEAR_CONSOLE_']
                
                for key, value in values.items():
                    if key not in settings_keys:
                        control_values[key] = value
                
                # Process configuration: GUI values → integers → 128-bit register
                bit_dict = An2Bits(control_values)
                Data = RegisterAssignment(bit_dict)  # Returns 16-byte list

                # Extract and validate clock frequency setting
                clk_freq_raw = values.get('_CLOCK_FREQ_', '100')
                selected_port = values.get('_SERIAL_PORT_', 'COM3')
                
                try:
                    clk_freq_khz = int(clk_freq_raw)
                    if clk_freq_khz < 1 or clk_freq_khz > 10000:
                        log_to_console(f"Clock frequency {clk_freq_khz} kHz out of range (1-10000), using 100 kHz")
                        clk_freq_khz = 100
                except ValueError as e:
                    log_to_console(f"Invalid clock frequency '{clk_freq_raw}', using default 100 kHz")
                    clk_freq_khz = 100
                
                log_to_console(f"Clock: {clk_freq_khz} kHz, Port: {selected_port}")
                
                # Embed configuration into Arduino firmware
                reg2ino(Data, clk_freq_khz)

                # Generate detailed configuration file for analysis
                filename = "WRITTEN_TO_CHIP.txt"
                if save_bits_to_file(Data, filename):
                    log_to_console(f"128-bit config saved to {filename}")
                else:
                    log_to_console(f"Error saving config to {filename}")

                # Execute firmware upload in background thread
                if upload_in_progress:
                    log_to_console("Upload already in progress, please wait...")
                else:
                    upload_thread = threading.Thread(target=threaded_upload, args=("main", selected_port, "transfer"))
                    upload_thread.start()
                    
            except Exception as e:
                log_to_console(f"Upload error: {str(e)}")

        if (event == 'RESET'):
            """
            RESET: Send reset signal to target chip via serial protocol.
            Useful for initializing or clearing the target chip state.
            """
            log_to_console("Performing serial reset...")
            try:
                selected_port = values.get('_SERIAL_PORT_', 'COM3')
                log_to_console(f"Port: {selected_port}")
                
                # Execute reset in background thread
                if serial_in_progress:
                    log_to_console("Serial operation already in progress, please wait...")
                else:
                    serial_thread = threading.Thread(target=threaded_serial_operation, args=("reset", selected_port))
                    serial_thread.start()
                    
            except Exception as e:
                log_to_console(f"Serial reset error: {str(e)}")
        
        # ========================================
        # Application Exit
        # ========================================
        
        if event in (None, 'Cancel','Exit'):
            window.Close()
            break




