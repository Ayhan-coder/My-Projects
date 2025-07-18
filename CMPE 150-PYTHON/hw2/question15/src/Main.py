
# DO_NOT_EDIT_ANYTHING_ABOVE_THIS_LINE

size = int(input())
for row in range(size):
    if row == 0:
        print(size*'1')

    elif row == size-1:
        print(size*'1')
        break
    else:
        print('1',end='')
        print((size-2)*'0',end='')
        print('1')
# DO_NOT_EDIT_ANYTHING_BELOW_THIS_LINE
