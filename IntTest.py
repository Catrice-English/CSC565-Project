import re
import csv
import math

output_line = [None, None, None, None, None]
output_rows = []

flags = {
    'carry': 0,             #unsigned overflow
    'sign': 0,              #1 when result is 0
    'zero': 0,              #1 when result is negative
    'overflow': 0           #signed overflow
}

registers = {
    'eax': ['F01', None],
    'ebx': ['F02', None],
    'ecx': ['F03', None],
    'edx': ['F04', None]
}

variable_values = {
    'a': ['000', None, 'unsigned'],
    'b': ['001', None, 'unsigned'],
    'c': ['002', None, 'unsigned'],
    'x': ['003', None, 'signed'],
    'y': ['004', None, 'signed'],
    'z': ['005', None, 'signed']
}

opcodes = {
    'mov': '509',
    'add': '400',
    'sub': '401',
    'mult': '402',
    'div': '403',
    'addsub': '404',
    'addmult': '405',
    'adddiv': '406',
    'subadd': '407',
    'submult': '408',
    'subdiv': '409',
    'multadd': '40A',
    'multsub': '40B',
    'multdiv': '40C',
    'divadd': '40D',
    'divsub': '40E',
    'divmult': '40F',
    'addadd': '410',
    'subsub': '411',
    'multmult': '412',
    'divdiv': '413',
    'jmp': '500',
    'je': '501',
    'jne': '502',
    'jz': '503',
    'jg': '504',
    'jge': '505',
    'jl': '506',
    'jle': '507',
    'cmp': '508'
}

testfile = r"""unsigned a b c
signed x y z

a = 3
b = 15 + a
c = b * a / 10

x = -5
y = 13

if c <= 10
    x = y + 10
else
    x = y - 20

while y > 0
    print y
    print \n
    print x
    print \n
    y = y - 1"""

testfile2 = r"""unsigned a b
signed x y

a = 10
b = 2
x = -10
y = 1

while x < 0
    print x
    print \n
    x = x + y

while a > 0
    print a
    print \n
    a = a - b
"""

#HLC, YMC Assembly, YMC Encoding, Mod Regs, Mod Flags - CSV order

def line_splitter(read_file):
    list1 = []
    list2 = []
    paragraphs = read_file.split('\n\n')
    ctr = 0
    for i in paragraphs:
        list1.append(i)
        ctr += 1
    ctr = 0
    for i in list1:                                 
        split_list = list1[ctr].split('\n')
        strip_split_list = [line.strip() for line in split_list]
        list2.append(strip_split_list)
        ctr +=1
    return list2

def list_splitter(list_ex):
    split_list = list_ex.split()
    return split_list

def classifier(list_ex):
    ctr = 0
    for i in list_ex:
        first_words = i[0].split()
        if first_words[0] == 'if':
            if_else(i)
            print('\n')
        elif first_words[0] == 'while':
            while_loop(i)
            print('\n')
        elif first_words[0] in variable_values.keys():
            arith_op(i)

def arith_op(list_ex):
    #print('Operand Statement')
    #print(list_ex, '\n')
    for i in list_ex:
        temp_list = list_splitter(i)
        if len(temp_list) == 3:
            print('MOV COMMAND')
            mov_func(temp_list)
            print('\n')
        elif len(temp_list) == 5:
            print('BASIC ARITH COMMAND')
            basic_func(temp_list)
            print('\n')
        elif len(temp_list) == 7:
            print('COMPLEX ARITH COMMAND')
            complex_func(temp_list)
            print('\n')

def if_else(list_ex):                                   #replace print statements with calling the operand function and reader for list_ex[1] if TRUE or list_ex[3] if FALSE
    words = list_ex[0].split()
    bool_flag = None
    temp_list = []
    #print(words)
    var = variable_values[words[1]][1]
    const = int(words[3])
    rel_op = words[2]
    hlc_str = list_ex[0]
    #print(hlc_str)
    assembly_list = [0]*2
    encoding_list = [0]*2
    assembly_list[0] = 'cmp eax, ' + hex(const)[2:].zfill(3).upper()
    encoding_list[0] = '508 F01 ' + hex(const)[2:].zfill(3).upper()
    if rel_op == '=':
        assembly_list[1] = 'je 300'
        encoding_list[1] = '501 300'
        if var == const:
            bool_flag = True                
        else:
            bool_flag = False
    elif rel_op == '!=':
        assembly_list[1] = 'jne 304'
        encoding_list[1] = '502 304'
        if var != const:
            bool_flag = True                
        else:
            bool_flag = False 
    elif rel_op == '>':
        assembly_list[1] = 'jg 308'
        encoding_list[1] = '504 308'
        if var > const:
            bool_flag = True                
        else:
            bool_flag = False 
    elif rel_op == '<':
        assembly_list[1] = 'jl 30C'
        encoding_list[1] = '506 30C'
        if var < const:
            bool_flag = True                
        else:
            bool_flag = False 
    elif rel_op == '>=':
        assembly_list[1] = 'jge 30F'
        encoding_list[1] = '505 30F'
        if var >= const:
            bool_flag = True                
        else:
            bool_flag = False
    elif rel_op == '<=':
        assembly_list[1] = 'jle 314'
        encoding_list[1] = '507 314'
        if var <= const:
            bool_flag = True                
        else:
            bool_flag = False
    assembly_str = "\n".join(assembly_list)
    encoding_str = "\n".join(encoding_list)
    #print(assembly_str)
    #print(encoding_str)
    mod_reg = ''
    flag_str = flag_check()                         #Checks for Flags

    output_line = [hlc_str, assembly_str, encoding_str, mod_reg, flag_str]
    output_rows.append(output_line)
    #encoding_list[1] = " ".join(encoding_list[1][1]
    #print(encoding_list[1])
    if bool_flag == True:
        temp_list = list_ex[1].split()
    elif bool_flag == False:
        hlc_str = list_ex[2]
        mod_reg = ''
        flag_str = flag_check()
        assembly_str = 'jmp 318'
        encoding_str = '500 318'
        output_line = [hlc_str, assembly_str, encoding_str, mod_reg, flag_str]
        output_rows.append(output_line)
        temp_list = list_ex[3].split()
    if len(temp_list) == 5:
        basic_func(temp_list)
    elif len(temp_list) == 7:
        complex_func(temp_list)

def while_loop(list_ex):
    print('LOOP TIME')
    new_list = []
    for i in list_ex:
        if len(i.split()) >= 3:
            new_list.append(i)
    words = new_list[0].split()
    temp_list = new_list[1:]

    var = variable_values[words[1]][1]
    const = int(words[3])

    rel_op = words[2]
    hlc_str = new_list[0]
    #print(hlc_str)
    assembly_list = [0]*2
    encoding_list = [0]*2
    assembly_list[0] = 'cmp eax, ' + hex(const)[2:].zfill(3).upper()
    encoding_list[0] = '508 F01 ' + hex(const)[2:].zfill(3).upper()
    mod_reg = ''
    flag_str = flag_check()
    assembly_str =''
    encoding_str =''
    if rel_op == '=':
        assembly_list[1] = 'je 200'
        encoding_list[1] = '501 200'
        assembly_str = "\n".join(assembly_list)
        encoding_str = "\n".join(encoding_list)
        output_line = [hlc_str, assembly_str, encoding_str, mod_reg, flag_str]
        output_rows.append(output_line)
        while variable_values[words[1]][1] == const:
            for i in temp_list:
                if len(i.split()) == 5:
                    basic_func(i.split())
                elif len(i.split()) == 7:
                    complex_func(i.split())
    elif rel_op == '!=':
        assembly_list[1] = 'jne 204'
        encoding_list[1] = '502 204'
        assembly_str = "\n".join(assembly_list)
        encoding_str = "\n".join(encoding_list)
        output_line = [hlc_str, assembly_str, encoding_str, mod_reg, flag_str]
        output_rows.append(output_line)
        while variable_values[words[1]][1] != const:
            for i in temp_list:
                if len(i.split()) == 5:
                    basic_func(i.split())
                elif len(i.split()) == 7:
                    complex_func(i.split())
    elif rel_op == '>':
        assembly_list[1] = 'jg 208'
        encoding_list[1] = '504 208'
        assembly_str = "\n".join(assembly_list)
        encoding_str = "\n".join(encoding_list)
        output_line = [hlc_str, assembly_str, encoding_str, mod_reg, flag_str]
        output_rows.append(output_line)
        while variable_values[words[1]][1] > const:
            for i in temp_list:
                if len(i.split()) == 5:
                    basic_func(i.split())
                elif len(i.split()) == 7:
                    complex_func(i.split())
    elif rel_op == '<':
        assembly_list[1] = 'jl 20C'
        encoding_list[1] = '506 20C'
        assembly_str = "\n".join(assembly_list)
        encoding_str = "\n".join(encoding_list)
        output_line = [hlc_str, assembly_str, encoding_str, mod_reg, flag_str]
        output_rows.append(output_line)
        while variable_values[words[1]][1] < const:
            for i in temp_list:
                print(i)
                if len(i.split()) == 5:
                    basic_func(i.split())
                elif len(i.split()) == 7:
                    complex_func(i.split())
    elif rel_op == '>=':
        assembly_list[1] = 'jge 20F'
        encoding_list[1] = '505 20F'
        assembly_str = "\n".join(assembly_list)
        encoding_str = "\n".join(encoding_list)
        output_line = [hlc_str, assembly_str, encoding_str, mod_reg, flag_str]
        output_rows.append(output_line)
        while variable_values[words[1]][1] >= const:
            for i in temp_list:
                if len(i.split()) == 5:
                    basic_func(i.split())
                elif len(i.split()) == 7:
                    complex_func(i.split())
    elif rel_op == '<=':
        assembly_list[1] = 'jle 214'
        encoding_list[1] = '507 214'
        assembly_str = "\n".join(assembly_list)
        encoding_str = "\n".join(encoding_list)
        output_line = [hlc_str, assembly_str, encoding_str, mod_reg, flag_str]
        output_rows.append(output_line)
        while variable_values[words[1]][1] <= const:
            for i in temp_list:
                if len(i.split()) == 5:
                    basic_func(i.split())
                elif len(i.split()) == 7:
                    complex_func(i.split())
    hlc_str = ''
    mod_reg = ''
    flag_str = flag_check()
    assembly_str = 'jmp 218'
    encoding_str = '500 218'
    output_line = [hlc_str, assembly_str, encoding_str, mod_reg, flag_str]
    output_rows.append(output_line)
            

def mov_func(mov_list):
    print(mov_list)
    hlc_str = " ".join(mov_list)                    #HLC Column

    registers['eax'][1] = register_det((mov_list[2]))          #modified registers
    variable_values[mov_list[0]][1] = registers['eax'][1]
    registers['eax'][1] = None
    mod_reg = 'eax'

    if variable_values[mov_list[0]][1] == 0:
        flags['zero'] = 1
    
    if variable_values[mov_list[0]][2] == 'signed':
        temp = int(mov_list[2])
        if temp < 0:
            mov_list[2] = str(4095 + temp)
            flags['sign'] = 1
                                          
    assembly_list = [0]*3                           #Assembly Column
    if mov_list[0] in variable_values.keys():
        assembly_list[0] = 'mov'
        assembly_list[1] = 'eax,'
        assembly_list[2] = hex(int(mov_list[2]))[2:].zfill(3).upper()
    assembly_str = " ".join(assembly_list)

    encoding_str = assembly_str.replace(',', '')    #YMC Encoding
    temp_str = encoding_str.split()
    temp_str[0] = opcodes[temp_str[0]]
    temp_str[1] = registers[temp_str[1]][0]
    encoding_str = " ".join(temp_str)
                             
    flag_str = flag_check()                         #Checks for Flags

    output_line = [hlc_str, assembly_str, encoding_str, mod_reg, flag_str]
    output_rows.append(output_line)

def basic_func(basic_list):
    #print(basic_list)
    assembly_list = [0]*3
    encoding_str = ''
    temp_list = []
    hlc_str = " ".join(basic_list)                          #HLC Column

    registers['eax'][1] = register_det((basic_list[2]))   #modified registers
    registers['ebx'][1] = register_det((basic_list[4]))
    if basic_list[3] == '+':
        variable_values[basic_list[0]][1] = registers['eax'][1] + registers['ebx'][1]
        assembly_list[2] = 'add eax, ebx'
    elif basic_list[3] == '-':
        variable_values[basic_list[0]][1] = registers['eax'][1] - registers['ebx'][1]
        assembly_list[2] = 'sub eax, ebx'
    elif basic_list[3] == '*':
        variable_values[basic_list[0]][1] = registers['eax'][1] * registers['ebx'][1]
        assembly_list[2] = 'mult eax, ebx'
    elif basic_list[3] == '/':
        variable_values[basic_list[0]][1] = math.trunc(registers['eax'][1] / registers['ebx'][1])
        assembly_list[2] = 'div eax, ebx'

    if variable_values[basic_list[0]][2] == 'signed':
        temp1 = registers['eax'][1]
        temp2 = registers['ebx'][1]
        if temp1 < 0:
            registers['eax'][1] = str(4095 + temp1)
        if temp2 < 0:
            registers['ebx'][1] = str(4095 + temp2)
    flag_det(basic_list)                                #flag check
    assembly_list[0] = 'mov eax, ' + hex(int(registers['eax'][1]))[2:].zfill(3).upper()
    assembly_list[1] = 'mov ebx, ' + hex(int(registers['ebx'][1]))[2:].zfill(3).upper()
    registers['eax'][1] = None
    registers['ebx'][1] = None
    mod_reg = 'eax, ebx'                                #modified registers
    assembly_str = "\n".join(assembly_list)             #assembly encoding
    print(assembly_list)

    for i in assembly_list:
        temp_str = i.replace(',', '')
        temp_str = temp_str.split()
        temp_str[0] = opcodes[temp_str[0]]
        temp_str[1] = registers[temp_str[1]][0]
        if temp_str[2] in registers.keys():
            temp_str[2] = registers[temp_str[2]][0]
        temp_str = temp_str[0] + ' ' + temp_str[1] + ' ' + temp_str[2]
        temp_list.append(temp_str)
    encoding_str = "\n".join(temp_list)

    flag_str = flag_check()
    output_line = [hlc_str, assembly_str, encoding_str, mod_reg, flag_str]
    output_rows.append(output_line)

def complex_func(comp_list):
    print(comp_list)
    assembly_list = [0]*4
    encoding_str = ''
    temp_list = []
    hlc_str = " ".join(comp_list)
    #print(hlc_str)
    registers['eax'][1] = register_det(comp_list[2])
    registers['ebx'][1] = register_det(comp_list[4])
    registers['ecx'][1] = register_det(comp_list[6])
    if comp_list[3] == '+':
        if comp_list[5] == '+':
            variable_values[comp_list[0]][1] = (registers['eax'][1] + registers['ebx'][1]) + registers['ecx'][1]
            assembly_list[3] = 'addadd eax, ebx, ecx'
        elif comp_list[5] == '-':
            variable_values[comp_list[0]][1] = (registers['eax'][1] + registers['ebx'][1]) - registers['ecx'][1]
            assembly_list[3] = 'addsub eax, ebx, ecx'
        elif comp_list[5] == '*':
            variable_values[comp_list[0]][1] = (registers['eax'][1] + registers['ebx'][1]) * registers['ecx'][1]
            assembly_list[3] = 'addmult eax, ebx, ecx'
        elif comp_list[5] == '/':
            variable_values[comp_list[0]][1] = math.trunc((registers['eax'][1] + registers['ebx'][1]) / registers['ecx'][1])
            assembly_list[3] = 'adddiv eax, ebx, ecx'
    elif comp_list[3] == '-':
        if comp_list[5] == '+':
            variable_values[comp_list[0]][1] = (registers['eax'][1] - registers['ebx'][1]) + registers['ecx'][1]
            assembly_list[3] = 'subadd eax, ebx, ecx'
        elif comp_list[5] == '-':
            variable_values[comp_list[0]][1] = (registers['eax'][1] - registers['ebx'][1]) - registers['ecx'][1]
            assembly_list[3] = 'subsub eax, ebx, ecx'
        elif comp_list[5] == '*':
            variable_values[comp_list[0]][1] = (registers['eax'][1] - registers['ebx'][1]) * registers['ecx'][1]
            assembly_list[3] = 'submult eax, ebx, ecx'
        elif comp_list[5] == '/':
            variable_values[comp_list[0]][1] = math.trunc((registers['eax'][1] - registers['ebx'][1]) / registers['ecx'][1])
            assembly_list[3] = 'subdiv eax, ebx, ecx'
    elif comp_list[3] == '*':
        if comp_list[5] == '+':
            variable_values[comp_list[0]][1] = (registers['eax'][1] * registers['ebx'][1]) + registers['ecx'][1]
            assembly_list[3] = 'multadd eax, ebx, ecx'
        elif comp_list[5] == '-':
            variable_values[comp_list[0]][1] = (registers['eax'][1] * registers['ebx'][1]) - registers['ecx'][1]
            assembly_list[3] = 'multsub eax, ebx, ecx'
        elif comp_list[5] == '*':
            variable_values[comp_list[0]][1] = (registers['eax'][1] * registers['ebx'][1]) * registers['ecx'][1]
            assembly_list[3] = 'multmult eax, ebx, ecx'
        elif comp_list[5] == '/':
            variable_values[comp_list[0]][1] = math.trunc((registers['eax'][1] * registers['ebx'][1]) / registers['ecx'][1])
            assembly_list[3] = 'multdiv eax, ebx, ecx'
    elif comp_list[3] == '/':
        if comp_list[5] == '+':
            variable_values[comp_list[0]][1] = math.trunc((registers['eax'][1] / registers['ebx'][1]) + registers['ecx'][1])
            assembly_list[3] = 'divadd eax, ebx, ecx'
        elif comp_list[5] == '-':
            variable_values[comp_list[0]][1] = math.trunc((registers['eax'][1] / registers['ebx'][1]) - registers['ecx'][1])
            assembly_list[3] = 'divsub eax, ebx, ecx'
        elif comp_list[5] == '*':
            variable_values[comp_list[0]][1] = math.trunc((registers['eax'][1] / registers['ebx'][1]) * registers['ecx'][1])
            assembly_list[3] = 'divmult eax, ebx, ecx'
        elif comp_list[5] == '/':
            variable_values[comp_list[0]][1] = math.trunc((registers['eax'][1] / registers['ebx'][1]) / registers['ecx'][1])
            assembly_list[3] = 'divdiv eax, ebx, ecx'

    if variable_values[comp_list[0]][2] == 'signed':
        temp1 = registers['eax'][1]
        temp2 = registers['ebx'][1]
        temp3 = registers['ecx'][1]
        if temp1 < 0:
            registers['eax'][1] = str(4095 + temp1)
        if temp2 < 0:
            registers['ebx'][1] = str(4095 + temp2)
        if temp3 < 0:
            registers['ecx'][1] = str(4095 + temp3)
    flag_det(comp_list)                                #flag check
    assembly_list[0] = 'mov eax, ' + hex(int(registers['eax'][1]))[2:].zfill(3).upper()
    assembly_list[1] = 'mov ebx, ' + hex(int(registers['ebx'][1]))[2:].zfill(3).upper()
    assembly_list[2] = 'mov ecx, ' + hex(int(registers['ecx'][1]))[2:].zfill(3).upper()
    registers['eax'][1] = None
    registers['ebx'][1] = None
    registers['ecx'][1] = None
    mod_reg = 'eax, ebx, ecx'                                #modified registers
    assembly_str = "\n".join(assembly_list)             #assembly encoding
    print(assembly_list)
    
    for i in assembly_list:
        temp_str = i.replace(',', '')
        temp_str = temp_str.split()
        temp_str[0] = opcodes[temp_str[0]]
        temp_str[1] = registers[temp_str[1]][0]
        if temp_str[2] in registers.keys():
            temp_str[2] = registers[temp_str[2]][0]
        if len(temp_str) > 3:
            temp_str[3] = registers[temp_str[3]][0]
            temp_str = temp_str[0] + ' ' + temp_str[1] + ' ' + temp_str[2] + ' ' + temp_str[3]
        else:
            temp_str = temp_str[0] + ' ' + temp_str[1] + ' ' + temp_str[2]
        temp_list.append(temp_str)
    encoding_str = "\n".join(temp_list)

    flag_str = flag_check()
    output_line = [hlc_str, assembly_str, encoding_str, mod_reg, flag_str]
    output_rows.append(output_line)

    
def flag_check():                               #checks what flags were changed and creates a string for output
    flag_lst = []
    flag_str = None
    for i in flags:
        if flags[i] == 1:
            flag_lst.append(str(i) + ' : ' + str(flags[i]))
            flags[i] = 0
        flag_str = "\n".join(flag_lst)
    return(flag_str)

def flag_det(var_list):                       #checks the variable to see what flags should be changed
#    print(variable_values[var_list[0]])
    temp = variable_values[var_list[0]]
    if temp[2] == 'signed':
        if temp[1] == 0:        #zero flag
            flags['zero'] = 1
        elif temp[1] > 127:
            flags['overflow'] = 1
            temp[1] = temp[1]%128
        elif temp[1] < -128:
            flags['sign'] = 1
            flags['overflow'] = 1
            temp[1] = (temp[1]%128) - 128
        elif temp[1] < 0:
            flags['sign'] = 1
    elif temp[2] == 'unsigned':
        if temp[1] == 0:        #zero flag
            flags['zero'] = 1
        elif temp[1] > 255:
            flags['carry'] = 1
            temp[1] = temp[1]%256
    variable_values[var_list[0]] = temp
#    print(temp)

def register_det(element):
    if element in variable_values.keys():
        return variable_values[element][1]
    else:
        return int(element)

def csv_output(list_ex):
    file_name = 'output_file.csv'
    headers=['HLC','YMC Assembly', 'YMC Encoding', 'Modified Registers', 'Modified Flags']
    with open(file_name, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
        writer.writerows(list_ex)

split_file = line_splitter(testfile2)
classifier(split_file)
csv_output(output_rows)

#for i in variable_values:
#    print(variable_values[i])

#dec = 4095
#hex_string = hex(dec)[2:].zfill(3).upper()
#print(hex_string)
