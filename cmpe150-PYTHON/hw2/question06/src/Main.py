n = int(input())
scores = [int(x) for x in input().split()]
# DO_NOT_EDIT_ANYTHING_ABOVE_THIS_LINE
max = -1
secmax = -1
all_same = True

for i in scores:
    if i > max:
        secmax = max
        max = i
    elif i < max:
        if i > secmax:
            secmax = i
    if i != scores[0]:
        all_same = False

if all_same:
    print(-1)
else:
    print(secmax)
# DO_NOT_EDIT_ANYTHING_BELOW_THIS_LINE