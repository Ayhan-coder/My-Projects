input_int = int(input())
output_list = []
# DO_NOT_EDIT_ANYTHING_ABOVE_THIS_LINE

fact = 1
for i in range(1, input_int + 1):
    fact *= i
    output_list.append(fact)
# DO_NOT_EDIT_ANYTHING_BELOW_THIS_LINE
for output_element in output_list:
    print(output_element)