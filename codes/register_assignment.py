def RegisterAssignment(bit_dict):
    """
    Input: bit_dict - dictionary with field names as keys and their values as strings (underscore style, e.g., _CSH_EN_8_)
    Output: config_bytes - list of 16 bytes, representing 128 bits for the new chip
    """
    config_bits = [0] * 128  # Bit 127 is MSB, Bit 0 is LSB

    # Helper to assign multi-bit fields
    def assign_bits(start_bit, value, width):
        bits = f"{int(value):0{width}b}"
        for i in range(width):
            config_bits[start_bit - i] = int(bits[i])

    # 1-8: _CSH_EN_8_ to _CSH_EN_1_ (Tick)
    for i in range(8):
        config_bits[127 - i] = int(bit_dict.get(f"_CSH_EN_{8-i}_", 0))
    # 9-16: _PI_EN_8_ to _PI_EN_1_ (Tick)
    for i in range(8):
        config_bits[119 - i] = int(bit_dict.get(f"_PI_EN_{8-i}_", 0))
    # 17-19: _PI_DC_CTRL_ (Number 0-7, 3 bits)
    assign_bits(111, bit_dict.get("_PI_DC_CTRL_", 0), 3)
    # 20-24: _PI_CAP_CTRL_ (Number 0-31, 5 bits)
    assign_bits(108, bit_dict.get("_PI_CAP_CTRL_", 0), 5)
    # 25-31: _PI_DELAY_CTRL1_ (Number 0-127, 7 bits)
    assign_bits(103, bit_dict.get("_PI_DELAY_CTRL1_", 0), 7)
    # 32-38: _PI_DELAY_CTRL2_ (Number 0-127, 7 bits)
    assign_bits(96, bit_dict.get("_PI_DELAY_CTRL2_", 0), 7)
    # 39-45: _PI_DELAY_CTRL3_ (Number 0-127, 7 bits)
    assign_bits(89, bit_dict.get("_PI_DELAY_CTRL3_", 0), 7)
    # 46-52: _PI_DELAY_CTRL4_ (Number 0-127, 7 bits)
    assign_bits(82, bit_dict.get("_PI_DELAY_CTRL4_", 0), 7)
    # 53-59: _PI_DELAY_CTRL5_ (Number 0-127, 7 bits)
    assign_bits(75, bit_dict.get("_PI_DELAY_CTRL5_", 0), 7)
    # 60-66: _PI_DELAY_CTRL6_ (Number 0-127, 7 bits)
    assign_bits(68, bit_dict.get("_PI_DELAY_CTRL6_", 0), 7)
    # 67-73: _PI_DELAY_CTRL7_ (Number 0-127, 7 bits)
    assign_bits(61, bit_dict.get("_PI_DELAY_CTRL7_", 0), 7)
    # 74-80: _PI_DELAY_CTRL8_ (Number 0-127, 7 bits)
    assign_bits(54, bit_dict.get("_PI_DELAY_CTRL8_", 0), 7)
    # 81-87: _PI_SUM_DELAY_CTRL_ (Number 0-127, 7 bits)
    assign_bits(47, bit_dict.get("_PI_SUM_DELAY_CTRL_", 0), 7)
    # 88-90: _PI_TEST_DELAY_CTRL_ (Number 0-7, 3 bits)
    assign_bits(40, bit_dict.get("_PI_TEST_DELAY_CTRL_", 0), 3)
    # 91: _BPF_SAMP_EN_ (Tick)
    config_bits[37] = int(bit_dict.get("_BPF_SAMP_EN_", 0))
    # 92: _BPF_EN_ (Tick)
    config_bits[36] = int(bit_dict.get("_BPF_EN_", 0))
    # 93: _LPF_SAMP_EN_ (Tick)
    config_bits[35] = int(bit_dict.get("_LPF_SAMP_EN_", 0))
    # 94: _LPF_EN_ (Tick)
    config_bits[34] = int(bit_dict.get("_LPF_EN_", 0))
    # 95-97: _BGR_OUT_CTRL_ (Number 0-7, 3 bits)
    assign_bits(33, bit_dict.get("_BGR_OUT_CTRL_", 0), 3)
    # 98-100: _CSH_ICTRL_ (Number 0-7, 3 bits)
    assign_bits(30, bit_dict.get("_CSH_ICTRL_", 0), 3)
    # 101-103: _PI_ICTRL_ (Number 0-7, 3 bits)
    assign_bits(27, bit_dict.get("_PI_ICTRL_", 0), 3)
    # 104-106: _DEMOD_ICTRL_ (Number 0-7, 3 bits)
    assign_bits(24, bit_dict.get("_DEMOD_ICTRL_", 0), 3)
    # 107-109: _BUFF_ICTRL_ (Number 0-7, 3 bits)
    assign_bits(21, bit_dict.get("_BUFF_ICTRL_", 0), 3)
    # 110: _SUM_PI_EN_ (Tick)
    config_bits[18] = int(bit_dict.get("_SUM_PI_EN_", 0))
    # 111: _DEMOD_ICH_EN_ (Tick)
    config_bits[17] = int(bit_dict.get("_DEMOD_ICH_EN_", 0))
    # 112: _DEMOD_QCH_EN_ (Tick)
    config_bits[16] = int(bit_dict.get("_DEMOD_QCH_EN_", 0))
    # 113: _LVDS_RES_CTRL_ (Tick)
    config_bits[15] = int(bit_dict.get("_LVDS_RES_CTRL_", 0))
    # 114: _BUFF_EN_ (Tick)
    config_bits[14] = int(bit_dict.get("_BUFF_EN_", 0))
    # 115: _IQ_DIV_EN_ (Tick)
    config_bits[13] = int(bit_dict.get("_IQ_DIV_EN_", 0))
    # 116: _IQ_DIV_RST_ (Tick)
    config_bits[12] = int(bit_dict.get("_IQ_DIV_RST_", 0))
    # 117: _CSH_TEST_EN_ (Tick)
    config_bits[11] = int(bit_dict.get("_CSH_TEST_EN_", 0))
    # 118: _CSH_VCM_EN_ (Tick)
    config_bits[10] = int(bit_dict.get("_CSH_VCM_EN_", 0))
    # 119: _PI_TEST_EN_ (Tick)
    config_bits[9] = int(bit_dict.get("_PI_TEST_EN_", 0))
    # 120-123: _TEST_ADD_ (Number 0-15, 4 bits)
    assign_bits(8, bit_dict.get("_TEST_ADD_", 0), 4)
    # 124-127: _TMUX_SEL_ (Number 0-15, 4 bits)
    assign_bits(4, bit_dict.get("_TMUX_SEL_", 0), 4)
    # 128: _SPARE_ (default 0)
    config_bits[0] = int(bit_dict.get("_SPARE_", 0))

    # After all assignments, pack bits into 16 bytes (MSB first)
    config_bytes = []
    for byte_index in range(16):
        byte_val = 0
        for bit_in_byte in range(8):
            bit_pos = 127 - (byte_index * 8 + bit_in_byte)
            byte_val = (byte_val << 1) | config_bits[bit_pos]
        config_bytes.append(byte_val)

    return config_bytes


def rev(bit_str):
  """
    To reverse the bits in bit_dict;bits are in string format and output them in a list
    Input : string of bits
    Output : reversed array of bits
  """
  out_str = []
  str_len = len(bit_str)
  for i in range(str_len):
      out_str.append(bit_str[str_len-1-i])
  return out_str
