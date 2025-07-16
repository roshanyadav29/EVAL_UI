def RUN():

    import PySimpleGUI as sg
    import tkinter as tk
    from tkinter import filedialog
    from codes.gui_parameters import make_layout, get_available_ports
    from codes.register2arduino import reg2ino, reset_only
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
                      resizable=True, finalize=True, use_default_focus=False)
    
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
    
    # Global variables for thread communication
    upload_in_progress = False
    upload_thread = None
    
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
    
    log_to_console("ESP32 Configuration Tool - Ready")

    while True:  #EVENT LOOP : KEEPS THE GUI RUNNING UNTIL "CROSS" IS PRESSED
        event, values = window.read()
        
        # Handle settings panel toggle
        if event == '_TOGGLE_SETTINGS_':
            current_visibility = window['_ADVANCED_FRAME_'].visible
            window['_ADVANCED_FRAME_'].update(visible=not current_visibility)
            
            # Update button text based on new visibility state
            if not current_visibility:
                # Panel is now opening
                window['_TOGGLE_SETTINGS_'].update(text='<')
            else:
                # Panel is now closing
                window['_TOGGLE_SETTINGS_'].update(text='>')
            
            # Simple refresh for now
            window.refresh()
        
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
            log_to_console("Starting data transfer...")
            
            E1 = "OK"
            if(E1 == "OK"):
                try:
                    # Filter out settings values - only pass control values to An2Bits
                    control_values = {}
                    settings_keys = ['_CLOCK_FREQ_', '_SERIAL_PORT_', '_CONSOLE_OUTPUT_', '_ADVANCED_FRAME_', '_ADVANCED_COLUMN_', '_TOGGLE_SETTINGS_', '_REFRESH_PORTS_', '_CLEAR_CONSOLE_']
                    
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
                    except ValueError as e:
                        log_to_console(f"Clock frequency error, using default 100 kHz")
                        clk_freq_khz = 100
                    
                    log_to_console(f"Clock: {clk_freq_khz} kHz, Port: {selected_port}")
                    
                    reg2ino(Data, clk_freq_khz)

                    filename = "WRITTEN_TO_CHIP.txt"
                    with open(filename, "w+") as f:
                        for i, val in enumerate(Data):
                            f.write(f"Byte {i+1}: {val}\n")
                    log_to_console(f"Config saved to {filename}")

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
                    log_to_console(f"Transfer error: {str(e)}")
            else :
                log_to_console("Transfer cancelled")

        if (event == 'RESET'):
            log_to_console("Performing reset...")
            try:
                # Get clock frequency from GUI
                clk_freq_raw = values.get('_CLOCK_FREQ_', '100')
                selected_port = values.get('_SERIAL_PORT_', 'COM3')
                
                # Convert clock frequency to integer with error handling
                try:
                    clk_freq_khz = int(clk_freq_raw)
                except ValueError:
                    clk_freq_khz = 100
                
                log_to_console(f"Clock: {clk_freq_khz} kHz, Port: {selected_port}")
                
                reset_only(clk_freq_khz)
                
                E2 = "OK"
                if(E2 == "OK"):
                    # Check if upload is already in progress
                    if upload_in_progress:
                        log_to_console("Upload already in progress, please wait...")
                    else:
                        # Start the upload in a separate thread
                        upload_thread = threading.Thread(target=threaded_upload, args=("main", selected_port, "reset"))
                        upload_thread.start()
                else:
                    log_to_console("Reset upload skipped")
            except Exception as e:
                log_to_console(f"Reset error: {str(e)}")
        
        if event in (None, 'Cancel','Exit'):
            window.Close()
            break




