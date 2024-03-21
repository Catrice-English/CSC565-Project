# -*- coding: utf-8 -*-
"""
draft 2 - N. Grencz

including step by step explanations
"""
#set registers
registers = {
    'eax': 0,
    'ebx': 0,
    'ecx': 0,
    'edx': 0
}

memory = [None] * 5  # Track 5 memory slots

# Function to display the state of the machine
def display_state(step):
    
    print(f"\nAfter step {step}:")
    print("Registers:")
    for reg, value in registers.items():
        print(f"  {reg}: {value}")
    print("Memory:")
    for i, value in enumerate(memory):
        print(f"  Memory[{i}]: {value}")
    print ()
    print("------------------------------------------")
    print()
    user_input = input("Press enter to continue")

# Function to simulate a mock operation
def simulate_operation(op1, op2, operator):
    step = 1
    print()
    print ("Step ", step, ": Load first value into register eax")
    # Load op1 into eax
    registers['eax'] = op1
    display_state(step)

    step += 1
    # Load op2 into ebx
    
    print()
    print ("Step ", step, ": Load second value into register ebx")
    registers['ebx'] = op2
    display_state(step)

    step += 1
    # Set answer variable
    global var1
    # Perform the operation in eax using ebx
    
    print()
    print ("Step ", step, ": Perform the operation, replacing the value in eax")
    if operator == '+':
        registers['eax'] += registers['ebx']
    elif operator == '-':
        registers['eax'] -= registers['ebx']
    elif operator == '*':
        registers['eax'] *= registers['ebx']
    elif operator == '/':
        registers['eax'] /= registers['ebx']
    var1 = registers['eax']
    display_state(step)

# Ask for input
expression = input("Enter a simple mathematical expression (e.g. '5 + 3'): ")
op1, operator, op2 = expression.split()

# Convert operands to integers
op1, op2 = int(op1), int(op2)

# Start simulation
simulate_operation(op1, op2, operator)

print()
print("Return the answer")
print()
print(op1, operator, op2, "=", var1 )