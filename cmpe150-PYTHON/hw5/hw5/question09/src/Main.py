n = int(input())
k = int(input())
# DO_NOT_EDIT_ANYTHING_ABOVE_THIS_LINE
def fib_mod(n,k):
    if n == 0: return 0
    if n == 1: return 1
    else: return (fib_mod(n-1,k) + fib_mod(n-2,k)) % k
# DO_NOT_EDIT_ANYTHING_BELOW_THIS_LINE
print(fib_mod(n, k))