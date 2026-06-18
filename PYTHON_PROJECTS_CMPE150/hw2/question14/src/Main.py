# DO_NOT_EDIT_ANYTHING_ABOVE_THIS_LINE
number = int(input())
dividers = []
for i in range(2, number):
    if number % i == 0:
        dividers.append(i)
for num in range(1, number):
    divisible = False
    for div in dividers:
        if num % div == 0:
            divisible = True
            break
    if divisible == False:
        print(num)



# DO_NOT_EDIT_ANYTHING_BELOW_THIS_LINE
