import re

variables = ['a', 'b', 'c', 'x', 'y','z']

variable_addresses = {
    'a': '[000]',
    'b': '[001]',
    'c': '[002]',
    'x': '[003]',
    'y': '[004]',
    'z': '[005]'
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
    print(list_ex, " : ", rel_op)

def while_loop(list_ex, rel_op):                #start of while function
    print(list_ex, " : ", rel_op)

lines = testfile.splitlines()
list1 = []                                      #need better names, temp for now
list2 = []
list3 = []

paragraphs = testfile.split('\n\n')
ctr = 0
for i in paragraphs:
    list1.append(i)
    ctr += 1

ctr = 0
for i in list1:
    split_list = list1[ctr].split('\n')
    strip_split_list = [line.strip() for line in split_list]
    list3.append(strip_split_list)
    ctr +=1

ctr = 0
for i in list3:
    first_words = i[0].split()                  #can add a case match/ or lowercase to make it easier
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
