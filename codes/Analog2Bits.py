"""
Takes Analog Inputs from the GUI and outputs the corresponding bit values
Input format : Dictionary
Output format : Dictionary

"""
def An2Bits(gui_dict):
    """Input : dictionary provided by the GUI (GUI Output)
       Output: dictionary (with same keys as input) with bit values instead
       of analog values
    """
    bit_dict = {}
    for key in gui_dict:
        #print(type(gui_dict[key]))
        bit_dict[key] = bin(int(gui_dict[key]))[2:]#to remove 0b in the beginning which comes from the bin function of python
    return bit_dict
    #print(bit_dict)
#An2Bits({'lnadb': True})
