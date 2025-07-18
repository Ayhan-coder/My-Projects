n1 = int(input())
n2 = int(input())
# DO_NOT_EDIT_ANYTHING_ABOVE_THIS_LINE
def gcd(n1,n2):
    if n2 == 0: return n1
    else:
        mod = n1 % n2
        return gcd(n2, mod)
# DO_NOT_EDIT_ANYTHING_BELOW_THIS_LINE
print(gcd(n1, n2))