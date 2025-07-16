def RUN():

    import PySimpleGUI as sg
    import tkinter as tk
    from tkinter import filedialog
    from codes.gui_parameters import make_layout
    from codes.register2arduino import reg2ino, reset_only
    from codes.register_assignment import RegisterAssignment
    from codes.Analog2Bits import An2Bits
    from codes.upload2Arduino import upload

    import os
    import ast

    #GUI OPERATIONS
    window = sg.Window('GUI', make_layout(), default_element_size=(50, 1), resizable=True, finalize=True)

    while True:  #EVENT LOOP : KEEPS THE GUI RUNNING UNTIL "CROSS" IS PRESSED
        event, values = window.read()
        if (event == 'SHOW DICT VALUES') or (event == 'PARAMETERS'):
            print(values)

        if (event == 'LOAD_STATE'):
            loadfile = filedialog.askopenfilename()
            if(loadfile):
                f = open(loadfile)
                state = f.read()
                state_dict = ast.literal_eval(state)
                f.close()
                for key in state_dict:
                    elem = window[key] if key in window.AllKeysDict else None
                    if elem is not None:
                        elem.update(state_dict[key])
            else:
                pass

        if(event == 'SAVE_STATE'):
            savefile = filedialog.asksaveasfilename(initialdir = "/",title = "Select file",defaultextension = '.state')
            if(savefile):
                f = open(savefile,"w+")
                f.write(str(values))        
                f.close()
        
        if (event == 'TRANSFER DATA') :
            E1 = "OK"
            if(E1 == "OK"):
                bit_dict = An2Bits(values)
                Data = RegisterAssignment(bit_dict)  # Data is now a 16-byte list

                clk_freq_khz = 500  # Default clock frequency in kHz
                reg2ino(Data, clk_freq_khz)

                filename = "WRITTEN_TO_CHIP.txt"
                with open(filename, "w+") as f:
                    for i, val in enumerate(Data):
                        f.write(f"Byte {i+1}: {val}\n")

                E2 = "OK"
                if(E2 == "OK"):
                    upload("main")
                else:
                    pass
            else :
                pass

        if (event == 'RESET'):
            clk_freq_khz = 500  # Default clock frequency in kHz
            reset_only(clk_freq_khz)
            
            E2 = "OK"
            if(E2 == "OK"):
                upload("main")
            else:
                pass
        
        if event in (None, 'Cancel','Exit'):
            window.Close()
            break




