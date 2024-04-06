# -*- coding: utf-8 -*-
"""
Created on Tue Mar 26 18:27:14 2024

@author: Catrice, Nicholas
"""

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
        hex_tokens = [convert_operands_to_hex(token) if token.isdigit() \
                      else token for token in tokens]
            
        #determine and store variables signed or unsigned status
        if (tokens[0] == 'unsigned' or 'signed'):
            for i in range(1, len(tokens)):
                variable_name = tokens[i]
                if variable_name in variables_sign_status:
                    variables_sign_status[variable_name] = tokens[0]  
                    
        
        #translate arithmetic or comparison line into machine code
        if tokens[0] not in ['unsigned', 'signed']:
            machine_code_y = translate_to_machine_code(hex_tokens)
            print(machine_code_y)
        
            #count number of integers in token list.
            int_list = [int(x) if x.isdigit() else x for x in tokens]
            num_integers = sum(isinstance(x, int) for x in int_list)
            
            print(int_list)
            
            
            #look up variables sign status
            variable_sign = variables_sign_status[tokens[0]]
            
            # Convert tokens list
            for i in range(1, len(int_list)-1):
                if isinstance(int_list[i], int) and int_list[i - 1] == "-":
                    neg_num = -int_list[i]
                    int_list[i] = neg_num
                    del int_list[i - 1]
            
            print(int_list)
            
            if (num_integers == 2):
                
                operator = tokens[3]
                operand1 = 0
                operand2 = 0
                result = 0
                
                if (tokens[1] == '='):
    
                    if (operator == '+'):
                        result = two_operand_add(tokens, variable_sign)
                                    
                    elif (operator == '-'):
                        result = two_operand_sub(operand1, operand2, \
                                                 variable_sign)
                                    
                    elif (operator == '*'):
                        result = two_operand_mult(operand1, operand2, \
                                                  variable_sign)
                                    
                    elif (operator == '/'):
                        result = two_operand_div(operand1, operand2, \
                                                 variable_sign)
    
        
                registers[tokens[0]] = convert_operands_to_hex(result)
            
            elif (num_integers == 3):
                
                operator1 = tokens[3]
                operator2 = tokens[5]
                operand1 = tokens[2]
                operand2 = tokens[4]
                operand3 = tokens[6]
                intermediateresult = 0
                finalresult = 0
                
                if (tokens[1] == '='):
                    
                    if (operator1 == '+'):
                        
                        #addsub
                        if(operator2 == '-'):
                            intermediateresult = two_operand_add\
                                (operand1, operand2, variable_sign)
                            finalresult = two_operand_sub\
                                (intermediateresult, operand3, variable_sign)
                        
                        #addmult
                        elif(operator2 == '*'):
                            intermediateresult = two_operand_add\
                                (operand1, operand2, variable_sign)
                            finalresult = two_operand_mult\
                                (intermediateresult, operand3, variable_sign)
                        
                        #adddiv
                        elif(operator2 == '/'):
                            intermediateresult = two_operand_add\
                                (operand1, operand2, variable_sign)
                            finalresult = two_operand_div\
                                (intermediateresult, operand3, variable_sign)
                            
                    elif (operator1 == '-'):
                        
                        #subadd
                        if(operator2 == '+'):
                            intermediateresult = two_operand_sub\
                                (operand1, operand2, variable_sign)
                            finalresult = two_operand_add\
                                (intermediateresult, operand3, variable_sign)
                        
                        #submult
                        elif(operator2 == '*'):
                            intermediateresult = two_operand_sub\
                                (operand1, operand2, variable_sign)
                            finalresult = two_operand_mult\
                                (intermediateresult, operand3, variable_sign)
                        
                        #subdiv
                        elif(operator2 == '/'):
                            intermediateresult = two_operand_sub\
                                (operand1, operand2, variable_sign)
                            finalresult = two_operand_div\
                                (intermediateresult, operand3, variable_sign)
                    
                    elif(operator1 == '*'):
                        
                        #multadd
                        if (operator2 == '+'):
                            intermediateresult = two_operand_mult\
                                (operand1, operand2, variable_sign)
                            finalresult = two_operand_add\
                                (intermediateresult, operand3, variable_sign)
                        
                        #multsub
                        elif(operator2 == '-'):
                            intermediateresult = two_operand_mult\
                                (operand1, operand2, variable_sign)
                            finalresult = two_operand_sub\
                                (intermediateresult, operand3, variable_sign)
                        
                        #multdiv
                        elif(operator2 == '/'):
                            intermediateresult = two_operand_mult\
                                (operand1, operand2, variable_sign)
                            finalresult = two_operand_div\
                                (intermediateresult, operand3, variable_sign)
                    
                    elif (operator1 == '/'):
                        
                        #divadd
                        if(operator2 == '+'):
                            intermediateresult = two_operand_div\
                                (operand1, operand2, variable_sign)
                            finalresult = two_operand_add\
                                (intermediateresult, operand3, variable_sign)
                        
                        #divsub
                        elif(operator2 == '-'):
                            intermediateresult = two_operand_div\
                                (operand1, operand2, variable_sign)
                            finalresult = two_operand_sub\
                                (intermediateresult, operand3, variable_sign)
                        
                        #divmult
                        elif(operator2 == '*'):
                            intermediateresult = two_operand_div\
                                (operand1, operand2, variable_sign)
                            finalresult = two_operand_mult\
                                (intermediateresult, operand3, variable_sign)
                
                registers[tokens[0]] = convert_operands_to_hex(finalresult)
            
            

def two_operand_add(token_list, sign_status):
    if sign_status == 'unsigned':
        addresult = int(token_list[2]) + int(token_list[4])
    
    #sign_status = signed
    else:
        int_indices = []
        operands = []
        
        for index, element in enumerate(token_list):
            if element.isdigit():
                int_indices.append(index)
        
        for i in int_indices:
            if token_list[i-1] == '-':
                num_string = ''.join(token_list[i-1], token_list[i])
                operands.append(int(num_string))
        
        addresult = sum(operands)
        print(addresult)
                
    return addresult

def two_operand_sub(op1, op2, sign_status):
    if op2 in registers:
        subresult = int(registers[op1], 16) - (int(registers[op2], 16) \
        if op1 in registers else int(op1))
    else:
        subresult = (int(registers[op1], 16) if op1 in registers else int(op1)) \
        - int(op2)
    
    return subresult

def two_operand_mult(op1, op2, sign_status):
    if op2 in registers:
        multresult = int(registers[op1], 16) * (int(registers[op2], 16) \
        if op1 in registers else int(op1))
    else:
        multresult = (int(registers[op1], 16) if op1 in registers else int(op1)) \
        * int(op2)
    
    return multresult

def two_operand_div(op1, op2, sign_status):
    if op2 in registers:
        divresult = int(registers[op1], 16) / (int(registers[op2], 16) \
        if op1 in registers else int(op1))
    else:
        divresult = (int(registers[op1], 16) if op1 in registers else int(op1)) \
        / int(op2)
    
    return divresult


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
    else:
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
a = -5 + 2
"""

split_program_into_lines(program)
