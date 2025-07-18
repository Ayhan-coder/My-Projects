input_int = int(input())
# DO_NOT_EDIT_ANYTHING_ABOVE_THIS_LINE

if input_int == 1:
    print('x')

elif input_int != 1 and input_int % 2 != 0 :
    for i in range(input_int//2):
        print((input_int//2)*'x_'+'x')
        print((input_int//2)*'_x'+'_')
    print((input_int // 2) * 'x_' + 'x')

elif input_int != 1 and input_int % 2 == 0 :
    for i in range(input_int//2):
        print((input_int//2)*'x_')
        print((input_int//2)*'_x')


else:
    exit()

# DO_NOT_EDIT_ANYTHING_BELOW_THIS_LINE
