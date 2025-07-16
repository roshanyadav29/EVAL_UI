import PySimpleGUI as sg
import serial.tools.list_ports
sg.theme('DefaultNoMoreNagging')
# sg.theme('TanBlue')

# Function to get available COM ports
def get_available_ports(logger=None):
    """
    Get available COM ports and detect Silicon Labs CP210x devices.
    
    Args:
        logger: Optional logging function to use instead of print
    
    Returns:
        tuple: (port_list, default_port)
    """
    if logger is None:
        logger = print  # Use print as default
    
    ports = list(serial.tools.list_ports.comports())
    port_list = []
    default_port = "COM3"  # fallback
    cp210x_found = False
    
    for p in ports:
        port_list.append(p.device)
        
        # Check for Silicon Labs CP210x USB-to-UART bridge (common on ESP32 boards)
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

# --- Logical frames for new chip ---

# 1. CSH EN (8 ticks) - vertical layout with reduced spacing
csh_en_layout = [
    [sg.CB(f'CSH EN {i}', key=f'_CSH_EN_{i}_', default=False, font='Any 8', pad=(1,1), expand_x=True)] for i in range(1, 9)
]

# 2. PI EN (8 ticks) - vertical layout with reduced spacing  
pi_en_layout = [
    [sg.CB(f'PI EN {i}', key=f'_PI_EN_{i}_', default=False, font='Any 8', pad=(1,1), expand_x=True)] for i in range(1, 9)
]

# 5. PI DELAY CTRLs (1-8, 0-127, 7 bits each) - vertical layout with editable dropdowns
pi_delay_ctrl_layout = [
    [sg.Text(f'PI DELAY CTRL {i}', font='Any 8', expand_x=True), 
     sg.Combo([str(j) for j in range(128)], default_value='0', key=f'_PI_DELAY_CTRL{i}_', font='Any 8', readonly=False, expand_x=True)] for i in range(1, 9)
]

# 6. PI SUM DELAY CTRL (0-127, 7 bits) - now in PI CTRL section with editable dropdown
pi_sum_delay_ctrl_layout = [
    [sg.Text('SUM DELAY CTRL', font='Any 8', justification='left', expand_x=True), 
     sg.Combo([str(i) for i in range(128)], default_value='0', key='_PI_SUM_DELAY_CTRL_', font='Any 8', readonly=False, expand_x=True)]
]

# 3. PI DC CTRL (0-7, 3 bits) - now in PI CTRL section with editable dropdown
pi_dc_ctrl_layout = [
    [sg.Text('PI DC CTRL', font='Any 8', justification='left', expand_x=True), 
     sg.Combo([str(i) for i in range(8)], default_value='0', key='_PI_DC_CTRL_', font='Any 8', readonly=False, expand_x=True)]
]

# 4. PI CAP CTRL (0-31, 5 bits) - now in PI CTRL section with editable dropdown
pi_cap_ctrl_layout = [
    [sg.Text('PI CAP CTRL', font='Any 8', justification='left', expand_x=True), 
     sg.Combo([str(i) for i in range(32)], default_value='0', key='_PI_CAP_CTRL_', font='Any 8', readonly=False, expand_x=True)]
]

# 8. BGR/CSH/PI/DEMOD/BUFF ICTRL (0-7, 3 bits each) - now CURRENT CTRL section with editable dropdowns
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

# 9. ENABLES & RESET section - 3 vertical columns (2x3 grid: horizontal 3, vertical 2)
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

# 10. FILTER section - center aligned
filter_layout = [
    [sg.CB('LPF EN', key='_LPF_EN_', default=False, font='Any 8', expand_x=True)],
    [sg.CB('LPF SAMPLE EN', key='_LPF_SAMP_EN_', default=False, font='Any 8', expand_x=True)],
    [sg.CB('BPF EN', key='_BPF_EN_', default=False, font='Any 8', expand_x=True)],
    [sg.CB('BPF SAMPLE EN', key='_BPF_SAMP_EN_', default=False, font='Any 8', expand_x=True)],
]

# 11. TEST NETWORK section - center aligned with editable dropdowns (0-15 range)
test_network_layout = [
    [sg.Text('TEST ADD', font='Any 8', justification='center', expand_x=True), 
     sg.Combo([str(i) for i in range(16)], default_value='0', key='_TEST_ADD_', font='Any 8', readonly=False, expand_x=True),
     sg.Text('TMUX SEL', font='Any 8', justification='center', expand_x=True), 
     sg.Combo([str(i) for i in range(16)], default_value='0', key='_TMUX_SEL_', font='Any 8', readonly=False, expand_x=True)]
]

# Advanced Settings Panel
def make_advanced_settings_panel():
    port_list, default_port = get_available_ports()
    
    # Clock frequency options (in kHz)
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
                 key='_ADVANCED_FRAME_', visible=False)]
    ]

def make_layout():
    layout = [
        [
            # Left section
            sg.Column([
                # Top row: CSH EN, PI EN, PI DELAY CTRL in a line - reduced horizontal spacing
                [
                    sg.Frame('CSH EN', csh_en_layout, font='Any 8', pad=(1,1), expand_x=True, expand_y=True, element_justification='center'),
                    sg.Frame('PI EN', pi_en_layout, font='Any 8', pad=(1,1), expand_x=True, expand_y=True, element_justification='center'),
                    sg.Frame('PI DELAY CTRL', pi_delay_ctrl_layout, font='Any 8', pad=(1,1), expand_x=True, expand_y=True, element_justification='center')
                ],
                [sg.Frame('ENABLES & RESET', enables_reset_layout, font='Any 8', pad=(1,1), expand_x=True, expand_y=True, element_justification='center')],
                [sg.Frame('TEST NETWORK', test_network_layout, font='Any 8', pad=(1,1), expand_x=True, expand_y=True, element_justification='center')]
            ], vertical_alignment='top', pad=(1,1), element_justification='left', expand_x=True, expand_y=True),
            
            # Right section - moved closer to left section
            sg.Column([
                # Top: PI CTRL
                [sg.Frame('PI CTRL', [
                    pi_sum_delay_ctrl_layout[0],
                    pi_dc_ctrl_layout[0],
                    pi_cap_ctrl_layout[0]
                ], font='Any 8', pad=(1,1), expand_x=True, expand_y=True, element_justification='center')],
                # Middle: CURRENT CTRL
                [sg.Frame('CURRENT CTRL', current_ctrl_layout, font='Any 8', pad=(1,1), expand_x=True, expand_y=True, element_justification='center')],
                # Bottom: FILTER
                [sg.Frame('FILTER', filter_layout, font='Any 8', pad=(1,1), expand_x=True, expand_y=True, element_justification='center')],
            ], vertical_alignment='top', pad=(1,1), expand_x=True, expand_y=True),
            
            # Advanced Settings Panel (toggleable) - initially hidden
            sg.Column(make_advanced_settings_panel(), vertical_alignment='top', pad=(5,1), 
                     expand_x=False, expand_y=True, key='_ADVANCED_COLUMN_')
        ],
        [
            # Very bottom: Important buttons - centered with settings toggle
            sg.Push(),
            sg.Button('RESET', size=(8,2), pad=(5,5)),
            sg.Button('TRANSFER DATA', key='TRANSFER DATA', size=(15,2), pad=(5,5)),
            sg.Button('SAVE STATE', key='SAVE_STATE', size=(12,2), pad=(5,5)),
            sg.Button('LOAD STATE', key='LOAD_STATE', size=(12,2), pad=(5,5)),
            sg.Button('>', key='_TOGGLE_SETTINGS_', size=(3,2), pad=(5,5), tooltip='Toggle Advanced Settings'),
            sg.Push(),
        ],
    ]
    return layout

