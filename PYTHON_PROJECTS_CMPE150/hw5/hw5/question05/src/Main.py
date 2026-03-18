n = int(input())
# DO_NOT_EDIT_ANYTHING_ABOVE_THIS_LINE
def sum_of_integers(number, current_sum=[]):
    if sum(current_sum) == number:return [current_sum]
    elif sum(current_sum) > number:return []
    else:
        result = []
        for i in range(1, number+1):
            result += sum_of_integers(number, current_sum + [i])
        return result
# DO_NOT_EDIT_ANYTHING_BELOW_THIS_LINE
sums = sum_of_integers(n)
sums = [" + ".join(list(map(str, a_sum))) for a_sum in sums]
sums.sort()
for a_sum in sums:
    print(a_sum)