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

#first column is mapping and second item in the list is the value of the register
registers = {
    'eax': ['F01', None],
    'ebx': ['F02', None],
    'ecx': ['F03', None],
    'edx': ['F04', None]
}

#variable values - first item in list is memory address, second item is value of
#variable, third item is variables sign status.
variable_values = {
    'a': ['000', None, None],
    'b': ['001', None, None],
    'c': ['002', None, None],
    'x': ['003', None, None],
    'y': ['004', None, None],
    'z': ['005', None, None]
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

    # Tokenize the current line using regular expressions
    tokens = re.findall(r'[a-zA-Z_]+|[\d]+|[+*/=\-<>]', line)
    
    #if blank line
    if len(tokens) == 0:
        tokens = None
        num_modified_registers = 0
        
    #determine if line is variable declaration line
    elif tokens[0] in ['unsigned', 'signed']:
        
        #if the value located at tokens[0] is either 'signed' or 'unsigned'
        signed_unsigned(tokens)
        
        tokens = None
        num_modified_registers = 0

    #line is an arithmetic line    
    else:
      
        #process negative numbers and convert numbers from the tokens list
        #from string to int
        integer_list = not_signed_unsigned(tokens)
        
        #move variable or immediate value to a register for computation. Count
        #the number of registers modified
        num_modified_registers, tokens = move_mem_register(integer_list)
        
        
        #determine appropriate arithmetic to perform based on number of
        #registers modified as the registers always hold the integer values
        #before they are moved to memory.
        if (num_modified_registers == 2):
            two_operand_arithmetic(integer_list)
        elif (num_modified_registers == 3):
            three_operand_arithmetic(integer_list)
      
       
        #assign result located in register eax to variable in 
        #variable_values dictionary. Variable_values dictionary represents memory
        if tokens[0] in variable_values:
            variable_values[tokens[0]][1] = registers['eax'][1]

       
        #set flags if arithmetic 
        if(num_modified_registers == 2 or num_modified_registers == 3):
            determine_carry_flag(registers['eax'][1])
            determine_sign_flag(registers['eax'][1])
            determine_zero_flag(registers['eax'][1])
            determine_overflow_flag(integer_list)
        
  
    #write headers if file empty
    write_headers()
    
    #output to csv
    csv_output(line, tokens, num_modified_registers)

    #reset the registers
    for items in registers:
        registers[items][1] = None
    
    

#function for variable declaration line to assign a variables sign status
def signed_unsigned(list_tokens):
   
    
    # Iterate over list_tokens starting from index 1
    for i in range(1, len(list_tokens)):
        variable_name = list_tokens[i]
        
        # Check if the variable_name exists in variable_values
        if variable_name in variable_values:
            
            #set variables sign status equal to the value located at 
            #list_tokens[0].
            variable_values[variable_name][2] = list_tokens[0]  


def not_signed_unsigned(list_tokens):                
                
    #convert integers from string to int type, i.e. ['2', +, '3'] to [2, '+', 3]
    int_list = [int(x) if x.isdigit() else x for x in list_tokens]
    
    #look up variables sign status
    variable_sign = variable_values[list_tokens[0]][2]

    # Convert tokens list if negative value. Start from the second element.
    #this will convert somthing that looks like ['1', '*', '-', '2'] to
    #['1', '*', -2]
    if (variable_sign == 'signed'):
        i = 1
        while i < len(int_list):
            
            #if token at i is an int, the token at before i is '-' and the
            #the token at [i-2] is not an integer. if the token at [i-2] is an
            #integer the '-' sign means minus not negative.
            if isinstance(int_list[i], int) and int_list[i - 1] == "-" and\
               not isinstance(int_list[i - 2], int):
                neg_num = -int_list[i]
                int_list[i] = neg_num
                del int_list[i - 1]
            i += 1
    
    #if int_list[i] is a variable look up value in memory. This line will replace
    #a variable in int_list with the value of the variable, i.e. ['a', '+', 'b']
    #to [5, '+', 2].
    for i in range(2, len(int_list)):
        if int_list[i] in variable_values:
            int_list[i] = variable_values[int_list[i]][1]          
    return int_list
    
            
def move_mem_register(list_tokens):
    
    count_mod_reg = 0
    modified_list_tokens = list_tokens[:]
 
    
    for i in range(2, len(modified_list_tokens)):
        
        #check if the token in modified_token_list exists in variable_values.
        #For example, check if the token is 'a' and if 'a' exists in variable_values
        if modified_list_tokens[i] in variable_values:
            for register_name in registers:
                
                #iterate through the registers until an empty one is found
                if registers[register_name][1] is None:
                    
                    #assign the empty register to the value of the variable
                    #located in memory
                    registers[register_name][1] = variable_values[list_tokens[i]][1]
                    
                    modified_list_tokens[i] = str(variable_values[list_tokens[i]][1])
                    count_mod_reg +=1
                    break    
        
        # Check if the token at index i is an integer
        elif isinstance(list_tokens[i], int):
            for register_name, values in registers.items():
                
                #iterate through the registers until an empty one is found
                if values[1] is None:
                    
                    #assign the empty register to the value of the integer
                    #located at token[i]
                    registers[register_name][1] = list_tokens[i]
                    modified_list_tokens[i] = str(modified_list_tokens[i])
                    count_mod_reg +=1
                    break
    
    return count_mod_reg, modified_list_tokens

     
 
def two_operand_arithmetic(integer_list):
            
    operator = integer_list[3]
    result = 0
    
    if (integer_list[1] == '='):
        
        #add
        if (operator == '+'):
            result = two_operand_add(registers['eax'][1], registers['ebx'][1])
        
        #sub                
        elif (operator == '-'):
            result = two_operand_sub(registers['eax'][1], registers['ebx'][1])
            
        #mult                
        elif (operator == '*'):
            result = two_operand_mult(registers['eax'][1], registers['ebx'][1])
        
        #div                
        elif (operator == '/'):
            result = two_operand_div(registers['eax'][1], registers['ebx'][1])
    
    registers['eax'][1] = result
                
 
def three_operand_arithmetic(integer_list):

    operator1 = integer_list[3]
    operator2 = integer_list[5]
    intermediateresult = 0
    finalresult = 0
    
    if (integer_list[1] == '='):
        
        if (operator1 == '+'):
            
            #addsub
            if(operator2 == '-'):
                intermediateresult = two_operand_add(registers['eax'][1], registers['ebx'][1])
                registers['eax'][1] = intermediateresult
                finalresult = two_operand_sub(registers['eax'][1], registers['ecx'][1])
            
            #addmult
            elif(operator2 == '*'):
                intermediateresult = two_operand_add(registers['eax'][1], registers['ebx'][1])
                registers['eax'][1] = intermediateresult
                finalresult = two_operand_mult(registers['eax'][1], registers['ecx'][1])
            
            #adddiv
            elif(operator2 == '/'):
                intermediateresult = two_operand_add(registers['eax'][1], registers['ebx'][1])
                registers['eax'][1] = intermediateresult
                finalresult = two_operand_div(registers['eax'][1], registers['ecx'][1])
                
        elif (operator1 == '-'):
            
            #subadd
            if(operator2 == '+'):
                intermediateresult = two_operand_sub(registers['eax'][1], registers['ebx'][1])
                registers['eax'][1]= intermediateresult
                finalresult = two_operand_add(registers['eax'][1], registers['ecx'][1])
            
            #submult
            elif(operator2 == '*'):
                intermediateresult = two_operand_sub(registers['eax'][1], registers['ebx'][1])
                registers['eax'][1] = intermediateresult
                finalresult = two_operand_mult(registers['eax'][1], registers['ecx'][1])
            
            #subdiv
            elif(operator2 == '/'):
                intermediateresult = two_operand_sub(registers['eax'][1], registers['ebx'][1])
                registers['eax'][1] = intermediateresult
                finalresult = two_operand_div(registers['eax'][1], registers['ecx'][1])
        
        elif(operator1 == '*'):
            
            #multadd
            if (operator2 == '+'):
                intermediateresult = two_operand_mult(registers['eax'][1], registers['ebx'][1])
                registers['eax'][1] = intermediateresult
                finalresult = two_operand_add(registers['eax'][1], registers['ecx'][1])
            
            #multsub
            elif(operator2 == '-'):
                intermediateresult = two_operand_mult(registers['eax'][1], registers['ebx'][1])
                registers['eax'][1] = intermediateresult
                finalresult = two_operand_sub(registers['eax'][1], registers['ecx'][1])
            
            #multdiv
            elif(operator2 == '/'):
                intermediateresult = two_operand_mult(registers['eax'][1], registers['ebx'][1])
                registers['eax'][1] = intermediateresult
                finalresult = two_operand_div(registers['eax'][1], registers['ecx'][1])
        
        elif (operator1 == '/'):
            
            #divadd
            if(operator2 == '+'):
                intermediateresult = two_operand_div(registers['eax'][1], registers['ebx'][1])
                registers['eax'][1] = intermediateresult
                finalresult = two_operand_add(registers['eax'][1], registers['ecx'][1])
            
            #divsub
            elif(operator2 == '-'):
                intermediateresult = two_operand_div(registers['eax'][1], registers['ebx'][1])
                registers['eax'][1] = intermediateresult
                finalresult = two_operand_sub(registers['eax'][1], registers['ecx'][1])
            
            #divmult
            elif(operator2 == '*'):
                intermediateresult = two_operand_div(registers['eax'][1], registers['ebx'][1])
                registers['eax'][1] = intermediateresult
                finalresult = two_operand_mult(registers['eax'][1], registers['ecx'][1])
    
    registers['eax'][1] = finalresult
                    

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
        
        #calculate twos complelemt for negative numbers
        final_result += 2 ** 8
        
    if final_result > max_value:
        flags['carry'] = 1
    else:
        flags['carry'] = 0
            
def determine_sign_flag(final_result):    
    print(final_result)
    if final_result < 0:
        flags['sign'] = 1
    else:
        flags['sign'] = 0
    

def determine_zero_flag(final_result):
   
    if final_result == 0:
        flags['zero'] = 1
    else:
        flags['zero'] = 0
       
        
def determine_overflow_flag(arg_list):
    
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
    
    #determine what the signed value is from the binary string
    op1_signed_num = binary_string_to_signed_int(op1_binary)
    op2_signed_num = binary_string_to_signed_int(op2_binary)
    
    
    operator1 = arg_list[3]
    result = operator_mapping[operator1](op1_signed_num, op2_signed_num)

    #if there are 3 operands
    if len(arg_list) == 7:
        operator2 = arg_list[5]
        op3_binary = bin(arg_list[6])[2:].zfill(8)
        op3_signed_num = binary_string_to_signed_int(op3_binary)
        result = operator_mapping[operator2](result, op3_signed_num)
        

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
        instructions.append(f"{operation_mnemonic} {list(registers.keys())[0]}, \
                            {list(registers.keys())[1]}, \
                            {list(registers.keys())[2]}")
    #Single operation    
    elif len(hex_token_list) == 5:
        instructions.append(f"{operation_mnemonic} {list(registers.keys())[0]}, \
                            {list(registers.keys())[1]}")
    
    return '\n'.join(instructions)

def ymc_to_mc(instruction_str):
    
    #Split instructions into components by the comma
    components = instruction_str.split(',')
    
    #Get the mnemonic without spaces
    operator_mnemonic = components[0].split()[0].strip().lower() 
    
    #Retrieve the corresponding opcode
    opcode = opcodes.get(operator_mnemonic, "")  
    
    operand_parts = [part.strip() for part in components[1:]]  
    operand_components = []
    
    for part in operand_parts:
        
        #If part is variable located in register
        if part in registers:  
            operand_components.append(registers[part][0])
        
        #If part is number
        else: 
            operand_components.append(part)
    
    mc_instruction = f"{opcode} {' '.join(operand_components)}"
    return mc_instruction

def write_headers():
    
    file_name = 'output.csv'
    headers=['HLC','YMC Assembly', 'YMC Encoding', 'Modified Registers', 'Modified Flags']
  
    try:
        
       with open(file_name, 'r') as csvfile:
           
           #Check if file is empty
           first_char = csvfile.read(1)
           empty = not first_char

       # Write headers if file is empty
       if empty:
           with open(file_name, 'a', newline='') as csvfile:
               writer = csv.writer(csvfile)
               writer.writerow(headers)
               
    except FileNotFoundError:
       
       # If the file doesn't exist, write headers
       with open(file_name, 'w', newline='') as csvfile:
           writer = csv.writer(csvfile)
           writer.writerow(headers)
    
    
def csv_output(a_line, tokens_list, number_mod_reg):
    
    file_name = 'output.csv'
    combination=[]
    assembly=[]
    
    #Output HLC to CSV file if a_line is not empty
    if a_line.strip():
        combination.append(a_line)


    if tokens_list is not None: 
        
        #machine code
        hex_tokens = [convert_operands_to_hex(token) if \
                      isinstance(token, str) and token.isdigit() \
                      else token for token in tokens_list]
        machine_code_y = translate_to_machine_code(hex_tokens)
        combination.append(machine_code_y)
        
        #assembly
        ymc_instructions = machine_code_y.strip().split('\n')
        mc_instructions_hex = [ymc_to_mc(instruction) for instruction in ymc_instructions if instruction]
        for instruction in mc_instructions_hex:
            assembly.append(instruction)
        assembly_string = '\n'.join(assembly)
        combination.append(assembly_string)
        
        #modified registers
        if number_mod_reg == 1:
            combination.append('eax')
        elif number_mod_reg == 2:
            combination.append('eax, ebx')
        elif number_mod_reg == 3:
            combination.append('eax, ebx, ecx')  
            

        #flags
        flags_string = '\n'.join([f"{key}: {value}" for key, value in flags.items()])
        combination.append(flags_string)
    
    with open(file_name, 'a', newline='') as csv_file:
        
        # Create a CSV writer object
        writer = csv.writer(csv_file)
        
        if combination:
            writer.writerow(combination)


def file_input(file_name):
   
    # Open the file for reading
    with open(file_name, 'r') as file:
        
        # Read the file line by line
        for a_line in file:
           main_split(a_line.rstrip('\n'))


#file with code that will be parsed
file = 'input_text.txt'
file_input(file)
