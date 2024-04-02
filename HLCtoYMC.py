"""

HLC to YMC to MC conversion Flowchart Model


Created on Monday Apr 04 3:59:58 2024

@author: Nicholas Grencz
With code from: Catrice English

"""
#Import Libraries

import re #The Regular Expressions Library

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

# Map Registers to addresses
register_addresses = {
    'eax': 'F01',
    'ebx': 'F02',
    'ecx': 'F03',
    'edx': 'F04'
}

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
        hex_value = format(int_value, 'X').zfill(bit_width // 4)  # Each hex digit represents 4 bits
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





#MAIN
if __name__ == "__main__":
   
    #Welcome Message and Instructions for Use
    print("\033[36m*"*25, "Welcome to the code translator!", "*"*25)
    print("This program will translate any simple arithmetic operation into the YMC language.")
    print("Acceptable arithmetic operations are: +, -, *, /. ")
    print("Parameters may include up to two operands per iteration.")
    print("Numbers allowable range from -128 to 127")
    print("This program will also allow you to see the resulting operation in MC (Hex) by selecting \"y\" when prompted")
    print()
    
    #Start an infinite loop for user operation input (breakable by blank input)
    while True:  
        try:
            
            #get expression from user
            python_op = input("Enter arithmetic operation (or press Enter to exit): ")
            
            #Break loop if empty (user pressed Enter)
            if not python_op:  
                break
            
            #Format input and convert numeric values to hex
            formatted_op = format_expression_with_hex(python_op)
            operand1, operator1, operand2, operator2, operand3 = parse_expression(formatted_op)
            
            #Generates YMC instructions string
            machine_code_y = translate_to_machine_code(
                operand1, operator1, operand2, operator2, operand3
            )  
            print("YMC instructions:")
            print(machine_code_y)
            print()
            
            HexYN = input("Would you like to see the instructions in hex? (y or n): ")
            HexYN = HexYN.upper()
            if HexYN == "Y":
                #Split the YMC into individual lines and strip it down
                ymc_instructions = machine_code_y.strip().split('\n')
            
                #Convert each YMC instruction MC in hex
                mc_instructions_hex = [ymc_to_mc(instruction) for instruction in ymc_instructions if instruction]
            
                print("\nMC (in hex):")
                for instruction in mc_instructions_hex:
                    print(instruction)
            else:
                continue
                
        except ValueError as e:
            print(f"An error occurred: {e}")
 
