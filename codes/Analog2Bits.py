"""
GUI Value Converter Module

Converts PySimpleGUI output values to integers for register assignment.
This is a critical preprocessing step that handles different GUI data types
before they are mapped to the 128-bit register configuration.

Input format: Dictionary from PySimpleGUI (mixed types)
Output format: Dictionary with integer values only
"""

def An2Bits(gui_dict):
    """
    Convert GUI dictionary values to integers for register assignment.
    
    This function standardizes all GUI inputs to integer format, which is
    required by the RegisterAssignment function for proper bit field mapping.
    
    Args:
        gui_dict (dict): Dictionary from PySimpleGUI with mixed value types:
                        - Checkboxes: True/False (boolean)
                        - Dropdowns: "0", "7", "127" etc. (string)
                        - Text inputs: string representations of numbers
    
    Returns:
        dict: Same keys as input, but all values converted to integers:
              - Boolean True/False → 1/0
              - String numbers → integers
              
    Example:
        Input:  {'_CSH_EN_1_': True, '_PI_DC_CTRL_': '7', '_TEST_ADD_': '15'}
        Output: {'_CSH_EN_1_': 1, '_PI_DC_CTRL_': 7, '_TEST_ADD_': 15}
    """
    bit_dict = {}
    
    for key in gui_dict:
        try:
            # Convert all GUI values to integers
            # This handles: True→1, False→0, "7"→7, "127"→127, etc.
            bit_dict[key] = int(gui_dict[key])
        except (ValueError, TypeError) as e:
            # Handle unexpected non-convertible values gracefully
            print(f"Warning: Could not convert {key}={gui_dict[key]} to int, using 0. Error: {e}")
            bit_dict[key] = 0
    
    return bit_dict
