s1 = input()
s2 = input()
# DO_NOT_EDIT_ANYTHING_ABOVE_THIS_LINE
def is_reverse(s1 ,s2):
    s1,s2 = str(s1).lower(), str(s2).lower()
    if len(s1) == 0 and len(s2) == 0: return True
    elif s1[0] == s2[-1] and len(s1) != 0 and len(s2) != 0:return is_reverse(s1[1:],s2[:-1])
    else: return False
# DO_NOT_EDIT_ANYTHING_BELOW_THIS_LINE
print(is_reverse(s1, s2))