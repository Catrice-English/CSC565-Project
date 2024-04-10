# -*- coding: utf-8 -*-
"""
Created on Tue Mar 26 18:27:14 2024

@author: Catrice, Nicholas, Ibaad
"""
#need hex_tokens and convert_to_hex to be able to handle negative numbers

import re
import csv

#set flags
flags = {
    'carry': 0,
    'sign': 0,
    'zero': 0,
    'overflow': 0
}

#register values
registers = {
    'eax': None,
    'ebx': None,
    'ecx': None,
    'edx': None
}

#variable values
variable_values = {
    'a': None,
    'b': None,
    'c': None,
    'x': None,
    'y': None,
    'z': None
}

#store whether variables are signed or unsigned
variables_sign_status = {
    'a': None,
    'b': None,
    'c': None,
    'x': None,
    'y': None,
    'z': None
}


# Map Registers to addresses
register_addresses = {
    'eax': 'F01',
    'ebx': 'F02',
    'ecx': 'F03',
    'edx': 'F04'
}

#set opcodes
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

#Map regular expressions to YMC equivalent
operator_to_machine_code = { 
    '+': 'add',
    '-': 'sub',
    '*': 'mult',
    '/': 'div',
    ('+', '-'): 'addsub',
    ('+', '+'): 'addadd',
    ('+', '*'): 'addmult',
    ('+', '/'): 'adddiv',
    ('-', '+'): 'subadd',
    ('-', '*'): 'submult',
    ('-', '/'): 'subdiv',
    ('-', '-'): 'subsub',
    ('*', '+'): 'multadd',
    ('*', '-'): 'multsub',
    ('*', '*'): 'multmult',
    ('*', '/'): 'multdiv',
    ('/', '+'): 'divadd',
    ('/', '-'): 'divsub',
    ('/', '*'): 'divmult',
    ('/', '/'): 'divdiv',
}

def main_split(line):
    # Split the program into lines
    #lines = program.splitlines()

    # Iterate over each line in the program
    #for line in lines:
    
    # Tokenize the current line using regular expressions
    tokens = re.findall(r'[a-zA-Z_]+|[\d]+|[+*/=\-<>]', line)
    
    #if blank line
    if len(tokens) == 0:
        hex_tokens = None
        
    #determine if line is variable declaration or arithmetic line
    elif tokens[0] in ['unsigned', 'signed']:
        signed_unsigned(tokens)
        hex_tokens = None

        
    else:

        #move variable from memory to register for computation
        tokens = move_mem_register(tokens)
        
        #if line read in is not a variable declaration line
        integer_list, number_integers = not_signed_unsigned(tokens)
        
        #determine appropriate arithmetic to perform based on number of operands
        if (number_integers == 2):
            result = two_operand_arithmetic(integer_list)
        else:
            result = three_operand_arithmetic(integer_list)
        
        #assign result to variable in variable_values dictionary
        if tokens[0] in variable_values:
            variable_values[tokens[0]] = result
                
        #set flags
        determine_carry_flag(result)
        determine_sign_flag(result)
        determine_zero_flag(result)
        determine_overflow_flag(integer_list)
    
        #print HLC        
        print(line)
        
        #translate to machine code
        hex_tokens = [convert_operands_to_hex(token) if \
                      isinstance(token, str) and token.isdigit() \
                      else token for token in tokens]
        machine_code_y = translate_to_machine_code(hex_tokens)
        print(machine_code_y)
        
        #print relevant dictionaries
        print(flags)
        
        #print names of registers that were altered
        print("modified registers:", end=' ')
        for key, value in registers.items():
            if value is not None:
                print(key, end=', ')
                
        print ("\n")
    
    #output to csv
    csv_output(line, hex_tokens)
    
    #reset the registers
    for items in registers:
        registers[items] = None


#function for variable declaration line
def signed_unsigned(list_tokens):
    
    for i in range(1, len(list_tokens)):
        variable_name = list_tokens[i]
        if variable_name in variables_sign_status:
            variables_sign_status[variable_name] = list_tokens[0]  
            
            
def move_mem_register(list_tokens):
    
    for i in range(2, len(list_tokens)):
        if list_tokens[i] in variable_values:
            for register_name in registers:
                if registers[register_name] is None:
                    registers[register_name] = variable_values[list_tokens[i]]
                    list_tokens[i] = str(variable_values[list_tokens[i]])
                    break    
                
    return list_tokens


def not_signed_unsigned(list_tokens):                
                
    #count number of integers in token list.
    int_list = [int(x) if x.isdigit() else x for x in list_tokens]
    num_integers = sum(isinstance(x, int) for x in int_list)
    
    #look up variables sign status
    variable_sign = variables_sign_status[list_tokens[0]]
    
    # Convert tokens list. Start from the second element.
    if (variable_sign == 'signed'):
        i = 1
        while i < len(int_list):
            if isinstance(int_list[i], int) and int_list[i - 1] == "-" and\
               not isinstance(int_list[i - 2], int):
                neg_num = -int_list[i]
                int_list[i] = neg_num
                del int_list[i - 1]
            i += 1
    
    return int_list, num_integers
    
        
 
def two_operand_arithmetic(integer_list):
            
    operator = integer_list[3]
    registers['eax'] = integer_list[2]
    registers['ebx'] = integer_list[4]
    result = 0
    
    if (integer_list[1] == '='):

        if (operator == '+'):
            result = two_operand_add(registers['eax'], registers['ebx'])
                        
        elif (operator == '-'):
            result = two_operand_sub(registers['eax'], registers['ebx'])
                        
        elif (operator == '*'):
            result = two_operand_mult(registers['eax'], registers['ebx'])
                        
        elif (operator == '/'):
            result = two_operand_div(registers['eax'], registers['ebx'])
    
    registers['ebx'] = result
    return round(result)
                
 
def three_operand_arithmetic(integer_list):
                
    operator1 = integer_list[3]
    operator2 = integer_list[5]
    registers['eax'] = integer_list[2]
    registers['ebx'] = integer_list[4]
    registers['ecx'] = integer_list[6]
    intermediateresult = 0
    finalresult = 0
    
    if (integer_list[1] == '='):
        
        if (operator1 == '+'):
            
            #addsub
            if(operator2 == '-'):
                intermediateresult = two_operand_add(registers['eax'], registers['ebx'])
                registers['eax'] = intermediateresult
                finalresult = two_operand_sub(registers['eax'], registers['ecx'])
            
            #addmult
            elif(operator2 == '*'):
                intermediateresult = two_operand_add(registers['eax'], registers['ebx'])
                registers['eax'] = intermediateresult
                finalresult = two_operand_mult(registers['eax'], registers['ecx'])
            
            #adddiv
            elif(operator2 == '/'):
                intermediateresult = two_operand_add(registers['eax'], registers['ebx'])
                registers['eax'] = intermediateresult
                finalresult = two_operand_div(registers['eax'], registers['ecx'])
                
        elif (operator1 == '-'):
            
            #subadd
            if(operator2 == '+'):
                intermediateresult = two_operand_sub(registers['eax'], registers['ebx'])
                registers['eax'] = intermediateresult
                finalresult = two_operand_add(registers['eax'], registers['ecx'])
            
            #submult
            elif(operator2 == '*'):
                intermediateresult = two_operand_sub(registers['eax'], registers['ebx'])
                registers['eax'] = intermediateresult
                finalresult = two_operand_mult(registers['eax'], registers['ecx'])
            
            #subdiv
            elif(operator2 == '/'):
                intermediateresult = two_operand_sub(registers['eax'], registers['ebx'])
                registers['eax'] = intermediateresult
                finalresult = two_operand_div(registers['eax'], registers['ecx'])
        
        elif(operator1 == '*'):
            
            #multadd
            if (operator2 == '+'):
                intermediateresult = two_operand_mult(registers['eax'], registers['ebx'])
                registers['eax'] = intermediateresult
                finalresult = two_operand_add(registers['eax'], registers['ecx'])
            
            #multsub
            elif(operator2 == '-'):
                intermediateresult = two_operand_mult(registers['eax'], registers['ebx'])
                registers['eax'] = intermediateresult
                finalresult = two_operand_sub(registers['eax'], registers['ecx'])
            
            #multdiv
            elif(operator2 == '/'):
                intermediateresult = two_operand_mult(registers['eax'], registers['ebx'])
                registers['eax'] = intermediateresult
                finalresult = two_operand_div(registers['eax'], registers['ecx'])
        
        elif (operator1 == '/'):
            
            #divadd
            if(operator2 == '+'):
                intermediateresult = two_operand_div(registers['eax'], registers['ebx'])
                registers['eax'] = intermediateresult
                finalresult = two_operand_add(registers['eax'], registers['ecx'])
            
            #divsub
            elif(operator2 == '-'):
                intermediateresult = two_operand_div(registers['eax'], registers['ebx'])
                registers['eax'] = intermediateresult
                finalresult = two_operand_sub(registers['eax'], registers['ecx'])
            
            #divmult
            elif(operator2 == '*'):
                intermediateresult = two_operand_div(registers['eax'], registers['ebx'])
                registers['eax'] = intermediateresult
                finalresult = two_operand_mult(registers['eax'], registers['ecx'])
    
    registers['eax'] = finalresult
    return round(finalresult)
                    

def two_operand_add(op1, op2):
    addresult = op1 + op2
    return addresult

def two_operand_sub(op1, op2):
    subresult = op1 - op2
    return subresult

def two_operand_mult(op1, op2):
    multresult = op1 * op2
    return multresult

def two_operand_div(op1, op2):
    divresult = op1 / op2
    return divresult

def determine_carry_flag(final_result):
    
    max_value = 255    
        
    #converts signed representation to unsigned
    if final_result < 0:
        final_result += 2 ** 8
        
    if final_result > max_value:
        flags['carry'] = 1
    else:
        flags['carry'] = 0
            
def determine_sign_flag(final_result):    
    
    # Convert decimal to binary string
    binary_str = bin(final_result)[2:]
    
    # Remove the 'b' prefix
    if binary_str.startswith('b'):
        binary_str = binary_str[1:]
    
    # Keep only the last 8 bits
    binary_str_8bits = binary_str[-8:]
    
    most_significant_bit = int(binary_str_8bits[0])
    flags['sign'] = most_significant_bit 
    

def determine_zero_flag(final_result):
   
    if final_result == 0:
        flags['zero'] = 1
    else:
        flags['zero'] = 0
       
        
def determine_overflow_flag(arg_list):
    
    op1_binary = None
    op2_binary = None
    op3_binary = None
    op1_signed_num = None
    op2_signed_num = None
    op3_signed_num = None
    operator1 = None
    result = None
    
    # Define a dictionary to map operators to arithmetic operations
    operator_mapping = {
        '*': lambda x, y: x * y,
        '/': lambda x, y: x / y,
        '+': lambda x, y: x + y,
        '-': lambda x, y: x - y
    }
    
    #convert decimal to binary string
    op1_binary = bin(arg_list[2])[2:].zfill(8)
    op2_binary = bin(arg_list[4])[2:].zfill(8)
    op1_signed_num = binary_string_to_signed_int(op1_binary)
    op2_signed_num = binary_string_to_signed_int(op2_binary)
    operator1 = arg_list[3]
    result = operator_mapping[operator1](op1_signed_num, op2_signed_num)
    
    if len(arg_list) == 7:
        op3_binary = bin(arg_list[6])[2:].zfill(8)
        op3_signed_num = binary_string_to_signed_int(op3_binary)
        result = operator_mapping[operator1](result, op3_signed_num)

    if (result < -128 or result > 127):
        flags['overflow'] = 1
    else:
        flags['overflow'] = 0 


def binary_string_to_signed_int(binary_str):
    
    # Remove the 'b' prefix
    if binary_str.startswith('b'):
        binary_str = binary_str[1:].zfill(8)
    
    if binary_str[0] == '1':
        # Convert binary string to signed integer using two's complement
        signed_int = -((int(''.join('1' if bit == '0' else '0' for bit in binary_str), 2) + 1) % (1 << len(binary_str)))
    else:
        signed_int = int(binary_str, 2)
    
    return signed_int



#Convert decimal inputs to Hex values
def convert_operands_to_hex(operand, bit_width=8):
    
    max_value = 2 ** bit_width
    
    try:
        #Convert to integer
        int_value = int(operand)
        
        #Check if negative
        if int_value < 0:
            
            # Compute two's complement for negative numbers
            int_value = max_value + int_value
            
        # Convert to hex (without '0x' prefix)
        hex_value = format(int_value, 'X').zfill(bit_width // 4)  # Each hex digit represents 4 bits
        return hex_value

    except ValueError:
        raise ValueError(f"Invalid operand: {operand}")


#Perform the translation
def translate_to_machine_code(hex_token_list):
    
    instructions=[]
    
    # If two operations exist
    if len(hex_token_list) == 7:
  
        #Get the compound operation mnemonic based on the operators
        operation_mnemonic = operator_to_machine_code.get((hex_token_list[3],\
                                                           hex_token_list[5]))
        if not operation_mnemonic:
            raise ValueError("Unsupported operation pair")
            
        #Write storage instructions
        instructions.extend([
            f"MOV {list(registers.keys())[0]}, {hex_token_list[2].zfill(3)}",
            f"MOV {list(registers.keys())[1]}, {hex_token_list[4].zfill(3)}",
            f"MOV {list(registers.keys())[2]}, {hex_token_list[6].zfill(3)}",
            ])
        
    #If single operation    
    elif len(hex_token_list) == 5:
        operation_mnemonic = operator_to_machine_code.get(hex_token_list[3])
        if not operation_mnemonic:
            raise ValueError("Unsupported operator")
            
        #Write storage instructions
        instructions.extend([
        f"MOV {list(registers.keys())[0]}, {hex_token_list[2].zfill(3)}",
        f"MOV {list(registers.keys())[1]}, {hex_token_list[4].zfill(3)}",
        ])
    
    #mov operation
    elif len(hex_token_list) == 3:
        instructions.extend([
        f"MOV {list(registers.keys())[0]}, {hex_token_list[2].zfill(3)}",
        ])

    #Finalize the instructions to include the operation(s)
    #Two operations
    if len(hex_token_list) == 7:
        instructions.append(f"{operation_mnemonic} {list(register_addresses.keys())[0]}, \
                            {list(registers.keys())[1]}, \
                            {list(registers.keys())[2]}")
    #Single operation    
    elif len(hex_token_list) == 5:
        instructions.append(f"{operation_mnemonic} {list(register_addresses.keys())[0]}, \
                            {list(registers.keys())[1]}")
    
    return '\n'.join(instructions)


def csv_output(input_line, token_hex_list):
    
    file_name = 'output.csv'
    
    with open(file_name, 'a', newline='') as csv_file:
        
        # Create a CSV writer object
        writer = csv.writer(csv_file)
        
        #write HLC to CSV
        writer.writerow([input_line])
        
        if token_hex_list is not None:
            
            #write YMC assembly language to CSV
            machine_code_y = translate_to_machine_code(token_hex_list)
            writer.writerow(machine_code_y)
        
            #write flag values to CSV
            for key, value in flags.items():
                writer.writerow([f'{key}: {value}'])
                
            #new line between each new command for readability    
            writer.writerow('')

def file_input(file_name):
   
    # Open the file for reading
    with open(file_name, 'r') as file:
        
        # Read the file line by line
        for a_line in file:
           main_split(a_line.rstrip('\n'))


#file with code that will be parsed
file = 'input_text.txt'
file_input(file)
