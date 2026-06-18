length = int(input())
num = int(input())
# DO_NOT_EDIT_ANYTHING_ABOVE_THIS_LINE
remeinder = 0
numlist =[]
for i in range(length):
    remeinder = num % 10
    numlist.append(remeinder)
    num = num // 10

result = 0
for i in range(length):
    result += numlist[i] * (10**(length-i-1))
print(result)


# DO_NOT_EDIT_ANYTHING_BELOW_THIS_LINE