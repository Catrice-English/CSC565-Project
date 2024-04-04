# -*- coding: utf-8 -*-
"""
Created on Tue Mar 26 18:27:14 2024

@author: Catrice, Nicholas
"""

import re

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
        
        #translate line into machine code
        machine_code_y = translate_to_machine_code(hex_tokens)
        print(machine_code_y)
        
        #the below code will compute the end state of each line in the program.
        #count the number of parts in each line to classify which type of
        #operation they belong to.
        #if number of parts is 3 then we know the operation is a mov operation
        # or a compare operation
        
        num_tokens = len(tokens)
        if (num_tokens == 3):
            
            if (tokens[1] == '='):
            
                #moving a value from one register to another register
                if tokens[2] in registers:
                    registers[tokens[0]] = registers[tokens[2]]
                    
                #moving an immediate value into a register
                else:
                    hex_token2 = convert_operands_to_hex(int(tokens[2]))
                    registers[tokens[0]] = hex_token2
        
        
        #if number of parts is 5 then we know the operation is a two operand
        #arithmetic operation or a compare operation.
        elif (num_tokens == 5):
            
            operator = tokens[3]
            operand1 = tokens[2]
            operand2 = tokens[4]
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

    
            registers[tokens[0]] = convert_operands_to_hex(result)
        
        elif (num_tokens == 7):
            
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
            
            registers[tokens[0]] = convert_operands_to_hex(finalresult)
            
            

def two_operand_add(op1, op2):
    if op2 in registers:
        addresult = int(registers[op1], 16) + (int(registers[op2], 16) \
        if op1 in registers else int(op1))
    else:
        addresult = (int(registers[op1], 16) if op1 in registers else int(op1)) \
        + int(op2)
    
    return addresult

def two_operand_sub(op1, op2):
    if op2 in registers:
        subresult = int(registers[op1], 16) - (int(registers[op2], 16) \
        if op1 in registers else int(op1))
    else:
        subresult = (int(registers[op1], 16) if op1 in registers else int(op1)) \
        - int(op2)
    
    return subresult

def two_operand_mult(op1, op2):
    if op2 in registers:
        multresult = int(registers[op1], 16) * (int(registers[op2], 16) \
        if op1 in registers else int(op1))
    else:
        multresult = (int(registers[op1], 16) if op1 in registers else int(op1)) \
        * int(op2)
    
    return multresult

def two_operand_div(op1, op2):
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
program = """ y=2+3-1
 y=5-10
 y=5
"""

split_program_into_lines(program)
