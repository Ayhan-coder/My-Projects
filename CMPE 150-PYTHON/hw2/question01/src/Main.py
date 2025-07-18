input_int = int(input())
output = 0
# DO_NOT_EDIT_ANYTHING_ABOVE_THIS_LINE

fib_2 = 0
fib_1 = 1
fib = 0
for i in range(2, input_int+1):
    fib = fib_1 + fib_2
    fib_2 = fib_1
    fib_1 = fib
if input_int == 0:
    output = fib_2
elif input_int >= 1:
    output = fib_1


# DO_NOT_EDIT_ANYTHING_BELOW_THIS_LINE
print(output)

