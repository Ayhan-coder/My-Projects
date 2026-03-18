import json
ls = json.loads(input())
# DO_NOT_EDIT_ANYTHING_ABOVE_THIS_LINE
def reverse_list(ls):
    if len(ls) < 1 : return ls
    else: return [ls[-1]] + reverse_list(ls[:-1])
# DO_NOT_EDIT_ANYTHING_BELOW_THIS_LINE
print(reverse_list(ls))