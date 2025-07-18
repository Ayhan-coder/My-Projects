numbers_list = []
while (True):
    x = int(input())
    if (x == 0):
        break
    numbers_list.append(x)
# DO_NOT_EDIT_ANYTHING_ABOVE_THIS_LINE
length = len(numbers_list)
sum = 0
for numbers in numbers_list :
    sum += numbers
average = sum // length
standartdev = 0
sum = 0
for numbers in numbers_list:
    sum += (numbers -average)**2
standartdev = (sum/length)**(1/2)
std_dev = standartdev
# DO_NOT_EDIT_ANYTHING_BELOW_THIS_LINE
result = round(std_dev, 4)
print(result)