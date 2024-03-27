# -*- coding: utf-8 -*-
"""
Created on Tue Mar 26 18:27:14 2024

@author: catri
"""

#set registers
registers = {
    'eax': 0,
    'ebx': 0,
    'ecx': 0,
    'edx': 0
}

#set opcodes
opcodes = {
    'mov': 509,
    'add': 400,
    'sub': 401,
    'mult': 402,
    'div': 403,
    'addsub': 404,
    'addmult': 405,
    'adddiv': 406,
    'subadd': 407,
    'submult': 408,
    'subdiv': 409,
    'multadd': '40A',
    'multsub': '40B',
    'multdiv': '40C',
    'divadd': '40D',
    'divsub': '40E',
    'divmult': '40F',
    'jmp': 500,
    'je': 501,
    'jne': 502,
    'jz': 503,
    'jg': 504,
    'jge': 505,
    'jl': 506,
    'jle': 507,
    'cmp': 508
}

def split_program_into_lines(program):
    # Split the program into lines
    lines = program.splitlines()
    
    #split each line into parts with delimiters being whitespace
    for line in lines:
        parts = line.split()
        
        #count the number of parts in each line to classify which type of
        #operation they belong to.
        
        #if number of parts is 3 then we know the operation is a mov operation
        if (len(parts) == 3):
            
            #moving a value from one register to another register
            if parts[2].strip() in registers:
                registers[parts[0].strip()] = registers[parts[2].strip()]
                
            #moving an immediate value into a register
            else:
                registers[parts[0].strip()] = int(parts[2].strip())
        
        #if number of parts is 5 then we know the operation is a two operand
        #arithmetic operation.
        elif (len(parts) == 5):
            
            operator = parts[3].strip()
            operand1 = parts[2].strip()
            operand2 = parts[4].strip()
            result = 0

            if (operator == '+'):
                if operand2 in registers:
                    result = registers[operand2] + \
                    (registers[operand1] if operand1 in registers \
                     else int(operand1))
                else:
                    result = int(operand2) + \
                        (registers[operand1] if operand1 in registers \
                         else int(operand1))
                            
            elif (operator == '-'):
                if operand2 in registers:
                    result = registers[operand2] - \
                        (registers[operand1] if operand1 in registers \
                         else int(operand1))
                else:
                    result = int(operand2) - \
                        (registers[operand1] if operand1 in registers \
                         else int(operand1))
                            
            elif (operator == '*'):
                if operand2 in registers:
                    result = registers[operand2] * \
                        (registers[operand1] if operand1 in registers \
                         else int(operand1))
                else:
                    result = int(operand2) * \
                        (registers[operand1] if operand1 in registers \
                         else int(operand1))
                            
            elif (operator == '/'):
                if operand2 in registers:
                    result = registers[operand2] \
                        / (registers[operand1] if operand1 in registers \
                           else int(operand1))
                else:
                    result = int(operand2) / \
                        (registers[operand1] if operand1 in registers \
                         else int(operand1))

    
            registers[parts[0].strip()] = result


program = """
eax = ebx
ebx = 10
ecx = ebx
edx = 300
ecx = edx
eax = 5 + 3
eax = eax + ebx
eax = 0
"""

split_program_into_lines(program)

for key, value in registers.items():
    print(f"{key}: {value}")
