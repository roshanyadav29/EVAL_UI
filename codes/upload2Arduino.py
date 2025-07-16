import os
import serial.tools.list_ports


def upload(file, port=None):
    """
    Purpose: Upload an Arduino file to ESP32 using Arduino-CLI.
    Input: Arduino file name (string), optional port (string)
    Output: Boolean indicating success/failure
    Default Port: Auto-detected (fallback to "COM3" on Windows)
    """

    # Use provided port or auto-detect ESP32's port
    if port:
        PORT = port
    else:
        PORT = "COM3"  # Default fallback port (Windows)

        ports = list(serial.tools.list_ports.comports())
        for p in ports:
            if "Silicon Labs CP210x" in str(p) or "CP210x" in str(p):  # ESP32 with CP210x driver
                PORT = str(p.device)
                break  # Stop once we find the correct port

    # Get the current working directory (handles different OS path formats)
    cwd = os.getcwd()
    file_path = os.path.join(cwd, file)  # Cross-platform path handling

    # Compile the Arduino sketch for ESP32
    compile_cmd = f'arduino-cli compile --fqbn esp32:esp32:esp32 -v "{file_path}"'
    upload_cmd = f'arduino-cli upload -p {PORT} --fqbn esp32:esp32:esp32 -v "{file_path}"'

    print(f"Using port: {PORT}")
    print("Compiling the ESP32 code...")
    compile_status = os.system(compile_cmd)

    if compile_status == 0:  # Check if compilation was successful
        print("Compilation successful. Uploading to ESP32...")
        upload_status = os.system(upload_cmd)
        if upload_status == 0:
            print("Program successfully uploaded to ESP32!")
            return True
        else:
            print("Error: Upload failed. Check your ESP32 connection and try again.")
            return False
    else:
        print("Error: Compilation failed. Please check your code for errors.")
        return False
