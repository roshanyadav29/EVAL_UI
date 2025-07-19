"""
ESP32 Chip Register Assignment Module

This module handles the critical conversion from GUI parameter values to the 128-bit
configuration register required by the ESP32 chip. The register mapping follows a
specific bit field layout where each parameter controls different chip functions.

Key Functions:
- RegisterAssignment(): Main conversion function from GUI values to 128-bit register
- rev(): Utility function for bit string reversal operations

Technical Context:
- 128-bit register = 16 bytes transmitted via SPI to ESP32
- Bit numbering: Bit 127 (MSB) to Bit 0 (LSB)
- Parameter types: Single bits (ticks), multi-bit fields (numbers)
- Critical for chip functionality: CSH, PI, demodulation, and control settings
"""

def RegisterAssignment(bit_dict):
    """
    Convert GUI parameter dictionary to 128-bit register configuration.
    
    This function maps GUI control values to specific bit positions in the chip's
    configuration register. Each parameter corresponds to specific chip functionality
    including channel selection, power controls, delays, and test modes.
    
    Args:
        bit_dict (dict): GUI parameter values with field names as keys
                        Format: {"_CSH_EN_8_": 1, "_PI_DC_CTRL_": 5, ...}
    
    Returns:
        list: 16 bytes representing 128-bit configuration register
              Byte order: MSB first for direct SPI transmission
    
    Register Layout:
        Bits 1-8:   CSH channel enables
        Bits 9-16:  PI channel enables  
        Bits 17-90: PI control and delay settings
        Bits 91-109: Filter and current controls
        Bits 110-128: Enable flags and test modes
    """
    config_bits = [0] * 128  # Initialize 128-bit register: Bit 127 (MSB) to Bit 0 (LSB)

    # Helper function for multi-bit field assignment
    def assign_bits(start_bit, value, width):
        """
        Assign multi-bit values to specific register positions.
        
        Args:
            start_bit (int): MSB position of the field
            value (int): Numeric value to encode
            width (int): Number of bits for the field
        """
        bits = f"{int(value):0{width}b}"  # Convert to binary string with zero padding
        for i in range(width):
            config_bits[start_bit - i] = int(bits[i])

    # === CHANNEL ENABLE SECTION (Bits 1-16) ===
    # CSH (Charge Sharing) Channel Enables - Individual control for 8 channels
    # Bits 1-8: _CSH_EN_8_ to _CSH_EN_1_ (Binary flags)
    for i in range(8):
        config_bits[127 - i] = int(bit_dict.get(f"_CSH_EN_{8-i}_", 0))
    
    # PI (Phase Interpolator) Channel Enables - Individual control for 8 channels  
    # Bits 9-16: _PI_EN_8_ to _PI_EN_1_ (Binary flags)
    for i in range(8):
        config_bits[119 - i] = int(bit_dict.get(f"_PI_EN_{8-i}_", 0))

    # === PI CONTROL SECTION (Bits 17-90) ===
    # Phase Interpolator configuration and delay controls
    # Bits 17-19: _PI_DC_CTRL_ (DC control, 0-7, 3 bits)
    assign_bits(111, bit_dict.get("_PI_DC_CTRL_", 0), 3)
    # Bits 20-24: _PI_CAP_CTRL_ (Capacitor control, 0-31, 5 bits)
    assign_bits(108, bit_dict.get("_PI_CAP_CTRL_", 0), 5)
    
    # PI Delay Controls - Individual delay settings for 8 channels (7 bits each, 0-127)
    # Bits 25-31: _PI_DELAY_CTRL1_ (Channel 1 delay)
    assign_bits(103, bit_dict.get("_PI_DELAY_CTRL1_", 0), 7)
    # Bits 32-38: _PI_DELAY_CTRL2_ (Channel 2 delay)
    assign_bits(96, bit_dict.get("_PI_DELAY_CTRL2_", 0), 7)
    # Bits 39-45: _PI_DELAY_CTRL3_ (Channel 3 delay)
    assign_bits(89, bit_dict.get("_PI_DELAY_CTRL3_", 0), 7)
    # Bits 46-52: _PI_DELAY_CTRL4_ (Channel 4 delay)
    # Bits 46-52: _PI_DELAY_CTRL4_ (Channel 4 delay)
    assign_bits(82, bit_dict.get("_PI_DELAY_CTRL4_", 0), 7)
    # Bits 53-59: _PI_DELAY_CTRL5_ (Channel 5 delay)
    assign_bits(75, bit_dict.get("_PI_DELAY_CTRL5_", 0), 7)
    # Bits 60-66: _PI_DELAY_CTRL6_ (Channel 6 delay)
    assign_bits(68, bit_dict.get("_PI_DELAY_CTRL6_", 0), 7)
    # Bits 67-73: _PI_DELAY_CTRL7_ (Channel 7 delay)
    assign_bits(61, bit_dict.get("_PI_DELAY_CTRL7_", 0), 7)
    # Bits 74-80: _PI_DELAY_CTRL8_ (Channel 8 delay)
    assign_bits(54, bit_dict.get("_PI_DELAY_CTRL8_", 0), 7)
    
    # PI Sum and Test Delay Controls
    # Bits 81-87: _PI_SUM_DELAY_CTRL_ (Sum delay control, 0-127, 7 bits)
    assign_bits(47, bit_dict.get("_PI_SUM_DELAY_CTRL_", 0), 7)
    # Bits 88-90: _PI_TEST_DELAY_CTRL_ (Test delay control, 0-7, 3 bits)
    assign_bits(40, bit_dict.get("_PI_TEST_DELAY_CTRL_", 0), 3)

    # === FILTER AND CURRENT CONTROL SECTION (Bits 91-109) ===
    # Filter enable controls
    # Bit 91: _BPF_SAMP_EN_ (Bandpass filter sampling enable)
    config_bits[37] = int(bit_dict.get("_BPF_SAMP_EN_", 0))
    # Bit 92: _BPF_EN_ (Bandpass filter enable)
    config_bits[36] = int(bit_dict.get("_BPF_EN_", 0))
    # Bit 93: _LPF_SAMP_EN_ (Lowpass filter sampling enable)
    config_bits[35] = int(bit_dict.get("_LPF_SAMP_EN_", 0))
    # Bit 94: _LPF_EN_ (Lowpass filter enable)
    config_bits[34] = int(bit_dict.get("_LPF_EN_", 0))
    
    # Current control settings (3 bits each, 0-7)
    # Bits 95-97: _BGR_OUT_CTRL_ (Bandgap reference output control)
    assign_bits(33, bit_dict.get("_BGR_OUT_CTRL_", 0), 3)
    # Bits 98-100: _CSH_ICTRL_ (CSH current control)
    assign_bits(30, bit_dict.get("_CSH_ICTRL_", 0), 3)
    # Bits 101-103: _PI_ICTRL_ (PI current control)
    assign_bits(27, bit_dict.get("_PI_ICTRL_", 0), 3)
    # Bits 104-106: _DEMOD_ICTRL_ (Demodulator current control)
    assign_bits(24, bit_dict.get("_DEMOD_ICTRL_", 0), 3)
    # Bits 107-109: _BUFF_ICTRL_ (Buffer current control)
    assign_bits(21, bit_dict.get("_BUFF_ICTRL_", 0), 3)

    # === ENABLE FLAGS AND TEST MODES SECTION (Bits 110-128) ===
    # System enable controls
    # Bit 110: _SUM_PI_EN_ (Sum PI enable)
    config_bits[18] = int(bit_dict.get("_SUM_PI_EN_", 0))
    # Bit 111: _DEMOD_ICH_EN_ (Demodulator I channel enable)
    config_bits[17] = int(bit_dict.get("_DEMOD_ICH_EN_", 0))
    # Bit 112: _DEMOD_QCH_EN_ (Demodulator Q channel enable)
    config_bits[16] = int(bit_dict.get("_DEMOD_QCH_EN_", 0))
    # Bit 113: _LVDS_RES_CTRL_ (LVDS resistance control)
    config_bits[15] = int(bit_dict.get("_LVDS_RES_CTRL_", 0))
    # Bit 114: _BUFF_EN_ (Buffer enable)
    config_bits[14] = int(bit_dict.get("_BUFF_EN_", 0))
    # Bit 115: _IQ_DIV_EN_ (IQ divider enable)
    config_bits[13] = int(bit_dict.get("_IQ_DIV_EN_", 0))
    # Bit 116: _IQ_DIV_RST_ (IQ divider reset)
    config_bits[12] = int(bit_dict.get("_IQ_DIV_RST_", 0))
    
    # Test mode controls
    # Bit 117: _CSH_TEST_EN_ (CSH test enable)
    config_bits[11] = int(bit_dict.get("_CSH_TEST_EN_", 0))
    # Bit 118: _CSH_VCM_EN_ (CSH VCM enable)
    config_bits[10] = int(bit_dict.get("_CSH_VCM_EN_", 0))
    # Bit 119: _PI_TEST_EN_ (PI test enable)
    config_bits[9] = int(bit_dict.get("_PI_TEST_EN_", 0))
    
    # Test address and multiplexer controls (4 bits each, 0-15)
    # Bits 120-123: _TEST_ADD_ (Test address selection)
    assign_bits(8, bit_dict.get("_TEST_ADD_", 0), 4)
    # Bits 124-127: _TMUX_SEL_ (Test multiplexer selection)
    assign_bits(4, bit_dict.get("_TMUX_SEL_", 0), 4)
    # Bit 128: _SPARE_ (Spare bit, typically 0)
    config_bits[0] = int(bit_dict.get("_SPARE_", 0))

    # === REGISTER PACKING SECTION ===
    # Convert 128-bit array to 16 bytes for SPI transmission
    config_bytes = []
    for byte_index in range(16):
        byte_val = 0
        # Pack 8 bits into each byte, MSB first
        for bit_in_byte in range(8):
            bit_pos = 127 - (byte_index * 8 + bit_in_byte)
            byte_val = (byte_val << 1) | config_bits[bit_pos]
        config_bytes.append(byte_val)

    return config_bytes


def rev(bit_str):
    """
    Reverse the order of bits in a string representation.
    
    Utility function for bit manipulation operations where bit order
    reversal is needed for specific register formats or protocols.
    
    Args:
        bit_str (str): String of bits to reverse (e.g., "10110")
    
    Returns:
        list: Reversed array of individual bit characters
              Example: "101" -> ['1', '0', '1']
    
    Note: Output is character array, not integer values
    """
    out_str = []
    str_len = len(bit_str)
    for i in range(str_len):
        out_str.append(bit_str[str_len-1-i])
    return out_str
