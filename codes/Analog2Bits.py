"""
Takes Analog Inputs from the GUI and outputs the corresponding bit values
Input format : Dictionary
Output format : Dictionary

"""
def An2Bits(gui_dict):
    """Input : dictionary provided by the GUI (GUI Output)
       Output: dictionary (with same keys as input) with integer values
       ready for register assignment (not binary strings)
    """
    bit_dict = {}
    for key in gui_dict:
        # Convert GUI values to integers
        # Booleans: True -> 1, False -> 0
        # Strings: "7" -> 7, "127" -> 127, etc.
        bit_dict[key] = int(gui_dict[key])
    return bit_dict
    #print(bit_dict)
#An2Bits({'lnadb': True})
