# DO_NOT_EDIT_ANYTHING_ABOVE_THIS_LINE
num_of_inputs = int(input())
student_list = [[],[]]
beststudents =[]
for i in range(num_of_inputs):
    student , grade1 , grade2 ,grade3 = input().rstrip().split()
    student_list[0].append(student)
    student_list[1].append(int(grade1)+int(grade2)+int(grade3))
while True:
    maxgrade = max(student_list[1])
    index = student_list[1].index(maxgrade)
    beststudents.append(student_list[0][index])
    student_list[1][index] = 0
    if maxgrade not in student_list[1]:
        break
beststudents.sort()
print(beststudents[0])

# DO_NOT_EDIT_ANYTHING_BELOW_THIS_LINE