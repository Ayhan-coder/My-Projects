input_int= int(input())
output_list = []
# DO_NOT_EDIT_ANYTHING_ABOVE_THIS_LINE

for i in range(2, input_int):
    count = 0
    for j in range(2, i):
        if i % j == 0:
            count += 1

    if count == 0:
        output_list.append(i)




# DO_NOT_EDIT_ANYTHING_BELOW_THIS_LINE
for element in output_list:
    print(element)