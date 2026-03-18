import json
ls = json.loads(input())
# DO_NOT_EDIT_ANYTHING_ABOVE_THIS_LINE
def any_empty(ls):
    if not ls:return True
    for el in ls:
        if type(el) is list:
            if any_empty(el):
                return True
        else:continue
    return False
# DO_NOT_EDIT_ANYTHING_BELOW_THIS_LINE
print(any_empty(ls))