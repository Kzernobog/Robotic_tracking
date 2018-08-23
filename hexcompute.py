import string

# Converter class to operate in hexadecimal notation
class Hex_Computer(object):

    def __init__(self):
        pass

    # converts a given hexadecimal string into its bytes equivalent
    def convert_hex_to_bytes(self, data):
        """
        Converts a hex string to a sequence of bytes
        @params:
            data - a string
        @return:
            returns a list of bytes
        """
        if len(data)%2 != 0:
            data = data.split('x')
            data[1] = '0'+data[1]
            data = data[0]+'x'+data[1]
        data = data[2:]
        main_result_list = []
        res_len = len(data)
        for i in range(0, res_len, 2):
            construct = '0x'+result[i:i+2]
            print(construct)
            temp = int('0x'+result[i:i+2], 16)
            main_result_list.append(temp)

        return main_result_list



    # checks if a given string sticks to the hexadecimal notation
    def check_for_hex(self, data):
        """
        checks is the given string is a hexidecimal notation
        """
        value = False
        if data[0:2] == '0x':
            value = True
        if all(c in string.hexdigits for c in data[2:]):
            value = True

        return value

if __name__ == "__main__":
    pass
