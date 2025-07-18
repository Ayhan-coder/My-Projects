n = int(input())
word = input()
# DO_NOT_EDIT_ANYTHING_ABOVE_THIS_LINE
count = 0
for j in range(0,n//2):
    if word[j] != word[n-j-1]:
        count += 1

if count == 0:
    print('YES')
else:
    print('NO')


# DO_NOT_EDIT_ANYTHING_BELOW_THIS_LINE