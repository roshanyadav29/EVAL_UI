"""
For MASTER part of the Custom Serial Protocol
Writes the register values into the .ino file
File location : main/main.ino
"""

import in_place

def reg2ino(Data, clk_freq_khz):
    """ 
    Input: 
    - Data: 16 bytes of Data in a list 
    - clk_freq_khz: Clock frequency in kHz (500, 1000, 5000, 10000)
    """
    # GPIO pin assignments
    clock_pin = 13  # Clock GPIO pin
    data_pin = 11   # Data GPIO pin
    shift_pin = 9   # Shift GPIO pin
    reset_pin = 12  # Reset GPIO pin
    
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
    str15 = ";     // Reset GPIO pin (low during transmission, high normally)"

    with in_place.InPlace("main/main.ino") as file:
        for line in file:
            if line.startswith('/*MODIFY DATA HERE*/'):
                line = str1 + str2 + str3 + "\n"
                print(line)

            if line.startswith('/*MODIFY CLK_FREQ HERE*/'):
                line = str4 + str5 + str6 + "\n"
                print(line)

            # For transfer data, set function call to sendSerialData()
            if line.strip() == "sendResetOnly();":
                line = "  sendSerialData();\n"
                print("Changed to full data transfer mode")

            file.write(line)

def reset_only(clk_freq_khz):
    """ 
    Input: 
    - clk_freq_khz: Clock frequency in kHz (500, 1000, 5000, 10000)
    This function generates Arduino code for RESET-only operation (no data transfer)
    """
    # GPIO pin assignments
    clock_pin = 13  # Clock GPIO pin
    data_pin = 11   # Data GPIO pin
    shift_pin = 9   # Shift GPIO pin
    reset_pin = 12  # Reset GPIO pin
    
    print(f"RESET ONLY - Clock frequency: {clk_freq_khz} kHz")
    print(f"GPIO pins - Clock: {clock_pin}, Data: {data_pin}, Shift: {shift_pin}, Reset: {reset_pin}")

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
    str15 = ";     // Reset GPIO pin (low during transmission, high normally)"

    # For reset-only, set function call to sendResetOnly()
    str16 = "  sendResetOnly();"

    with in_place.InPlace("main/main.ino") as file:
        for line in file:
            if line.startswith('/*MODIFY CLK_FREQ HERE*/'):
                line = str4 + str5 + str6 + "\n"
                print(line)

            # For reset-only, set function call to sendResetOnly()
            if line.strip() == "sendSerialData();":
                line = str16 + "\n"
                print("Changed to reset-only mode")

            file.write(line)


