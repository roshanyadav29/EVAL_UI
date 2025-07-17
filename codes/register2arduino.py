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
    # GPIO pin assignments - MUST match main.ino
    clock_pin = 27  # Clock GPIO pin
    data_pin = 25   # Data GPIO pin
    shift_pin = 26  # Shift GPIO pin
    reset_pin = 33  # Reset GPIO pin

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
        for line in file:
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

            # For transfer data, set function call to sendDataSequence()
            if line.strip() == "sendResetSequence();":
                line = "  sendDataSequence();\n"
                print("Changed to timer-based data transfer mode")

            file.write(line)

def reset_only(clk_freq_khz):
    """ 
    Input: 
    - clk_freq_khz: Clock frequency in kHz (500, 1000, 5000, 10000)
    This function generates Arduino code for RESET-only operation (no data transfer)
    """
    # GPIO pin assignments - MUST match main.ino
    clock_pin = 27  # Clock GPIO pin
    data_pin = 25   # Data GPIO pin
    shift_pin = 26  # Shift GPIO pin
    reset_pin = 33  # Reset GPIO pin

    print(f"RESET ONLY - Clock frequency: {clk_freq_khz} kHz")
    print(f"GPIO pins - Clock: {clock_pin}, Data: {data_pin}, Shift: {shift_pin}, Reset: {reset_pin}")

    # Prepare strings for clock frequency
    str4 = "/*MODIFY CLK_FREQ HERE*/ int clk_freq_khz = "
    str5 = str(clk_freq_khz)
    str6 = ";"

    # Prepare strings for GPIO pins
    str7 = "/*MODIFY GPIO PINS HERE*/ \nconst int CLOCK_PIN = "
    str8 = str(clock_pin)
    str9 = ";\nconst int DATA_PIN = "
    str10 = str(data_pin)
    str11 = ";\nconst int SHIFT_PIN = "
    str12 = str(shift_pin)
    str13 = ";\nconst int RESET_PIN = "
    str14 = str(reset_pin)
    str15 = ";\nconst int LED_BUILTIN = 2;    // Built-in LED pin (usually GPIO 2 on ESP32)"

    # For reset-only, set function call to sendResetSequence()
    str16 = "  sendResetSequence();"

    with in_place.InPlace("main/main.ino") as file:
        skip_gpio_lines = False
        for line in file:
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

            # For reset-only, set function call to sendTimerBasedResetOnly()
            if line.strip() == "sendDataSequence();":
                line = str16 + "\n"
                print("Changed to timer-based reset-only mode")

            file.write(line)


