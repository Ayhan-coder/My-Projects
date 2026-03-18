words = input().split()
# DO_NOT_EDIT_ANYTHING_ABOVE_THIS_LINE
def permutations(my_list):
    if len(my_list) == 0: return [""]
    else:
        output_list = []
        for i in range(len(my_list)):
            rest = my_list[:i] + my_list[i+1:]
            for p in permutations(rest):output_list.append(my_list[i] + p)
    return output_list
# DO_NOT_EDIT_ANYTHING_BELOW_THIS_LINE
perms = permutations(words)
perms.sort()
for perm in perms:
    print(perm)