def RUN():

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

    #GUI OPERATIONS
    window = sg.Window('GUI ESP32 Configuration', make_layout(), default_element_size=(50, 1), 
                      finalize=True, use_default_focus=False)
    
    # Let window size itself initially
    window.refresh()
    
    # Initialize console with welcome message
    def log_to_console(message):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        console_text = f"[{timestamp}] {message}"
        current_text = window['_CONSOLE_OUTPUT_'].get()
        # Ensure we don't have too much text accumulating
        if len(current_text) > 10000:  # Keep last 10k characters
            current_text = current_text[-8000:]
        
        # Add proper line break
        if current_text:
            new_text = current_text + "\n" + console_text
        else:
            new_text = console_text
            
        window['_CONSOLE_OUTPUT_'].update(new_text)
        window['_CONSOLE_OUTPUT_'].set_vscroll_position(1.0)  # Auto-scroll to bottom
    
    def save_bits_to_file(Data, filename="WRITTEN_TO_CHIP.txt"):
        """
        Save 128 bits (16 bytes) as individual bits to a text file
        
        Input:
        - Data: 16-byte list
        - filename: output file name
        """
        try:
            with open(filename, "w+") as f:
                f.write("128-Bit Configuration (MSB first):\n")
                f.write("=" * 50 + "\n\n")
                
                bit_counter = 0
                for byte_index, byte_val in enumerate(Data):
                    f.write(f"Byte {byte_index + 1} (0x{byte_val:02X}):\n")
                    
                    # Convert byte to 8 bits (MSB first)
                    for bit_pos in range(7, -1, -1):  # 7, 6, 5, 4, 3, 2, 1, 0
                        bit_value = (byte_val >> bit_pos) & 1
                        f.write(f"  Bit {bit_counter:3d}: {bit_value}\n")
                        bit_counter += 1
                    
                    f.write("\n")  # Add spacing between bytes
                
                # Summary section
                f.write("=" * 50 + "\n")
                f.write("SUMMARY:\n")
                f.write(f"Total bits: {bit_counter}\n")
                f.write(f"Bytes: {Data}\n")
                f.write(f"Hex: {' '.join(f'0x{b:02X}' for b in Data)}\n")
                
                # Binary representation in groups of 8
                f.write("Binary (8-bit groups):\n")
                for i, byte_val in enumerate(Data):
                    f.write(f"Byte {i+1:2d}: {byte_val:08b}\n")
                
                # Single line binary (all 128 bits)
                f.write("\nComplete 128-bit string:\n")
                binary_string = ''.join(f'{byte_val:08b}' for byte_val in Data)
                # Split into groups of 32 bits for readability
                for i in range(0, 128, 32):
                    f.write(f"Bits {i:3d}-{i+31:3d}: {binary_string[i:i+32]}\n")
                
        except Exception as e:
            log_to_console(f"Error saving bits to file: {str(e)}")
            return False
        
        return True
    
    # Global variables for thread communication
    upload_in_progress = False
    upload_thread = None
    serial_in_progress = False
    serial_thread = None
    
    def threaded_upload(file_name, port, operation_type="transfer"):
        """
        Run upload in a separate thread to prevent GUI freezing
        """
        global upload_in_progress
        upload_in_progress = True
        
        try:
            if operation_type == "transfer":
                log_to_console("Uploading to ESP32...")
            else:
                log_to_console("Uploading reset to ESP32...")
            
            # Actual upload
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
        Run serial operations in a separate thread to prevent GUI freezing
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

    while True:  #EVENT LOOP : KEEPS THE GUI RUNNING UNTIL "CROSS" IS PRESSED
        event, values = window.read()
        
        # Handle console clear
        if event == '_CLEAR_CONSOLE_':
            window['_CONSOLE_OUTPUT_'].update('')
            log_to_console("Console cleared")
        
        # Handle port refresh
        if event == '_REFRESH_PORTS_':
            port_list, default_port = get_available_ports(logger=log_to_console)
            window['_SERIAL_PORT_'].update(values=port_list, value=default_port)
            log_to_console(f"Ports refreshed ({len(port_list)} found)")
        
        if (event == 'SHOW DICT VALUES') or (event == 'PARAMETERS'):
            print(values)

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
        
        if (event == 'TRANSFER DATA') :
            log_to_console("Starting serial data transfer...")
            
            try:
                # Filter out settings values - only pass control values to An2Bits
                control_values = {}
                settings_keys = ['_CLOCK_FREQ_', '_SERIAL_PORT_', '_CONSOLE_OUTPUT_', '_ADVANCED_FRAME_', '_ADVANCED_COLUMN_', '_REFRESH_PORTS_', '_CLEAR_CONSOLE_']
                
                for key, value in values.items():
                    if key not in settings_keys:
                        control_values[key] = value
                
                bit_dict = An2Bits(control_values)
                Data = RegisterAssignment(bit_dict)  # Data is now a 16-byte list
                selected_port = values.get('_SERIAL_PORT_', 'COM3')
                
                log_to_console(f"Port: {selected_port}, Data: {Data}")
                
                # Save data to file with individual bits
                filename = "WRITTEN_TO_CHIP.txt"
                if save_bits_to_file(Data, filename):
                    log_to_console(f"128-bit config saved to {filename}")
                else:
                    log_to_console(f"Error saving config to {filename}")
                
                # Check if serial operation is already in progress
                if serial_in_progress:
                    log_to_console("Serial operation already in progress, please wait...")
                else:
                    # Start the serial transfer in a separate thread
                    serial_thread = threading.Thread(target=threaded_serial_operation, args=("data_transfer", selected_port, Data))
                    serial_thread.start()
                    
            except Exception as e:
                log_to_console(f"Serial transfer error: {str(e)}")

        if (event == 'UPLOAD DATA') :
            log_to_console("Starting data upload...")
            
            E1 = "OK"
            if(E1 == "OK"):
                try:
                    # Filter out settings values - only pass control values to An2Bits
                    control_values = {}
                    settings_keys = ['_CLOCK_FREQ_', '_SERIAL_PORT_', '_CONSOLE_OUTPUT_', '_ADVANCED_FRAME_', '_ADVANCED_COLUMN_', '_REFRESH_PORTS_', '_CLEAR_CONSOLE_']
                    
                    for key, value in values.items():
                        if key not in settings_keys:
                            control_values[key] = value
                    
                    bit_dict = An2Bits(control_values)
                    Data = RegisterAssignment(bit_dict)  # Data is now a 16-byte list

                    # Get clock frequency from GUI (convert to integer)
                    clk_freq_raw = values.get('_CLOCK_FREQ_', '100')
                    selected_port = values.get('_SERIAL_PORT_', 'COM3')
                    
                    # Convert clock frequency to integer with error handling
                    try:
                        clk_freq_khz = int(clk_freq_raw)
                        if clk_freq_khz < 1 or clk_freq_khz > 10000:
                            log_to_console(f"Clock frequency {clk_freq_khz} kHz out of range (1-10000), using 100 kHz")
                            clk_freq_khz = 100
                    except ValueError as e:
                        log_to_console(f"Invalid clock frequency '{clk_freq_raw}', using default 100 kHz")
                        clk_freq_khz = 100
                    
                    log_to_console(f"Clock: {clk_freq_khz} kHz, Port: {selected_port}")
                    
                    reg2ino(Data, clk_freq_khz)

                    # Save data to file with individual bits
                    filename = "WRITTEN_TO_CHIP.txt"
                    if save_bits_to_file(Data, filename):
                        log_to_console(f"128-bit config saved to {filename}")
                    else:
                        log_to_console(f"Error saving config to {filename}")

                    E2 = "OK"
                    if(E2 == "OK"):
                        # Check if upload is already in progress
                        if upload_in_progress:
                            log_to_console("Upload already in progress, please wait...")
                        else:
                            # Start the upload in a separate thread
                            upload_thread = threading.Thread(target=threaded_upload, args=("main", selected_port, "transfer"))
                            upload_thread.start()
                    else:
                        log_to_console("Upload skipped")
                except Exception as e:
                    log_to_console(f"Upload error: {str(e)}")
            else :
                log_to_console("Upload cancelled")

        if (event == 'RESET'):
            log_to_console("Performing serial reset...")
            try:
                selected_port = values.get('_SERIAL_PORT_', 'COM3')
                log_to_console(f"Port: {selected_port}")
                
                # Check if serial operation is already in progress
                if serial_in_progress:
                    log_to_console("Serial operation already in progress, please wait...")
                else:
                    # Start the serial reset in a separate thread
                    serial_thread = threading.Thread(target=threaded_serial_operation, args=("reset", selected_port))
                    serial_thread.start()
                    
            except Exception as e:
                log_to_console(f"Serial reset error: {str(e)}")
        
        if event in (None, 'Cancel','Exit'):
            window.Close()
            break




