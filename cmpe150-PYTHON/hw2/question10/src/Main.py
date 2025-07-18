# DO_NOT_EDIT_ANYTHING_ABOVE_THIS_LINE

size = int(input())
halfsize: int = size//2
for i in range(0, size//2):
    print(i *'-',end='')
    print('+',end ='')
    print((size-2*i-2) * '-', end='')
    print('+', end='')
    print(i * '-', end='')
    print('')
print(size//2*'-',end='')
print('+',end ='')
print(size//2*'-',end='')
print('')
for j in range(0,size//2):
    print((halfsize - j - 1) * '-',end ='')
    print('+', end='')
    print(((2*j)+1) * '-', end ='')
    print('+', end='')
    print((halfsize - j - 1) * '-', end ='')
    print('')

# DO_NOT_EDIT_ANYTHING_BELOW_THIS_LINE
