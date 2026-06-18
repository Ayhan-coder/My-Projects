inp_str = input()
# DO_NOT_EDIT_ANYTHING_ABOVE_THIS_LINE
def calc_parser(calc_str):
    while "(" in calc_str:
        start = calc_str.rfind("(")
        end = calc_str.find(")", start)
        inner_result = calc_parser(calc_str[start + 1 : end])
        calc_str = calc_str[:start] + str(inner_result) + calc_str[end + 1 :]
    parts = calc_str.split()
    operator = parts[1]
    def removeparantesis(part):
        if part.startswith('('):part = part.lstrip('(')
        if part.endswith(')'):part = part.rstrip(')')
        return int(part)
    sayi1 = removeparantesis(parts[0])
    sayi2 = removeparantesis(parts[2])
    if operator == "+" : return sayi1 + sayi2
    elif operator == "-" : return sayi1 - sayi2
# DO_NOT_EDIT_ANYTHING_BELOW_THIS_LINE
print(calc_parser(inp_str))