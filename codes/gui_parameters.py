"""
GUI Layout Parameters and Components Module

Defines the PySimpleGUI layout structure for ESP32 chip configuration interface.
This module creates organized parameter sections corresponding to the 128-bit register
mapping, including enable controls, delay settings, current controls, and filters.

Key Layout Sections:
- CSH EN: Channel select controls (8 bits)
- PI EN: Pixel interface enables (8 bits) 
- PI DELAY CTRL: Delay control values (8 × 7-bit fields)
- PI CTRL: DC, capacitor, and sum delay controls
- CURRENT CTRL: Current control for various blocks
- ENABLES & RESET: Digital enable controls
- FILTER: Low-pass and band-pass filter controls
- TEST NETWORK: Test multiplexer and address controls
- ADVANCED SETTINGS: Clock frequency, serial port, console
"""

import PySimpleGUI as sg
import serial.tools.list_ports

sg.theme('DefaultNoMoreNagging')  # Suppress PySimpleGUI theme warnings

def get_available_ports(logger=None):
    """
    Detect available serial ports with ESP32 device auto-detection.
    
    Automatically identifies Silicon Labs CP210x USB-to-UART bridges commonly
    used on ESP32 development boards for optimal default port selection.
    
    Args:
        logger (function, optional): Logging function for status messages
    
    Returns:
        tuple: (port_list, default_port)
            - port_list: List of all available COM ports
            - default_port: Best guess for ESP32 port (CP210x preferred)
    """
    if logger is None:
        logger = print
    
    ports = list(serial.tools.list_ports.comports())
    port_list = []
    default_port = "COM3"  # Windows fallback
    cp210x_found = False
    
    for p in ports:
        port_list.append(p.device)
        
        # Multi-field search for Silicon Labs CP210x devices (common ESP32 USB-UART)
        desc_str = str(p.description).lower()
        manuf_str = str(p.manufacturer).lower() if p.manufacturer else ""
        product_str = str(p.product).lower() if p.product else ""
        
        if ("silicon labs" in desc_str) or ("cp210x" in desc_str) or ("cp2102" in desc_str) or \
           ("silicon labs" in manuf_str) or ("cp210x" in manuf_str) or ("cp2102" in manuf_str) or \
           ("silicon labs" in product_str) or ("cp210x" in product_str) or ("cp2102" in product_str):
            default_port = p.device
            cp210x_found = True
    
    if cp210x_found:
        logger(f"CP210x device found on {default_port}")
    else:
        logger(f"Using fallback port {default_port}")
    
    return port_list, default_port

# ============================================================================
# GUI LAYOUT COMPONENT DEFINITIONS
# ============================================================================
# Each section corresponds to specific bit fields in the 128-bit register.
# Layout components are organized to match the register assignment mapping.

# CSH EN Controls (Bits 127-120): 8 individual enable checkboxes
csh_en_layout = [
    [sg.CB(f'CSH EN {i}', key=f'_CSH_EN_{i}_', default=False, font='Any 8', pad=(1,1), expand_x=True)] for i in range(1, 9)
]

# PI EN Controls (Bits 119-112): 8 pixel interface enable checkboxes
pi_en_layout = [
    [sg.CB(f'PI EN {i}', key=f'_PI_EN_{i}_', default=False, font='Any 8', pad=(1,1), expand_x=True)] for i in range(1, 9)
]

# PI DELAY Controls (Multiple 7-bit fields): Delay settings for 8 PI channels (0-127 range)
pi_delay_ctrl_layout = [
    [sg.Text(f'PI DELAY CTRL {i}', font='Any 8', expand_x=True), 
     sg.Combo([str(j) for j in range(128)], default_value='0', key=f'_PI_DELAY_CTRL{i}_', font='Any 8', readonly=False, expand_x=True)] for i in range(1, 9)
]

# PI Control Settings: Additional PI configuration parameters
pi_sum_delay_ctrl_layout = [
    [sg.Text('SUM DELAY CTRL', font='Any 8', justification='left', expand_x=True), 
     sg.Combo([str(i) for i in range(128)], default_value='0', key='_PI_SUM_DELAY_CTRL_', font='Any 8', readonly=False, expand_x=True)]
]

pi_dc_ctrl_layout = [
    [sg.Text('PI DC CTRL', font='Any 8', justification='left', expand_x=True), 
     sg.Combo([str(i) for i in range(8)], default_value='0', key='_PI_DC_CTRL_', font='Any 8', readonly=False, expand_x=True)]
]

pi_cap_ctrl_layout = [
    [sg.Text('PI CAP CTRL', font='Any 8', justification='left', expand_x=True), 
     sg.Combo([str(i) for i in range(32)], default_value='0', key='_PI_CAP_CTRL_', font='Any 8', readonly=False, expand_x=True)]
]

# Current Control Settings: 3-bit current control for different circuit blocks (0-7 range)
current_ctrl_layout = [
    [sg.Text('BGR OUT CTRL', font='Any 8', justification='left', expand_x=True), 
     sg.Combo([str(i) for i in range(8)], default_value='0', key='_BGR_OUT_CTRL_', font='Any 8', readonly=False, expand_x=True)],
    [sg.Text('CSH ICTRL', font='Any 8', justification='left', expand_x=True), 
     sg.Combo([str(i) for i in range(8)], default_value='0', key='_CSH_ICTRL_', font='Any 8', readonly=False, expand_x=True)],
    [sg.Text('PI ICTRL', font='Any 8', justification='left', expand_x=True), 
     sg.Combo([str(i) for i in range(8)], default_value='0', key='_PI_ICTRL_', font='Any 8', readonly=False, expand_x=True)],
    [sg.Text('DEMOD ICTRL', font='Any 8', justification='left', expand_x=True), 
     sg.Combo([str(i) for i in range(8)], default_value='0', key='_DEMOD_ICTRL_', font='Any 8', readonly=False, expand_x=True)],
    [sg.Text('BUFF ICTRL', font='Any 8', justification='left', expand_x=True), 
     sg.Combo([str(i) for i in range(8)], default_value='0', key='_BUFF_ICTRL_', font='Any 8', readonly=False, expand_x=True)],
]

# Digital Enable Controls: Various system enable signals organized in columns for space efficiency
enables_reset_layout = [
    [
        sg.Column([
            [sg.CB('CSH VCM EN', key='_CSH_VCM_EN_', default=False, font='Any 8', expand_x=True)],
            [sg.CB('SUM PI EN', key='_SUM_PI_EN_', default=False, font='Any 8', expand_x=True)],
            [sg.CB('BUFF EN', key='_BUFF_EN_', default=False, font='Any 8', expand_x=True)]
        ], vertical_alignment='top', expand_x=True),
        sg.Column([
            [sg.CB('IQ DIV EN', key='_IQ_DIV_EN_', default=False, font='Any 8', expand_x=True)],
            [sg.CB('IQ DIV RST', key='_IQ_DIV_RST_', default=False, font='Any 8', expand_x=True)]
        ], vertical_alignment='top', expand_x=True),
        sg.Column([
            [sg.CB('DEMOD ICH EN', key='_DEMOD_ICH_EN_', default=False, font='Any 8', expand_x=True)],
            [sg.CB('DEMOD QCH EN', key='_DEMOD_QCH_EN_', default=False, font='Any 8', expand_x=True)]
        ], vertical_alignment='top', expand_x=True)
    ]
]

# Filter Controls: Low-pass and band-pass filter enable settings
filter_layout = [
    [sg.CB('LPF EN', key='_LPF_EN_', default=False, font='Any 8', expand_x=True)],
    [sg.CB('LPF SAMPLE EN', key='_LPF_SAMP_EN_', default=False, font='Any 8', expand_x=True)],
    [sg.CB('BPF EN', key='_BPF_EN_', default=False, font='Any 8', expand_x=True)],
    [sg.CB('BPF SAMPLE EN', key='_BPF_SAMP_EN_', default=False, font='Any 8', expand_x=True)],
]

# Test Network Controls: Test multiplexer and address selection (4-bit fields, 0-15 range)
test_network_layout = [
    [sg.Text('TEST ADD', font='Any 8', justification='center', expand_x=True), 
     sg.Combo([str(i) for i in range(16)], default_value='0', key='_TEST_ADD_', font='Any 8', readonly=False, expand_x=True),
     sg.Text('TMUX SEL', font='Any 8', justification='center', expand_x=True), 
     sg.Combo([str(i) for i in range(16)], default_value='0', key='_TMUX_SEL_', font='Any 8', readonly=False, expand_x=True)]
]

# ============================================================================
# ADVANCED SETTINGS PANEL
# ============================================================================

def make_advanced_settings_panel():
    """
    Create the advanced settings panel with system-level configurations.
    
    Includes:
    - Clock frequency selection (50kHz - 2MHz)
    - Serial port auto-detection and selection
    - Real-time console output with dark theme
    - Port refresh and console clear utilities
    
    Returns:
        list: PySimpleGUI layout for advanced settings frame
    """
    port_list, default_port = get_available_ports()
    
    # Available clock frequencies for SPI communication (in kHz)
    clock_freq_options = ['50', '100', '200', '500', '1000', '2000']
    
    settings_layout = [
        [sg.Text('CLOCK FREQUENCY (KHZ)', font='Any 8', expand_x=True), 
         sg.Combo(clock_freq_options, default_value='100', key='_CLOCK_FREQ_', font='Any 8', readonly=False, expand_x=True)],
        [sg.Text('SERIAL PORT', font='Any 8', expand_x=True), 
         sg.Combo(port_list, default_value=default_port, key='_SERIAL_PORT_', font='Any 8', readonly=True, expand_x=True)],
        [sg.Text('CONSOLE OUTPUT', font='Any 8', expand_x=True),
         sg.Push(),
         sg.Button('REFRESH', key='_REFRESH_PORTS_', font='Any 8', size=(8,1)),
         sg.Button('CLEAR', key='_CLEAR_CONSOLE_', font='Any 8', size=(8,1))],
        [sg.Multiline('', key='_CONSOLE_OUTPUT_', font='Courier 8', size=(45, 18), 
                     expand_x=True, expand_y=False, disabled=True, autoscroll=True, 
                     background_color='#1e1e1e', text_color='#d4d4d4', write_only=False,
                     reroute_stdout=False, reroute_stderr=False, echo_stdout_stderr=False)]
    ]
    
    return [
        [sg.Frame('ADVANCED SETTINGS', settings_layout, font='Any 8', pad=(5,5), 
                 expand_x=False, expand_y=False, element_justification='left', 
                 key='_ADVANCED_FRAME_', visible=True)]
    ]

# ============================================================================
# MAIN LAYOUT ASSEMBLY
# ============================================================================

def make_layout():
    """
    Assemble the complete GUI layout with all parameter sections and controls.
    
    Layout Structure:
    - Left Column: CSH/PI enables, delay controls, system enables, test network
    - Right Column: PI controls, current controls, filter settings
    - Advanced Panel: Clock/port settings, console output
    - Bottom Row: Main action buttons (Reset, Transfer, Upload, Save/Load)
    
    Returns:
        list: Complete PySimpleGUI layout structure
    """
    layout = [
        [
            # Left section: Primary chip configuration controls
            sg.Column([
                [
                    sg.Frame('CSH EN', csh_en_layout, font='Any 8', pad=(1,1), expand_x=True, expand_y=True, element_justification='center'),
                    sg.Frame('PI EN', pi_en_layout, font='Any 8', pad=(1,1), expand_x=True, expand_y=True, element_justification='center'),
                    sg.Frame('PI DELAY CTRL', pi_delay_ctrl_layout, font='Any 8', pad=(1,1), expand_x=True, expand_y=True, element_justification='center')
                ],
                [sg.Frame('ENABLES & RESET', enables_reset_layout, font='Any 8', pad=(1,1), expand_x=True, expand_y=True, element_justification='center')],
                [sg.Frame('TEST NETWORK', test_network_layout, font='Any 8', pad=(1,1), expand_x=True, expand_y=True, element_justification='center')]
            ], vertical_alignment='top', pad=(1,1), element_justification='left', expand_x=True, expand_y=True),
            
            # Right section: Secondary configuration controls
            sg.Column([
                [sg.Frame('PI CTRL', [
                    pi_sum_delay_ctrl_layout[0],
                    pi_dc_ctrl_layout[0],
                    pi_cap_ctrl_layout[0]
                ], font='Any 8', pad=(1,1), expand_x=True, expand_y=True, element_justification='center')],
                [sg.Frame('CURRENT CTRL', current_ctrl_layout, font='Any 8', pad=(1,1), expand_x=True, expand_y=True, element_justification='center')],
                [sg.Frame('FILTER', filter_layout, font='Any 8', pad=(1,1), expand_x=True, expand_y=True, element_justification='center')],
            ], vertical_alignment='top', pad=(1,1), expand_x=True, expand_y=True),
            
            # Advanced settings panel: System configuration and monitoring
            sg.Column(make_advanced_settings_panel(), vertical_alignment='top', pad=(5,1), 
                     expand_x=False, expand_y=True, key='_ADVANCED_COLUMN_')
        ],
        [
            # Main action buttons: Core application operations
            sg.Push(),
            sg.Button('RESET', size=(8,2), pad=(5,5)),
            sg.Button('TRANSFER DATA', key='TRANSFER DATA', size=(15,2), pad=(5,5)),
            sg.Button('UPLOAD DATA', key='UPLOAD DATA', size=(12,2), pad=(5,5)),
            sg.Button('SAVE STATE', key='SAVE_STATE', size=(12,2), pad=(5,5)),
            sg.Button('LOAD STATE', key='LOAD_STATE', size=(12,2), pad=(5,5)),
            sg.Push(),
        ],
    ]
    return layout

