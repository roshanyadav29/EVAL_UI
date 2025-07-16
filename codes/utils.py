def arr2int(array):
    """
    convert 8 bits of array into integers
    """
    num = 0
    for i in range(8):
        num = num + int(array[7-i])*(2**i)
    return num
