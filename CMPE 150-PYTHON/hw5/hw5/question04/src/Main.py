words = input().split()
k = int(input())
# DO_NOT_EDIT_ANYTHING_ABOVE_THIS_LINE
def permutations_of_size(my_list, k):
    if k == 0:return ['']
    output_list = []
    for i in range(len(my_list)):
        rest = my_list[:i] + my_list[i + 1:]
        for p in permutations_of_size(rest, k - 1):output_list.append(my_list[i] + p)
    return output_list
# DO_NOT_EDIT_ANYTHING_BELOW_THIS_LINE
perms = permutations_of_size(words, k)
perms.sort()
for perm in perms:
    print(perm)