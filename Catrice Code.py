# -*- coding: utf-8 -*-
"""
Created on Tue Mar 26 18:27:14 2024

@author: Catrice, Nicholas
"""
#need hex_tokens and convert_to_hex to be able to handle negative numbers

import re

#set flags
flags = {
    'carry': 0,
    'sign': 0,
    'zero': 0,
    'overflow': 0
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

#Registers list
registers = {
    'eax': 0,
    'ebx': 0,
    'ecx': 0,
    'edx': 0
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

def split_program_into_lines(program):
    # Split the program into lines
    lines = program.splitlines()

    # Iterate over each line in the program
    for line in lines:
        
        # Tokenize the current line using regular expressions
        tokens = re.findall(r'[a-zA-Z_]+|[\d]+|[+*/=\-<>]', line)
        
        
        #determine and store variables signed or unsigned status
        if (tokens[0] == 'unsigned' or 'signed'):
            for i in range(1, len(tokens)):
                variable_name = tokens[i]
                if variable_name in variables_sign_status:
                    variables_sign_status[variable_name] = tokens[0]  
                    
        
        #translate arithmetic or comparison line into machine code
        if tokens[0] not in ['unsigned', 'signed']:
        
            #count number of integers in token list.
            int_list = [int(x) if x.isdigit() else x for x in tokens]
            num_integers = sum(isinstance(x, int) for x in int_list)
 
            
            #look up variables sign status
            variable_sign = variables_sign_status[tokens[0]]
            
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
            
            hex_tokens = [convert_operands_to_hex(token) if \
                          isinstance(token, str) and token.isdigit() \
                          else token for token in tokens]
                
            machine_code_y = translate_to_machine_code(hex_tokens)
            print(machine_code_y)
                
            
            if (num_integers == 2):
                
                operator = int_list[3]
                operand1 = int_list[2]
                operand2 = int_list[4]
                result = 0
                
                if (tokens[1] == '='):
    
                    if (operator == '+'):
                        result = two_operand_add(operand1, operand2)
                                    
                    elif (operator == '-'):
                        result = two_operand_sub(operand1, operand2)
                                    
                    elif (operator == '*'):
                        result = two_operand_mult(operand1, operand2)
                                    
                    elif (operator == '/'):
                        result = two_operand_div(operand1, operand2)
                        
                determine_carry_flag(result)
                determine_sign_flag(result)
                determine_zero_flag(result)
                determine_overflow_flag(int_list)
    
            
            elif (num_integers == 3):
                
                operator1 = int_list[3]
                operator2 = int_list[5]
                operand1 = int_list[2]
                operand2 = int_list[4]
                operand3 = int_list[6]
                intermediateresult = 0
                finalresult = 0
                
                if (tokens[1] == '='):
                    
                    if (operator1 == '+'):
                        
                        #addsub
                        if(operator2 == '-'):
                            intermediateresult = two_operand_add(operand1, operand2)
                            finalresult = two_operand_sub(intermediateresult, operand3)
                        
                        #addmult
                        elif(operator2 == '*'):
                            intermediateresult = two_operand_add(operand1, operand2)
                            finalresult = two_operand_mult(intermediateresult, operand3)
                        
                        #adddiv
                        elif(operator2 == '/'):
                            intermediateresult = two_operand_add(operand1, operand2)
                            finalresult = two_operand_div(intermediateresult, operand3)
                            
                    elif (operator1 == '-'):
                        
                        #subadd
                        if(operator2 == '+'):
                            intermediateresult = two_operand_sub(operand1, operand2)
                            finalresult = two_operand_add(intermediateresult, operand3)
                        
                        #submult
                        elif(operator2 == '*'):
                            intermediateresult = two_operand_sub(operand1, operand2)
                            finalresult = two_operand_mult(intermediateresult, operand3)
                        
                        #subdiv
                        elif(operator2 == '/'):
                            intermediateresult = two_operand_sub(operand1, operand2)
                            finalresult = two_operand_div(intermediateresult, operand3)
                    
                    elif(operator1 == '*'):
                        
                        #multadd
                        if (operator2 == '+'):
                            intermediateresult = two_operand_mult(operand1, operand2)
                            finalresult = two_operand_add(intermediateresult, operand3)
                        
                        #multsub
                        elif(operator2 == '-'):
                            intermediateresult = two_operand_mult(operand1, operand2)
                            finalresult = two_operand_sub(intermediateresult, operand3)
                        
                        #multdiv
                        elif(operator2 == '/'):
                            intermediateresult = two_operand_mult(operand1, operand2)
                            finalresult = two_operand_div(intermediateresult, operand3)
                    
                    elif (operator1 == '/'):
                        
                        #divadd
                        if(operator2 == '+'):
                            intermediateresult = two_operand_div(operand1, operand2)
                            finalresult = two_operand_add(intermediateresult, operand3)
                        
                        #divsub
                        elif(operator2 == '-'):
                            intermediateresult = two_operand_div(operand1, operand2)
                            finalresult = two_operand_sub(intermediateresult, operand3)
                        
                        #divmult
                        elif(operator2 == '*'):
                            intermediateresult = two_operand_div(operand1, operand2)
                            finalresult = two_operand_mult(intermediateresult, operand3)
            
                determine_carry_flag(finalresult)
                determine_sign_flag(finalresult)
                determine_zero_flag(result)
                determine_overflow_flag(int_list)
            

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
            f"MOV {list(registers.keys())[2]}, {hex_token_list[2].zfill(3)}",
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
        instructions.append(f"{operation_mnemonic} {list(registers.keys())[0]}, \
                            {list(registers.keys())[1]}, \
                            {list(registers.keys())[2]}")
    #Single operation    
    elif len(hex_token_list) == 5:
        instructions.append(f"{operation_mnemonic} {list(registers.keys())[0]}, \
                            {list(registers.keys())[1]}")
    
    return '\n'.join(instructions)


#main
program = """ unsigned a, b, c
signed a
unsigned x, y
signed z
a = -128 - 1
"""

split_program_into_lines(program)