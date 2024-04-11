import re
import random

a = random.randint(0, 20)
b = random.randint(0, 20)
c = random.randint(0, 20)
x = random.randint(-20, 20)
y = random.randint(-20, 20)
z = random.randint(-20, 20)

variable_addresses = {
    'a': a,
    'b': b,
    'c': c,
    'x': x,
    'y': y,
    'z': z
    }

testfile = r"""if c <= 10
    x = y + 10
else
    x = y - 20

while y > 0
    print y
    print \n
    print x
    print \n
    y = y - 1"""

def if_else(list_ex, rel_op):                   #start of if-else function
    #print(list_ex, " : ", rel_op)
    words = list_ex[0].split()
    var = variable_addresses[words[1]]
    const = int(words[3])
    print(words[1], ' = ', var, ' : ', const)
    if rel_op == 0:
        if var == const:
            print("Equal True")                 #replace print statements with calling the operand function and reader for list_ex[1] if TRUE or list_ex[3] if FALSE
        else:
            print("Equal False")
    elif rel_op == 1:
        if var != const:
            print("Not Equal True")
        else:
            print("Not Equal False")
    elif rel_op == 2:
        if var > const:
            print("Greater Than True")
        else:
            print("Greater Than False")
    elif rel_op == 3:
        if var < const:
            print("Less Than True")
        else:
            print("Less Than False")
    elif rel_op == 4:
        if var >= const:
            print("Greater Equal True")
        else:
            print("Greater Equal False")
    elif rel_op == 5:
        if var <= const:
            print("Less Equal True")
        else:
            print("Less Equal False")

def while_loop(list_ex, rel_op):                #start of while function
    #print(list_ex, " : ", rel_op)
    words = list_ex[0].split()
    var = variable_addresses[words[1]]
    const = int(words[3])
    print(words[1], ' = ', var, ' : ', const)
    if rel_op == 0:
        if var == const:                        #simply replace the if-else with a while statement instead
            print("Equal True")                 #replace print statements with calling the operand function and reader for list_ex[1] if TRUE or list_ex[3] if FALSE
        else:
            print("Equal False")
    elif rel_op == 1:
        if var != const:
            print("Not Equal True")
        else:
            print("Not Equal False")
    elif rel_op == 2:
        if var > const:
            print("Greater Than True")
        else:
            print("Greater Than False")
    elif rel_op == 3:
        if var < const:
            print("Less Than True")
        else:
            print("Less Than False")
    elif rel_op == 4:
        if var >= const:
            print("Greater Equal True")
        else:
            print("Greater Equal False")
    elif rel_op == 5:
        if var <= const:
            print("Less Equal True")
        else:
            print("Less Equal False")

def line_splitter(read_file):
    list1 = []
    list2 = []
    paragraphs = read_file.split('\n\n')             #breaks up into 'paragraphs'
    ctr = 0
    for i in paragraphs:
        list1.append(i)
        ctr += 1
    ctr = 0
    for i in list1:                                 
        split_list = list1[ctr].split('\n')
        strip_split_list = [line.strip() for line in split_list]
        list2.append(strip_split_list)
        ctr +=1
    return list2
    
def classifier(list_ex):
    ctr = 0
    for i in list_ex:
        first_words = i[0].split()                  #pulls 1st string to determine section
        if first_words[0] == 'if':                  #if-else section
            if first_words[2] == '==':
                if_else(i, 0)
            elif first_words[2] == '!=':
                if_else(i, 1)
            elif first_words[2] == '>':
                if_else(i, 2)
            elif first_words[2] == '<':
                if_else(i, 3)
            elif first_words[2] == '>=':
                if_else(i, 4)
            elif first_words[2] == '<=':
                if_else(i, 5)
        elif first_words[0] == 'while':             #while section
            if first_words[2] == '==':
                while_loop(i, 0)
            elif first_words[2] == '!=':
                while_loop(i, 1)
            elif first_words[2] == '>':
                while_loop(i, 2)
            elif first_words[2] == '<':
                while_loop(i, 3)
            elif first_words[2] == '>=':
                while_loop(i, 4)
            elif first_words[2] == '<=':
                while_loop(i, 5)
        else:
            print('This is an operand statement')

temp_list = line_splitter(testfile)
classifier(temp_list)

#paragraphs = testfile.split('\n\n')             #breaks up into 'paragraphs'
#ctr = 0
#for i in paragraphs:
#    list1.append(i)
#    ctr += 1

#ctr = 0
#for i in list1:                                 
#    split_list = list1[ctr].split('\n')
#    strip_split_list = [line.strip() for line in split_list]
#    list3.append(strip_split_list)
#    ctr +=1

#ctr = 0
#for i in list3:
#    first_words = i[0].split()                  #pulls 1st string to determine section
#    if first_words[0] == 'if':                  #if-else section
#        if first_words[2] == '==':
#            if_else(i, 0)
#        elif first_words[2] == '!=':
#            if_else(i, 1)
#        elif first_words[2] == '>':
#            if_else(i, 2)
#        elif first_words[2] == '<':
#            if_else(i, 3)
#        elif first_words[2] == '>=':
#            if_else(i, 4)
#       elif first_words[2] == '<=':
#            if_else(i, 5)
#    elif first_words[0] == 'while':             #while section
#        if first_words[2] == '==':
#            while_loop(i, 0)
#        elif first_words[2] == '!=':
#            while_loop(i, 1)
#        elif first_words[2] == '>':
#            while_loop(i, 2)
#        elif first_words[2] == '<':
#            while_loop(i, 3)
#        elif first_words[2] == '>=':
#            while_loop(i, 4)
#        elif first_words[2] == '<=':
#            while_loop(i, 5)
#    else:
#        print('This is an operand statement')
        #call operand function - handled elsewhere

##ctr = 0
##for i in lines:
##    print(ctr, ": ", i)
##    ctr +=1

##ctr = 0
##paragraphs = list(filter(lambda x : x != '', testfile.split('\n\n')))
##for i in paragraphs:
##    print(ctr, ": ", i)
##    ctr +=1
