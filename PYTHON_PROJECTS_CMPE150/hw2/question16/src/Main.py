
# DO_NOT_EDIT_ANYTHING_ABOVE_THIS_LINE
text = input()
text = text.lstrip(' ')
text = text.rstrip('.')
textlist = text.split()
print(len(textlist))
numberofchar = 0
for word in textlist:
    for chr in word:
        numberofchar += 1

print(numberofchar)
# DO_NOT_EDIT_ANYTHING_BELOW_THIS_LINE
