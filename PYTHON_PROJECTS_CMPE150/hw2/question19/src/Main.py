n = int(input())
# DO_NOT_EDIT_ANYTHING_ABOVE_THIS_LINE
primelist = []

for i in range(2,n):
    dividecount = False
    for j in range(2,n):
        if i != j and i % j == 0:
            dividecount = True
    if dividecount == False:
        primelist.append(i)
    else:
        continue

for i in primelist:
    for j in primelist:
        if i + j == n:
            print(i,j)
# DO_NOT_EDIT_ANYTHING_BELOW_THIS_LINE
