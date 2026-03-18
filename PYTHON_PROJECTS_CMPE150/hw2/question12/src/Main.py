numbers = list(map(int, input().split()))
target = int(input())
# DO_NOT_EDIT_ANYTHING_ABOVE_THIS_LINE
for x in numbers:
    for y in numbers:
        if x!=y and x + y == target:
            print(x,y)

# DO_NOT_EDIT_ANYTHING_BELOW_THIS_LINE
