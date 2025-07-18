n = int(input())
num = int(input())
# DO_NOT_EDIT_ANYTHING_ABOVE_THIS_LINE
numofdigits = n
binarynum = num
sum = 0
for i in range(0,numofdigits):
    remainder = 0
    remainder = binarynum % 10
    binarynum = binarynum // 10
    sum += remainder * (2**i)

print(sum)




# DO_NOT_EDIT_ANYTHING_BELOW_THIS_LINE
