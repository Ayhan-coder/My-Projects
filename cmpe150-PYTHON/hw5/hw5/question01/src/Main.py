n1 = int(input())
n2 = int(input())
# DO_NOT_EDIT_ANYTHING_ABOVE_THIS_LINE
def digit_match(n1, n2):
    n1 = str(n1).rstrip(" ").lstrip(" ")
    n2 = str(n2).rstrip(" ").lstrip(" ")
    if len(n1) > len(n2):return digit_match(n1[1:], n2)
    elif len(n2) > len(n1):return digit_match(n1, n2[1:])
    else:
        if len(n1) == 0:return 0
        elif n1[0] == n2[0]:return 1 + digit_match(n1[1:], n2[1:])
        else:return 0 + digit_match(n1[1:], n2[1:])
# DO_NOT_EDIT_ANYTHING_BELOW_THIS_LINE
print(digit_match(n1, n2))