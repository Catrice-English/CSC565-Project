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

def split_program_into_lines(program):
    # Split the program into lines
    lines = program.splitlines()
    
    #split each line into parts with delimiters being whitespace
    for line in lines:
        parts = line.split()
        
        #count the number of parts in each line to classify which type of
        #operation they belong to.
        
        #if number of parts is 3 then we know the operation is a mov operation
        # or a compare operation
        if (len(parts) == 3):
            
            if (parts[1] == '='):
            
                #moving a value from one register to another register
                if parts[2].strip() in registers:
                    registers[parts[0].strip()] = registers[parts[2].strip()]
                    
                #moving an immediate value into a register
                else:
                    registers[parts[0].strip()] = int(parts[2].strip())
        
        
        #if number of parts is 5 then we know the operation is a two operand
        #arithmetic operation or a compare operation.
        elif (len(parts) == 5):
            
            operator = parts[3].strip()
            operand1 = parts[2].strip()
            operand2 = parts[4].strip()
            result = 0
            
            if (parts[1] == '='):

                if (operator == '+'):
                    result = two_operand_add(operand1, operand2)
                                
                elif (operator == '-'):
                    result = two_operand_sub(operand1, operand2)
                                
                elif (operator == '*'):
                    result = two_operand_mult(operand1, operand2)
                                
                elif (operator == '/'):
                    result = two_operand_div(operand1, operand2)

    
            registers[parts[0].strip()] = result
        
        elif (len(parts) == 7):
            
            operator1 = parts[3].strip()
            operator2 = parts[5].strip()
            operand1 = parts[2].strip()
            operand2 = parts[4].strip()
            operand3 = parts[6].strip()
            intermediateresult = 0
            finalresult = 0
            
            if (parts[1] == '='):
                
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
            
            registers[parts[0].strip()] = finalresult
            
            

def two_operand_add(op1, op2):
    if op2 in registers:
        addresult = registers[op1] + (registers[op2] \
        if op1 in registers else int(op1))
    else:
        addresult = (registers[op1] if op1 in registers else int(op1)) \
        + int(op2)
    
    return addresult

def two_operand_sub(op1, op2):
    if op2 in registers:
        subresult = registers[op1] - (registers[op2] \
        if op1 in registers else int(op1))
    else:
        subresult = (registers[op1] if op1 in registers else int(op1)) \
        - int(op2)
    
    return subresult

def two_operand_mult(op1, op2):
    if op2 in registers:
        multresult = registers[op1] * (registers[op2] \
        if op1 in registers else int(op1))
    else:
        multresult = (registers[op1] if op1 in registers else int(op1)) \
        * int(op2)
    
    return multresult

def two_operand_div(op1, op2):
    if op2 in registers:
        divresult = registers[op1] / (registers[op2] \
        if op1 in registers else int(op1))
    else:
        divresult = (registers[op1] if op1 in registers else int(op1)) \
        / int(op2)
    
    return divresult


program = """
eax = ebx
ebx = 10
ecx = ebx
edx = 300
ecx = edx
eax = 10
eax = eax / 2 * 2
"""

split_program_into_lines(program)

for key, value in registers.items():
    print(f"{key}: {value}")
