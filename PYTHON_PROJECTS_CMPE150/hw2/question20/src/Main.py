n = int(input())
# DO_NOT_EDIT_ANYTHING_ABOVE_THIS_LINE
for i in range(0,n-1):
    print((n-1-i)*'#',end='')
    print(i * '+',end='')
    print('+',end='')
    print(i * '+', end='')
    print((n - 1 - i) * '#', end='')
    print()
print((2*n-1)*'+')

for i in range(0,n-1):
    print((i+1)*'#',end='')
    print((n-i-2)*'+',end='')
    print('+',end='')
    print((n-i-2)*'+',end='')
    print((i + 1) * '#', end='')
    print()


# DO_NOT_EDIT_ANYTHING_BELOW_THIS_LINE
