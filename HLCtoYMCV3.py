# -*- coding: utf-8 -*-
"""
Created on Fri Apr  5 11:37:58 2024

@author: Nick
"""

"""

HLC to YMC to MC conversion Flowchart Model
V2 includes variable support, negative number support(Sort of) and CSV log save functions
V3 includes input file option

Created on Monday Apr 04 3:59:58 2024

@author: Nicholas Grencz
With code from: Catrice English

TODO 
    finish negative number support
    format output to match example
    write the correct values in each column to CSV
    
"""
#Import Libraries

import re #The Regular Expressions Library
import csv #The CSV File Storage Library
from colorama import init, Fore, Style

#initialize color
init(autoreset=True)
#Define Variables, Lists and Dictionaries

#Map operations to our YMC Address Values
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

#Registers list
registers = ['eax', 'ebx', 'ecx', 'edx']

#Map Registers to addresses
register_addresses = {
    'eax': 'F01',
    'ebx': 'F02',
    'ecx': 'F03',
    'edx': 'F04'
}

#variable list
variables = ['a', 'b', 'c', 'x', 'y','z']

#Map variables to memory addresses
variable_addresses = {
    'a': '[000]',
    'b': '[001]',
    'c': '[002]',
    'x': '[003]',
    'y': '[004]',
    'z': '[005]'
    }

#declare csv file name and column headers
filename = 'Output.csv'
csv_headers = ['HLC Instruction', 'YMC Address', 'YMC Assembly', 'YMC encoding','Modified Registers', 'Modified Flags']

#Sanitize inputs for negative values (deals with leading negatives and double operators)
def sanitize_expression(expression):
   
    # Strip whitespace from the expression
    expression = expression.strip()

    # Replace double operators (like '+-', '--') with a single '-' if it is subtraction
    expression = re.sub(r'\+-|-\+', '-', expression)
    expression = re.sub(r'-{2,}', '+', expression)  # Handling '--' can be context dependent

    # If the string starts with a negative sign, add a zero in front to avoid confusion with subtraction
    if expression.startswith('-'):
        expression = '0' + expression

    return expression

#Parse input into operands and operators
def parse_expression(expression):
    
    parts = re.findall(r'\d+|\+|\-|\*|\/', expression)
    
    #Determine number of operands and return them as applicable
    if len(parts) == 3:
        operand1, operator, operand2 = parts
        return operand1, operator, operand2, None, None
    elif len(parts) == 5:
        return parts
    else:
        raise ValueError("Expression must have one or two operands.")
        
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
        hex_value = format(int_value, 'X').zfill(3)  # Each hex digit represents 4 bits
        return hex_value
    except ValueError:
        raise ValueError(f"Invalid operand: {operand}")
        

#format the input into the correct syntax for our YMC
def format_expression_with_hex(expression): 
    
    #Use reg expression to find all numbers and arithmetic operators
    tokens = re.findall(r'\d+|\+|\-|\*|\/', expression)
    #Convert all numeric tokens to hexadecimal
    tokens = [convert_operands_to_hex(token) if token.isdigit() else token for token in tokens]
    return ' '.join(tokens)

#Perform the translation
def translate_to_machine_code(operand1, operator1, operand2, operator2=None, operand3=None):
    
    instructions = []

    if operator2:  # If two operations exist
        #Get the compound operation mnemonic based on the operators
        operation_mnemonic = operator_to_machine_code.get((operator1, operator2))
        if not operation_mnemonic:
            raise ValueError("Unsupported operation pair")
            
        #Write storage instructions
        instructions.extend([
            f"MOV {registers[0]}, {operand1.zfill(3)}",
            f"MOV {registers[1]}, {operand2.zfill(3)}",
            f"MOV {registers[2]}, {operand3.zfill(3)}",
        ])
    else:  #If single operation
        operation_mnemonic = operator_to_machine_code.get(operator1)
        if not operation_mnemonic:
            raise ValueError("Unsupported operator")
            
        #Write storage instructions
        instructions.extend([
            f"MOV {registers[0]}, {operand1.zfill(3)}",
            f"MOV {registers[1]}, {operand2.zfill(3)}",
        ])

    #Finalize the instructions to include the operation(s)
    if operator2:
        #Two operations
        instructions.append(f"{operation_mnemonic} {registers[0]}, {registers[1]}, {registers[2]}")
    else:
        #Single operation
        instructions.append(f"{operation_mnemonic} {registers[0]}, {registers[1]}")
    
    return '\n'.join(instructions)

#For S&G - Convert the output to its hex code equivalent
def ymc_to_mc(instruction_str):
    
    #Split instructions into components by the comma
    components = instruction_str.split(',')
    
    #Get the mnemonic without spaces
    operator_mnemonic = components[0].split()[0].strip().lower()  
    
    #Retrieve the corresponding opcode
    opcode = opcodes.get(operator_mnemonic, "")  

    #Strip and define Operands
    operand_parts = [part.strip() for part in components[1:]]  
    operand_components = []
    for part in operand_parts:
        
        #If part is register
        if part in register_addresses:  
            operand_components.append(register_addresses[part])
            
        #If part is number
        else:  
            operand_components.append(convert_operands_to_hex(part))

    #Construct final machine code string by joining with spaces
    mc_instruction = f"{opcode} {' '.join(operand_components)}"
    return mc_instruction

#Check if file exists. If not create a new file and write the column headers to that file
with open(filename, 'a', newline='') as csvfile:
    writer = csv.writer(csvfile)
    if csvfile.tell() == 0:
        writer.writerow(csv_headers)

def get_input_filename():
    filename = input("Enter the filename: ")
    if not filename.lower().endswith(".txt"):
        filename += ".txt"
    return filename

def extract_instructions(input_file_path):
    instructions = []
    with open(input_file_path, 'r') as file:
        for line in file:
            instruction = line.strip()  # Remove any leading/trailing whitespace characters
            if instruction:  # Skip empty lines
                instructions.append(instruction)
    return instructions
                
#process a single line of instructions
def process_instruction(instruction):
    try:
        # Perform your instruction operations here...
        sanitized_op = sanitize_expression(instruction)
        formatted_op = format_expression_with_hex(sanitized_op)
        operand1, operator1, operand2, operator2, operand3 = parse_expression(formatted_op)
        
        machine_code_y = translate_to_machine_code(
            operand1, operator1, operand2, operator2, operand3
        )

        # Split the YMC into individual lines and get hex representation
        ymc_instructions = machine_code_y.strip().split('\n')
        mc_instructions_hex = [ymc_to_mc(instruction) for instruction in ymc_instructions if instruction]

        # Write results to CSV if needed
        with open('output.csv', 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            ymc_output = '\n'.join(ymc_instructions)
            mc_output = '\n'.join(mc_instructions_hex)
            writer.writerow([instruction, ymc_output, mc_output])

        return machine_code_y, mc_instructions_hex

    except ValueError as e:
        print(f"An error occurred: {e}")
        return None, None

#MAIN
if __name__ == "__main__":
   
    print(Style.BRIGHT + Fore.GREEN)
    #Welcome Message and Instructions for Use
    print("*"*25, "Welcome to the code translator!", "*"*25)
    print("This program will translate any simple arithmetic operation into the YMC language.")
    print("Acceptable arithmetic operations are: +, -, *, /. ")
    print("Parameters may include up to two operands per iteration.")
    print("Numbers allowable range from -128 to 127")
    print("This program will also allow you to see the resulting operation in MC (Hex) by selecting \"y\" when prompted")
    print()
   
    #Start an infinite loop for operation inputs (breakable by blank input)
    
    while True:
        try:
            action = input(f"{Fore.YELLOW}Open a file [F], enter manual command [M], or exit [Enter]: ").strip().upper()
                        
            if action == 'F':
                input_file_path = get_input_filename()
                instructions = extract_instructions(input_file_path)
                
                for instruction in instructions:
                    machine_code_y, mc_instructions_hex = process_instruction(instruction)
                    if machine_code_y and mc_instructions_hex:
                        # Assume ymc_to_mc returns a single string instead of a list
                        print(f"YMC instructions for '{instruction}': {machine_code_y}")
                        print(f"MC (hex) instructions: {','.join(mc_instructions_hex)}")
                        print()

            elif action == 'M':
                command = input("Enter arithmetic operation (or press Enter to exit): ")
                if not command:
                    break  
                
                # Process the manual command
                machine_code_y, mc_instructions_hex = process_instruction(command)
                if machine_code_y and mc_instructions_hex:
                    print(f"YMC instructions for '{command}': {machine_code_y}")
                    print(f"MC (hex) instructions: {','.join(mc_instructions_hex)}")
                    print()

            elif action == '':
                break  # Exit the loop if an empty string is entered

            else:
                print("Unknown action. Please try 'F', 'M', or press Enter to exit.")

        except ValueError as e:
            print(f"An error occurred: {e}")