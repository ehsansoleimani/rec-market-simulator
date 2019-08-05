# coding: utf-8


def writeStringArrayToNewFile(open_file, input_array):
    arr_len = len(input_array)

    for line in range(arr_len-1):
        line_len = len(input_array[line])
        for entry in range(line_len-1):
            open_file.write(input_array[line][entry] + ",")
        open_file.write(input_array[line][line_len-1] + "\n")
    last_line_len = len(input_array[arr_len-1])

    for entry in range(last_line_len-1):
        open_file.write(input_array[arr_len-1][entry] + ",")
    open_file.write(input_array[arr_len-1][last_line_len-1])


def readFloatArrayFromFile(open_file):
    flag_eof = False
    output_arr = []
    currentLine = open_file.readline().replace("\n","")
    while not flag_eof:
        output_arr.append(list(map(float, currentLine.split(","))))
        currentLine = open_file.readline()
        flag_eof = False if len(currentLine) > 0 else True
    return output_arr


def readStringArrayFromFile(open_file):
    flag_eof = False
    output_arr = []
    currentLine = open_file.readline().strip('\n')
    while not flag_eof:
        output_arr.append(currentLine.split(","))
        currentLine = open_file.readline().strip('\n')
        flag_eof = False if len(currentLine) > 0 else True
    return output_arr
