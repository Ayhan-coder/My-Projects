car_height = int(input())
car_length = int(input())
man_height = int(input())
# DO_NOT_EDIT_ANYTHING_ABOVE_THIS_LINE
carup = ((8 + man_height) - (car_height + 3))
colnumber = (2 * car_length )+15
if car_length > 4:
    for col in range(1, colnumber + 1):

        if col <= 11:

            for row in range(1, 8+man_height+2):
                if row == 1:
                    if row == carup + 1: print(5*'X',(11-col)*' ',car_length*'X',sep='')
                    else: print(5*'X',(11-col)*' ',sep='')
                elif row == 2:
                    if row == carup +1: print("X   X",(11-col)*' ',car_length*'X',sep='')
                    elif row == carup +2: print("X   X",(11-col)*' ','X',(car_length-2)*' ','X',sep='')
                    else: print('X   X')
                elif row == 3:
                    if row == carup + 1: print("X   X", (11 - col) * ' ', car_length * 'X',sep='')
                    elif carup + 1 < row < carup + car_height: print("X   X", (11 - col) * ' ','X',(car_length-2)*' ','X',sep='' )
                    elif row == carup+ car_height: print("X   X", (11 - col) * ' ',car_length*'X',sep='')
                    else: print('X   X')
                elif row == 4:
                    if row == carup + 1: print(5*"X", (11 - col) * ' ', car_length * 'X',sep='')
                    elif carup + 1 < row < carup + car_height: print(5*"X", (11 - col) * ' ', 'X', (car_length - 2) * ' ', 'X',sep='')
                    elif row == carup+ car_height:print(5*"X", (11 - col) * ' ', car_length * 'X',sep='')
                    else: print(5*'X')
                elif row == 5:
                    if row == carup + 1: print('  X  ', (11 - col) * ' ', car_length * 'X',sep='')
                    elif carup + 1 < row < carup + car_height: print('  X  ', (11 - col) * ' ', 'X', (car_length - 2) * ' ', 'X',sep='')
                    elif row == carup+ car_height:print('  X  ', (11 - col) * ' ', car_length * 'X',sep='')
                    else: print('  X')
                elif row == 6:
                    if row == carup + 1: print('XXXXX', (11 - col) * ' ', car_length * 'X',sep='')
                    elif carup + 1 < row < carup + car_height: print('XXXXX', (11 - col) * ' ', 'X', (car_length - 2) * ' ','X', sep='')
                    elif row == carup + car_height: print('XXXXX', (11 - col) * ' ', car_length * 'X',sep='')
                    else: print('XXXXX')
                elif 7 <= row <= 6 + man_height:
                    if row == carup + 1: print('  X  ', (11 - col) * ' ', car_length * 'X', sep='')
                    elif carup + 1 < row < carup + car_height: print('  X  ', (11 - col) * ' ', 'X', (car_length - 2) * ' ', 'X', sep='')
                    elif row == carup + car_height: print('  X  ', (11 - col) * ' ', car_length * 'X',sep='')
                    else: print('  X')
                elif row == man_height +7:print(' X X')
                elif row == man_height +8:print("X   X")
                elif row == man_height +9:print(" ")
        if colnumber +1> col >11:
            for row in range(1, 8 + man_height + 2):
                if col == 12:
                    if carup +1> row and row == 1: print("XXXXX")
                    if carup +1 == row and row == 1: print((16-col)*"X",car_length*"X",sep='')
                    if row == 2 and carup + 1 == row : print("X", (15 - col) * ' ', car_length*"X", sep='')
                    if row == 2 and carup + 1 < row < carup + car_height:print("X",(15-col)*' ',"X",(car_length-2)*" ","X",sep='')
                    if row == 2 and carup + 1 > row: print("X   X")
                    if row == 2 and car_height + carup == row: print("X", (15 - col) * ' ', car_length * "X", sep='')
                    if row == 3 and carup + 1 == row : print("X", (15 - col) * ' ', car_length*"X", sep='')
                    if row == 3 and carup + 1 < row < carup + car_height:print("X",(15-col)*' ',"X",(car_length-2)*" ","X",sep='')
                    if row == 3 and carup + 1 > row: print("X   X")
                    if row == 3 and car_height + carup == row: print("X", (15 - col) * ' ', car_length*"X", sep='')
                    if row == 4 and carup + 1 == row : print((16-col)*"X", car_length*"X", sep='')
                    if row == 4 and carup + 1 < row < carup + car_height:print((16-col)*"X","X",(car_length-2)*" ","X",sep='')
                    if row == 4 and car_height+ carup ==row: print((16-col)*"X",car_length*'X',sep='')
                    if row == 4 and carup + 1 > row: print("XXXXX")
                    if row == 5 and carup + 1 == row : print("  X ", car_length*"X", sep='')
                    if row == 5 and carup + 1 < row < carup + car_height:print("  X ","X",(car_length-2)*" ","X",sep='')
                    if row == 5 and car_height+ carup ==row: print("  X ",car_length*'X',sep='')
                    if row == 5 and carup + 1 > row: print("  X  ")
                    if row == 6 and carup + 1 == row : print((16-col)*"X", car_length*"X", sep='')
                    if row == 6 and carup + 1 < row < carup + car_height:print((16-col)*"X","X",(car_length-2)*" ","X",sep='')
                    if row == 6 and car_height+ carup ==row: print((16-col)*"X",car_length*'X',sep='')
                    if row == 6 and carup + 1 > row: print("XXXXX")
                    if 7 <= row <= 6 + man_height and carup + 1 == row : print("  X ", car_length*"X", sep='')
                    if 7 <= row <= 6 + man_height and car_height+ carup ==row: print("  X ", car_length * "X", sep='')
                    if 7 <= row <= 6 + man_height and car_height + carup < row: print("  X")
                    if 7 <= row <= 6 + man_height and carup + 1 < row < carup + car_height: print("  X ", "X",(car_length-2)*" ","X", sep='')
                    if 7 <= row <= 6 + man_height and carup + 1 > row: print("  X")
                    elif row == man_height + 7:print(' X X')
                    elif row == man_height + 8:print("X   X")
                    elif row == man_height + 9:
                        print(" ")
                if col == 13:
                    if carup +1> row and row == 1: print("XXXXX")
                    if carup +1 == row and row == 1: print((16-col)*"X",car_length*"X",sep='')
                    if row == 2 and carup + 1 == row : print("X", (15 - col) * ' ', car_length*"X", sep='')
                    if row == 2 and carup + 1 < row < carup + car_height:print("X",(15-col)*' ',"X",(car_length-2)*" ","X",sep='')
                    if row == 2 and carup + 1 > row: print("X   X")
                    if row == 2 and car_height + carup == row: print("X", (15 - col) * ' ', car_length * "X", sep='')
                    if row == 3 and carup + 1 == row : print("X", (15 - col) * ' ', car_length*"X", sep='')
                    if row == 3 and carup + 1 < row < carup + car_height:print("X",(15-col)*' ',"X",(car_length-2)*" ","X",sep='')
                    if row == 3 and carup + 1 > row: print("X   X")
                    if row == 3 and car_height + carup == row: print("X", (15 - col) * ' ', car_length*"X", sep='')
                    if row == 4 and carup + 1 == row : print((16-col)*"X", car_length*"X", sep='')
                    if row == 4 and carup + 1 < row < carup + car_height:print((16-col)*"X","X",(car_length-2)*" ","X",sep='')
                    if row == 4 and car_height+ carup ==row: print((16-col)*"X",car_length*'X',sep='')
                    if row == 4 and carup + 1 > row: print("XXXXX")
                    if row == 5 and carup + 1 == row : print("  X", car_length*"X", sep='')
                    if row == 5 and carup + 1 < row < carup + car_height:print("  X","X",(car_length-2)*" ","X",sep='')
                    if row == 5 and car_height+ carup ==row: print("  X",car_length*'X',sep='')
                    if row == 5 and carup + 1 > row: print("  X  ")
                    if row == 6 and carup + 1 == row : print((16-col)*"X", car_length*"X", sep='')
                    if row == 6 and carup + 1 < row < carup + car_height:print((16-col)*"X","X",(car_length-2)*" ","X",sep='')
                    if row == 6 and car_height+ carup ==row: print((16-col)*"X",car_length*'X',sep='')
                    if row == 6 and carup + 1 > row: print("XXXXX")
                    if 7 <= row <= 6 + man_height and carup + 1 == row : print("  X", car_length*"X", sep='')
                    if 7 <= row <= 6 + man_height and car_height+ carup ==row: print("  X", car_length * "X", sep='')
                    if 7 <= row <= 6 + man_height and car_height + carup < row: print("  X  ")
                    if 7 <= row <= 6 + man_height and carup + 1 < row < carup + car_height: print("  X", "X",(car_length-2)*" ","X", sep='')
                    if 7 <= row <= 6 + man_height and carup + 1 > row: print("  X  ")
                    elif row == man_height + 7:print(' X X')
                    elif row == man_height + 8:print("X   X")
                    elif row == man_height + 9:
                        print(" ")

                if col == 14:
                    if carup +1> row and row ==1: print("XXXXX")
                    if carup +1 == row and row == 1: print((16-col)*"X",car_length*"X",sep='')
                    if row == 2 and carup + 1 == row :print("X", (15 - col) * ' ', car_length*"X", sep='')
                    if row == 2 and carup + 1 < row < carup + car_height:print("X",(15-col)*' ',"X",(car_length-2)*" ","X",sep='')
                    if row == 2 and carup + 1 > row: print("X   X")
                    if row == 2 and car_height + carup == row: print("X", (15 - col) * ' ', car_length * "X", sep='')
                    if row == 3 and carup + 1 == row : print("X", (15 - col) * ' ', car_length*"X", sep='')
                    if row == 3 and carup + 1 < row < carup + car_height:print("X",(15-col)*' ',"X",(car_length-2)*" ","X",sep='')
                    if row == 3 and carup + 1 > row: print("X   X")
                    if row == 3 and car_height + carup == row: print("X", (15 - col) * ' ', car_length*"X", sep='')
                    if row == 4 and carup + 1 == row : print((16-col)*"X", car_length*"X", sep='')
                    if row == 4 and carup + 1 < row < carup + car_height:print((16-col)*"X","X",(car_length-2)*" ","X",sep='')
                    if row == 4 and car_height+ carup ==row: print((16-col)*"X",car_length*'X',sep='')
                    if row == 4 and carup + 1 > row: print("XXXXX")
                    if row == 5 and carup + 1 == row : print("  ", car_length*"X", sep='')
                    if row == 5 and carup + 1 < row < carup + car_height:print("  ","X",(car_length-2)*" ","X",sep='')
                    if row == 5 and car_height+ carup ==row: print("  ",car_length*'X',sep='')
                    if row == 5 and carup + 1 > row: print("  X")
                    if row == 6 and carup + 1 == row : print((16-col)*"X", car_length*"X", sep='')
                    if row == 6 and carup + 1 < row < carup + car_height:print((16-col)*"X","X",(car_length-2)*" ","X",sep='')
                    if row == 6 and car_height+ carup ==row: print((16-col)*"X",car_length*'X',sep='')
                    if row == 6 and carup + 1 > row: print("XXXXX")
                    if 7 <= row <= 6 + man_height and carup + 1 == row : print("  ", car_length*"X", sep='')
                    if 7 <= row <= 6 + man_height and car_height+ carup ==row: print("  ", car_length * "X", sep='')
                    if 7 <= row <= 6 + man_height and car_height + carup < row: print("  X")
                    if 7 <= row <= 6 + man_height and carup + 1 < row < carup + car_height: print("  ", "X",(car_length-2)*" ","X", sep='')
                    if 7 <= row <= 6 + man_height and carup + 1 > row: print("  X")
                    elif row == man_height + 7:print(' X X')
                    elif row == man_height + 8:print("X   X")
                    elif row == man_height + 9:
                        print(" ")
                if col == 15:
                    if carup +1> row and row ==1: print("XXXXX")
                    if carup +1 == row and row == 1: print((16-col)*"X",car_length*"X",sep='')
                    if row == 2 and carup + 1 == row : print("X", (15 - col) * ' ', car_length*"X", sep='')
                    if row == 2 and carup + 1 < row < carup + car_height:print("X",(15-col)*' ',"X",(car_length-2)*" ","X",sep='')
                    if row == 2 and carup + 1 > row: print("X   X")
                    if row == 2 and car_height + carup == row: print("X", (15 - col) * ' ', car_length * "X", sep='')
                    if row == 3 and carup + 1 == row : print("X", (15 - col) * ' ', car_length*"X", sep='')
                    if row == 3 and carup + 1 < row < carup + car_height:print("X",(15-col)*' ',"X",(car_length-2)*" ","X",sep='')
                    if row == 3 and carup + 1 > row: print("X   X")
                    if row == 3 and car_height + carup == row: print("X", (15 - col) * ' ', car_length*"X", sep='')
                    if row == 4 and carup + 1 == row : print((16-col)*"X", car_length*"X", sep='')
                    if row == 4 and carup + 1 < row < carup + car_height:print((16-col)*"X","X",(car_length-2)*" ","X",sep='')
                    if row == 4 and car_height+ carup ==row: print((16-col)*"X",car_length*'X',sep='')
                    if row == 4 and carup + 1 > row: print("XXXXX")
                    if row == 5 and carup + 1 == row : print(" ", car_length*"X", sep='')
                    if row == 5 and carup + 1 < row < carup + car_height:print(" ","X",(car_length-2)*" ","X",sep='')
                    if row == 5 and car_height+ carup ==row: print(" ",car_length*'X',sep='')
                    if row == 5 and carup + 1 > row: print("  X")
                    if row == 6 and carup + 1 == row : print((16-col)*"X", car_length*"X", sep='')
                    if row == 6 and carup + 1 < row < carup + car_height:print((16-col)*"X","X",(car_length-2)*" ","X",sep='')
                    if row == 6 and car_height+ carup ==row: print((16-col)*"X",car_length*'X',sep='')
                    if row == 6 and carup + 1 > row: print("XXXXX")
                    if 7 <= row <= 6 + man_height and carup + 1 == row : print(" ", car_length*"X", sep='')
                    if 7 <= row <= 6 + man_height and car_height+ carup ==row: print(" ", car_length * "X", sep='')
                    if 7 <= row <= 6 + man_height and car_height + carup < row: print("  X")
                    if 7 <= row <= 6 + man_height and carup + 1 < row < carup + car_height: print(" ", "X",(car_length-2)*" ","X", sep='')
                    if 7 <= row <= 6 + man_height and carup + 1 > row: print("  X")
                    elif row == man_height + 7:print(' X X')
                    elif row == man_height + 8:print("X   X")
                    elif row == man_height + 9:
                        print(" ")
                if col == 16:

                        if carup +1> row and row ==1: print("XXXXX")
                        if carup +1 == row and row == 1: print(car_length*"X",sep='')
                        if row == 2 and carup + 1 == row : print( car_length*"X", sep='')
                        if row == 2 and carup + 1 < row < carup + car_height:print("X",(car_length-2)*" ","X",sep='')
                        if row == 2 and carup + 1 > row: print("X   X")
                        if row == 2 and car_height + carup == row: print( car_length * "X", sep='')
                        if row == 3 and carup + 1 == row : print( car_length*"X", sep='')
                        if row == 3 and carup + 1 < row < carup + car_height:print("X",(car_length-2)*" ","X",sep='')
                        if row == 3 and carup + 1 > row: print("X   X")
                        if row == 3 and car_height + carup == row: print(car_length*"X", sep='')
                        if row == 4 and carup + 1 == row : print( car_length*"X", sep='')
                        if row == 4 and carup + 1 < row < carup + car_height:print("X",(car_length-2)*" ","X",sep='')
                        if row == 4 and car_height+ carup ==row: print(car_length*'X',sep='')
                        if row == 4 and carup + 1 > row: print("XXXXX")
                        if row == 5 and carup + 1 == row : print( car_length*"X", sep='')
                        if row == 5 and carup + 1 < row < carup + car_height:print("X",(car_length-2)*" ","X",sep='')
                        if row == 5 and car_height+ carup ==row: print(car_length*'X',sep='')
                        if row == 5 and carup + 1 > row: print("  X")
                        if row == 6 and carup + 1 == row : print( car_length*"X", sep='')
                        if row == 6 and carup + 1 < row < carup + car_height:print("X",(car_length-2)*" ","X",sep='')
                        if row == 6 and car_height+ carup ==row: print(car_length*'X',sep='')
                        if row == 6 and carup + 1 > row: print("XXXXX")
                        if 7 <= row <= 6 + man_height and carup + 1 == row : print( car_length*"X", sep='')
                        if 7 <= row <= 6 + man_height and car_height+ carup ==row: print( car_length * "X", sep='')
                        if 7 <= row <= 6 + man_height and car_height + carup < row: print("  X")
                        if 7 <= row <= 6 + man_height and carup + 1 < row < carup + car_height: print("X",(car_length-2)*" ","X", sep='')
                        if 7 <= row <= 6 + man_height and carup + 1 > row: print("  X")
                        elif row == man_height + 7:print(' X X')
                        elif row == man_height + 8:print("X   X")
                        elif row == man_height + 9:print(" ")

        if  colnumber -1 >= col > 16 and car_length - (col -16) >0:
            fcol = col - 16
            for row in range(1, 8 + man_height + 2):

                if row == 1 and carup +1> row: print("XXXXX")
                if carup + 1 == row and row == 1 and car_length - fcol >= 5: print((car_length - fcol) * "X", sep='')
                if carup + 1 == row and row == 1 and car_length - fcol < 5: print((car_length - fcol) * "X", (5 - (car_length - fcol)) *"X", sep='')
                if row == 2 and carup + 1 > row: print("X   X")
                if carup + 1 == row and row == 2 and car_length - fcol >= 5: print((car_length - fcol) * "X", sep='')
                if carup + 1 == row and row == 2 and car_length - fcol < 5: print((car_length - fcol) * "X",(4 - (car_length - fcol)) * " ","X", sep='')
                if carup + 1 < row < carup + car_height and row == 2 and car_length - fcol >= 5: print((car_length - fcol-1) * " ","X", sep='')
                if carup + 1 < row < carup + car_height and row == 2 and car_length - fcol < 5: print((car_length - fcol-1) * " ","X",(4 - (car_length - fcol)) * " ","X", sep='')
                if car_height+ carup ==row and row == 2 and car_length - fcol >= 5: print((car_length - fcol) * "X", sep='')
                if car_height+ carup ==row and row == 2 and car_length - fcol < 5: print((car_length - fcol) * "X",(4 - (car_length - fcol)) * " ","X", sep='')
                if row == 3 and carup + 1 > row: print("X   X")
                if carup + 1 == row and row == 3 and car_length - fcol >= 5: print((car_length - fcol) * "X", sep='')
                if carup + 1 == row and row == 3 and car_length - fcol < 5: print((car_length - fcol) * "X",(4 - (car_length - fcol)) * " ","X", sep='')
                if carup + 1 < row < carup + car_height and row == 3 and car_length - fcol >= 5: print((car_length - fcol-1) * " ","X", sep='')
                if carup + 1 < row < carup + car_height and row == 3 and car_length - fcol < 5: print((car_length - fcol-1) * " ","X",(4 - (car_length - fcol)) * " ","X", sep='')
                if car_height+ carup ==row and row == 3 and car_length - fcol >= 5: print((car_length - fcol) * "X", sep='')
                if car_height+ carup ==row and row == 3 and car_length - fcol < 5: print((car_length - fcol) * "X",(4 - (car_length - fcol)) * " ","X", sep='')
                if row == 4 and carup + 1 > row: print("XXXXX")
                if carup + 1 == row and row == 4 and car_length - fcol >= 5: print((car_length - fcol) * "X", sep='')
                if carup + 1 == row and row == 4 and car_length - fcol < 5: print((car_length - fcol) * "X",(5 - (car_length - fcol)) * "X", sep='')
                if carup + 1 < row < carup + car_height and row == 4 and car_length - fcol >= 5: print((car_length - fcol-1) * " ","X", sep='')
                if carup + 1 < row < carup + car_height and row == 4 and car_length - fcol < 5: print((car_length - fcol-1) * " ","X",(5 - (car_length - fcol)) * "X", sep='')
                if car_height+ carup ==row and row == 4 and car_length - fcol >= 5: print((car_length - fcol) * "X", sep='')
                if car_height+ carup ==row and row == 4 and car_length - fcol < 5: print((car_length - fcol) * "X",(5 - (car_length - fcol)) * "X", sep='')
                if row == 5 and car_length -fcol >= 3:
                    if carup + 1 > row :print("  X")
                    if carup + 1 == row :print((car_length - fcol) * "X", sep='')
                    if carup + 1 < row < carup + car_height: print((car_length - fcol-1) * " ","X",sep='')
                    if car_height+ carup ==row : print((car_length - fcol) * "X", sep='')
                elif row == 5 and car_length -fcol < 3:
                    if carup + 1 > row: print("  X")
                    if carup + 1 == row: print((car_length - fcol) * "X", (2 - (car_length - fcol)) * " ","X",sep='')
                    if carup + 1 < row < carup + car_height: print((car_length - fcol - 1) * " ", "X",(2 - (car_length - fcol)) * " ","X", sep='')
                    if car_height + carup == row: print((car_length - fcol) * "X", (2 - (car_length - fcol)) * " ","X",sep='')
                if row == 6 and carup + 1 > row: print("XXXXX")
                if carup + 1 == row and row == 6 and car_length - fcol >= 5: print((car_length - fcol) * "X", sep='')
                if carup + 1 == row and row == 6 and car_length - fcol < 5: print((car_length - fcol) * "X",(5 - (car_length - fcol)) * "X", sep='')
                if carup + 1 < row < carup + car_height and row == 6 and car_length - fcol >= 5: print((car_length - fcol - 1) * " ", "X", sep='')
                if carup + 1 < row < carup + car_height and row == 6 and car_length - fcol < 5: print((car_length - fcol - 1) * " ", "X", (5 - (car_length - fcol)) * "X", sep='')
                if car_height + carup == row and row == 6 and car_length - fcol >= 5: print((car_length - fcol) * "X",sep='')
                if car_height + carup == row and row == 6 and car_length - fcol < 5: print((car_length - fcol) * "X",(5 - (car_length - fcol)) * "X",sep='')
                if 7 <= row <= 6 + man_height and car_length -fcol >= 3:
                    if carup + 1 > row :print("  X")
                    if carup + 1 == row :print((car_length - fcol) * "X", sep='')
                    if carup + 1 < row < carup + car_height: print((car_length - fcol-1) * " ","X",sep='')
                    if car_height+ carup ==row : print((car_length - fcol) * "X", sep='')
                    if car_height + carup < row: print("  X")
                if 7 <= row <= 6 + man_height and car_length -fcol < 3:
                    if carup + 1 > row: print("  X")
                    if carup + 1 == row: print((car_length - fcol) * "X", (2 - (car_length - fcol)) * " ","X",sep='')
                    if carup + 1 < row < carup + car_height: print((car_length - fcol - 1) * " ", "X",(2 - (car_length - fcol)) * " ","X", sep='')
                    if car_height + carup == row: print((car_length - fcol) * "X", (2 - (car_length - fcol)) * " ","X",sep='')
                    if car_height + carup < row: print("  X")
                if row == man_height + 7:print(' X X')
                if row == man_height + 8: print('X   X')
                elif row == man_height + 9: print(" ")

        if car_length - (col - 16) == 0:
            for row in range(1, 8+man_height+1):
                if row == 1:print(5*"X")
                elif row == 2:print("X   X")
                elif row == 3:print("X   X")
                elif row == 4:print(5*"X")
                elif row == 5:print("  X")
                elif row == 6:print(5*"X")
                elif 7 <= row <= 6 + man_height:print("  X")
                elif row == man_height +7:print(' X X')
                elif row == man_height +8:print("X   X")

            exit()
elif car_length == 4:
    for col in range(1, colnumber + 1):

        if col <= 11:

            for row in range(1, 8+man_height+2):
                if row == 1:
                    if row == carup + 1: print(5*'X',(11-col)*' ',car_length*'X',sep='')
                    else: print(5*'X',(11-col)*' ',sep='')
                elif row == 2:
                    if row == carup +1: print("X   X",(11-col)*' ',car_length*'X',sep='')
                    elif row == carup +2: print("X   X",(11-col)*' ','X',(car_length-2)*' ','X',sep='')
                    else: print('X   X')
                elif row == 3:
                    if row == carup + 1: print("X   X", (11 - col) * ' ', car_length * 'X',sep='')
                    elif carup + 1 < row < carup + car_height: print("X   X", (11 - col) * ' ','X',(car_length-2)*' ','X',sep='' )
                    elif row == carup+ car_height: print("X   X", (11 - col) * ' ',car_length*'X',sep='')
                    else: print('X   X')
                elif row == 4:
                    if row == carup + 1: print(5*"X", (11 - col) * ' ', car_length * 'X',sep='')
                    elif carup + 1 < row < carup + car_height: print(5*"X", (11 - col) * ' ', 'X', (car_length - 2) * ' ', 'X',sep='')
                    elif row == carup+ car_height:print(5*"X", (11 - col) * ' ', car_length * 'X',sep='')
                    else: print(5*'X')
                elif row == 5:
                    if row == carup + 1: print('  X  ', (11 - col) * ' ', car_length * 'X',sep='')
                    elif carup + 1 < row < carup + car_height: print('  X  ', (11 - col) * ' ', 'X', (car_length - 2) * ' ', 'X',sep='')
                    elif row == carup+ car_height:print('  X  ', (11 - col) * ' ', car_length * 'X',sep='')
                    else: print('  X')
                elif row == 6:
                    if row == carup + 1: print('XXXXX', (11 - col) * ' ', car_length * 'X',sep='')
                    elif carup + 1 < row < carup + car_height: print('XXXXX', (11 - col) * ' ', 'X', (car_length - 2) * ' ','X', sep='')
                    elif row == carup + car_height: print('XXXXX', (11 - col) * ' ', car_length * 'X',sep='')
                    else: print('XXXXX')
                elif 7 <= row <= 6 + man_height:
                    if row == carup + 1: print('  X  ', (11 - col) * ' ', car_length * 'X', sep='')
                    elif carup + 1 < row < carup + car_height: print('  X  ', (11 - col) * ' ', 'X', (car_length - 2) * ' ', 'X', sep='')
                    elif row == carup + car_height: print('  X  ', (11 - col) * ' ', car_length * 'X',sep='')
                    else: print('  X')
                elif row == man_height +7:print(' X X')
                elif row == man_height +8:print("X   X")
                elif row == man_height +9:print(" ")
        if colnumber +2> col >11:
            for row in range(1, 8 + man_height + 2):
                if col == 12:
                    if carup +1> row and row == 1: print("XXXXX")
                    if carup +1 == row and row == 1: print((16-col)*"X",car_length*"X",sep='')
                    if row == 2 and carup + 1 == row : print("X", (15 - col) * ' ', car_length*"X", sep='')
                    if row == 2 and carup + 1 < row < carup + car_height:print("X",(15-col)*' ',"X",(car_length-2)*" ","X",sep='')
                    if row == 2 and carup + 1 > row: print("X   X")
                    if row == 2 and car_height + carup == row: print("X", (15 - col) * ' ', car_length * "X", sep='')
                    if row == 3 and carup + 1 == row : print("X", (15 - col) * ' ', car_length*"X", sep='')
                    if row == 3 and carup + 1 < row < carup + car_height:print("X",(15-col)*' ',"X",(car_length-2)*" ","X",sep='')
                    if row == 3 and carup + 1 > row: print("X   X")
                    if row == 3 and car_height + carup == row: print("X", (15 - col) * ' ', car_length*"X", sep='')
                    if row == 4 and carup + 1 == row : print((16-col)*"X", car_length*"X", sep='')
                    if row == 4 and carup + 1 < row < carup + car_height:print((16-col)*"X","X",(car_length-2)*" ","X",sep='')
                    if row == 4 and car_height+ carup ==row: print((16-col)*"X",car_length*'X',sep='')
                    if row == 4 and carup + 1 > row: print("XXXXX")
                    if row == 5 and carup + 1 == row : print("  X ", car_length*"X", sep='')
                    if row == 5 and carup + 1 < row < carup + car_height:print("  X ","X",(car_length-2)*" ","X",sep='')
                    if row == 5 and car_height+ carup ==row: print("  X ",car_length*'X',sep='')
                    if row == 5 and carup + 1 > row: print("  X  ")
                    if row == 6 and carup + 1 == row : print((16-col)*"X", car_length*"X", sep='')
                    if row == 6 and carup + 1 < row < carup + car_height:print((16-col)*"X","X",(car_length-2)*" ","X",sep='')
                    if row == 6 and car_height+ carup ==row: print((16-col)*"X",car_length*'X',sep='')
                    if row == 6 and carup + 1 > row: print("XXXXX")
                    if 7 <= row <= 6 + man_height and carup + 1 == row : print("  X ", car_length*"X", sep='')
                    if 7 <= row <= 6 + man_height and car_height+ carup ==row: print("  X ", car_length * "X", sep='')
                    if 7 <= row <= 6 + man_height and car_height + carup < row: print("  X")
                    if 7 <= row <= 6 + man_height and carup + 1 < row < carup + car_height: print("  X ", "X",(car_length-2)*" ","X", sep='')
                    if 7 <= row <= 6 + man_height and carup + 1 > row: print("  X")
                    elif row == man_height + 7:print(' X X')
                    elif row == man_height + 8:print("X   X")
                    elif row == man_height + 9:
                        print(" ")
                if col == 13:
                    if carup +1> row and row == 1: print("XXXXX")
                    if carup +1 == row and row == 1: print((16-col)*"X",car_length*"X",sep='')
                    if row == 2 and carup + 1 == row : print("X", (15 - col) * ' ', car_length*"X", sep='')
                    if row == 2 and carup + 1 < row < carup + car_height:print("X",(15-col)*' ',"X",(car_length-2)*" ","X",sep='')
                    if row == 2 and carup + 1 > row: print("X   X")
                    if row == 2 and car_height + carup == row: print("X", (15 - col) * ' ', car_length * "X", sep='')
                    if row == 3 and carup + 1 == row : print("X", (15 - col) * ' ', car_length*"X", sep='')
                    if row == 3 and carup + 1 < row < carup + car_height:print("X",(15-col)*' ',"X",(car_length-2)*" ","X",sep='')
                    if row == 3 and carup + 1 > row: print("X   X")
                    if row == 3 and car_height + carup == row: print("X", (15 - col) * ' ', car_length*"X", sep='')
                    if row == 4 and carup + 1 == row : print((16-col)*"X", car_length*"X", sep='')
                    if row == 4 and carup + 1 < row < carup + car_height:print((16-col)*"X","X",(car_length-2)*" ","X",sep='')
                    if row == 4 and car_height+ carup ==row: print((16-col)*"X",car_length*'X',sep='')
                    if row == 4 and carup + 1 > row: print("XXXXX")
                    if row == 5 and carup + 1 == row : print("  X", car_length*"X", sep='')
                    if row == 5 and carup + 1 < row < carup + car_height:print("  X","X",(car_length-2)*" ","X",sep='')
                    if row == 5 and car_height+ carup ==row: print("  X",car_length*'X',sep='')
                    if row == 5 and carup + 1 > row: print("  X  ")
                    if row == 6 and carup + 1 == row : print((16-col)*"X", car_length*"X", sep='')
                    if row == 6 and carup + 1 < row < carup + car_height:print((16-col)*"X","X",(car_length-2)*" ","X",sep='')
                    if row == 6 and car_height+ carup ==row: print((16-col)*"X",car_length*'X',sep='')
                    if row == 6 and carup + 1 > row: print("XXXXX")
                    if 7 <= row <= 6 + man_height and carup + 1 == row : print("  X", car_length*"X", sep='')
                    if 7 <= row <= 6 + man_height and car_height+ carup ==row: print("  X", car_length * "X", sep='')
                    if 7 <= row <= 6 + man_height and car_height + carup < row: print("  X  ")
                    if 7 <= row <= 6 + man_height and carup + 1 < row < carup + car_height: print("  X", "X",(car_length-2)*" ","X", sep='')
                    if 7 <= row <= 6 + man_height and carup + 1 > row: print("  X  ")
                    elif row == man_height + 7:print(' X X')
                    elif row == man_height + 8:print("X   X")
                    elif row == man_height + 9:
                        print(" ")

                if col == 14:
                    if carup +1> row and row ==1: print("XXXXX")
                    if carup +1 == row and row == 1: print((16-col)*"X",car_length*"X",sep='')
                    if row == 2 and carup + 1 == row :print("X", (15 - col) * ' ', car_length*"X", sep='')
                    if row == 2 and carup + 1 < row < carup + car_height:print("X",(15-col)*' ',"X",(car_length-2)*" ","X",sep='')
                    if row == 2 and carup + 1 > row: print("X   X")
                    if row == 2 and car_height + carup == row: print("X", (15 - col) * ' ', car_length * "X", sep='')
                    if row == 3 and carup + 1 == row : print("X", (15 - col) * ' ', car_length*"X", sep='')
                    if row == 3 and carup + 1 < row < carup + car_height:print("X",(15-col)*' ',"X",(car_length-2)*" ","X",sep='')
                    if row == 3 and carup + 1 > row: print("X   X")
                    if row == 3 and car_height + carup == row: print("X", (15 - col) * ' ', car_length*"X", sep='')
                    if row == 4 and carup + 1 == row : print((16-col)*"X", car_length*"X", sep='')
                    if row == 4 and carup + 1 < row < carup + car_height:print((16-col)*"X","X",(car_length-2)*" ","X",sep='')
                    if row == 4 and car_height+ carup ==row: print((16-col)*"X",car_length*'X',sep='')
                    if row == 4 and carup + 1 > row: print("XXXXX")
                    if row == 5 and carup + 1 == row : print("  ", car_length*"X", sep='')
                    if row == 5 and carup + 1 < row < carup + car_height:print("  ","X",(car_length-2)*" ","X",sep='')
                    if row == 5 and car_height+ carup ==row: print("  ",car_length*'X',sep='')
                    if row == 5 and carup + 1 > row: print("  X")
                    if row == 6 and carup + 1 == row : print((16-col)*"X", car_length*"X", sep='')
                    if row == 6 and carup + 1 < row < carup + car_height:print((16-col)*"X","X",(car_length-2)*" ","X",sep='')
                    if row == 6 and car_height+ carup ==row: print((16-col)*"X",car_length*'X',sep='')
                    if row == 6 and carup + 1 > row: print("XXXXX")
                    if 7 <= row <= 6 + man_height and carup + 1 == row : print("  ", car_length*"X", sep='')
                    if 7 <= row <= 6 + man_height and car_height+ carup ==row: print("  ", car_length * "X", sep='')
                    if 7 <= row <= 6 + man_height and car_height + carup < row: print("  X")
                    if 7 <= row <= 6 + man_height and carup + 1 < row < carup + car_height: print("  ", "X",(car_length-2)*" ","X", sep='')
                    if 7 <= row <= 6 + man_height and carup + 1 > row: print("  X")
                    elif row == man_height + 7:print(' X X')
                    elif row == man_height + 8:print("X   X")
                    elif row == man_height + 9:
                        print(" ")
                if col == 15:
                    if carup +1> row and row ==1: print("XXXXX")
                    if carup +1 == row and row == 1: print((16-col)*"X",car_length*"X",sep='')
                    if row == 2 and carup + 1 == row : print("X", (15 - col) * ' ', car_length*"X", sep='')
                    if row == 2 and carup + 1 < row < carup + car_height:print("X",(15-col)*' ',"X",(car_length-2)*" ","X",sep='')
                    if row == 2 and carup + 1 > row: print("X   X")
                    if row == 2 and car_height + carup == row: print("X", (15 - col) * ' ', car_length * "X", sep='')
                    if row == 3 and carup + 1 == row : print("X", (15 - col) * ' ', car_length*"X", sep='')
                    if row == 3 and carup + 1 < row < carup + car_height:print("X",(15-col)*' ',"X",(car_length-2)*" ","X",sep='')
                    if row == 3 and carup + 1 > row: print("X   X")
                    if row == 3 and car_height + carup == row: print("X", (15 - col) * ' ', car_length*"X", sep='')
                    if row == 4 and carup + 1 == row : print((16-col)*"X", car_length*"X", sep='')
                    if row == 4 and carup + 1 < row < carup + car_height:print((16-col)*"X","X",(car_length-2)*" ","X",sep='')
                    if row == 4 and car_height+ carup ==row: print((16-col)*"X",car_length*'X',sep='')
                    if row == 4 and carup + 1 > row: print("XXXXX")
                    if row == 5 and carup + 1 == row : print(" ", car_length*"X", sep='')
                    if row == 5 and carup + 1 < row < carup + car_height:print(" ","X",(car_length-2)*" ","X",sep='')
                    if row == 5 and car_height+ carup ==row: print(" ",car_length*'X',sep='')
                    if row == 5 and carup + 1 > row: print("  X")
                    if row == 6 and carup + 1 == row : print((16-col)*"X", car_length*"X", sep='')
                    if row == 6 and carup + 1 < row < carup + car_height:print((16-col)*"X","X",(car_length-2)*" ","X",sep='')
                    if row == 6 and car_height+ carup ==row: print((16-col)*"X",car_length*'X',sep='')
                    if row == 6 and carup + 1 > row: print("XXXXX")
                    if 7 <= row <= 6 + man_height and carup + 1 == row : print(" ", car_length*"X", sep='')
                    if 7 <= row <= 6 + man_height and car_height+ carup ==row: print(" ", car_length * "X", sep='')
                    if 7 <= row <= 6 + man_height and car_height + carup < row: print("  X")
                    if 7 <= row <= 6 + man_height and carup + 1 < row < carup + car_height: print(" ", "X",(car_length-2)*" ","X", sep='')
                    if 7 <= row <= 6 + man_height and carup + 1 > row: print("  X")
                    elif row == man_height + 7:print(' X X')
                    elif row == man_height + 8:print("X   X")
                    elif row == man_height + 9:
                        print(" ")
                if col == 16:

                        if carup +1> row and row ==1: print("XXXXX")
                        if carup +1 == row and row == 1: print(car_length*"X","X",sep='')
                        if row == 2 and carup + 1 == row : print( car_length*"X","X", sep='')
                        if row == 2 and carup + 1 < row < carup + car_height:print("X",(car_length-2)*" ","X","X",sep='')
                        if row == 2 and carup + 1 > row: print("X   X")
                        if row == 2 and car_height + carup == row: print( car_length * "X", "X",sep='')
                        if row == 3 and carup + 1 == row : print( car_length*"X", "X",sep='')
                        if row == 3 and carup + 1 < row < carup + car_height:print("X",(car_length-2)*" ","X","X",sep='')
                        if row == 3 and carup + 1 > row: print("X   X")
                        if row == 3 and car_height + carup == row: print(car_length*"X", "X",sep='')
                        if row == 4 and carup + 1 == row : print( car_length*"X", "X",sep='')
                        if row == 4 and carup + 1 < row < carup + car_height:print("X",(car_length-2)*" ","X","X",  sep='')
                        if row == 4 and car_height+ carup ==row: print(car_length*'X',"X",sep='')
                        if row == 4 and carup + 1 > row: print("XXXXX")
                        if row == 5 and carup + 1 == row : print( car_length*"X", sep='')
                        if row == 5 and carup + 1 < row < carup + car_height:print("X",(car_length-2)*" ","X",sep='')
                        if row == 5 and car_height+ carup ==row: print(car_length*'X', sep='')
                        if row == 5 and carup + 1 > row: print("  X")
                        if row == 6 and carup + 1 == row : print( car_length*"X", "X",sep='')
                        if row == 6 and carup + 1 < row < carup + car_height:print("X",(car_length-2)*" ","X","X",sep='')
                        if row == 6 and car_height+ carup ==row: print(car_length*'X',"X",sep='')
                        if row == 6 and carup + 1 > row: print("XXXXX")
                        if 7 <= row <= 6 + man_height and carup + 1 == row : print( car_length*"X", sep='')
                        if 7 <= row <= 6 + man_height and car_height+ carup ==row: print( car_length * "X", sep='')
                        if 7 <= row <= 6 + man_height and car_height + carup < row: print("  X")
                        if 7 <= row <= 6 + man_height and carup + 1 < row < carup + car_height: print("X",(car_length-2)*" ","X",sep='')
                        if 7 <= row <= 6 + man_height and carup + 1 > row: print("  X")
                        elif row == man_height + 7:print(' X X')
                        elif row == man_height + 8:print("X   X")
                        elif row == man_height + 9:print(" ")

        if  colnumber -1 >= col > 16 and car_length - (col -16) >0:
            fcol = col - 16
            for row in range(1, 8 + man_height + 2):

                if row == 1 and carup +1> row: print("XXXXX")
                if carup + 1 == row and row == 1 and car_length - fcol >= 5: print((car_length - fcol) * "X", sep='')
                if carup + 1 == row and row == 1 and car_length - fcol < 5: print((car_length - fcol) * "X", (5 - (car_length - fcol)) *"X", sep='')
                if row == 2 and carup + 1 > row: print("X   X")
                if carup + 1 == row and row == 2 and car_length - fcol >= 5: print((car_length - fcol) * "X", sep='')
                if carup + 1 == row and row == 2 and car_length - fcol < 5: print((car_length - fcol) * "X",(4 - (car_length - fcol)) * " ","X", sep='')
                if carup + 1 < row < carup + car_height and row == 2 and car_length - fcol >= 5: print((car_length - fcol-1) * " ","X", sep='')
                if carup + 1 < row < carup + car_height and row == 2 and car_length - fcol < 5: print((car_length - fcol-1) * " ","X",(4 - (car_length - fcol)) * " ","X", sep='')
                if car_height+ carup ==row and row == 2 and car_length - fcol >= 5: print((car_length - fcol) * "X", sep='')
                if car_height+ carup ==row and row == 2 and car_length - fcol < 5: print((car_length - fcol) * "X",(4 - (car_length - fcol)) * " ","X", sep='')
                if row == 3 and carup + 1 > row: print("X   X")
                if carup + 1 == row and row == 3 and car_length - fcol >= 5: print((car_length - fcol) * "X", sep='')
                if carup + 1 == row and row == 3 and car_length - fcol < 5: print((car_length - fcol) * "X",(4 - (car_length - fcol)) * " ","X", sep='')
                if carup + 1 < row < carup + car_height and row == 3 and car_length - fcol >= 5: print((car_length - fcol-1) * " ","X", sep='')
                if carup + 1 < row < carup + car_height and row == 3 and car_length - fcol < 5: print((car_length - fcol-1) * " ","X",(4 - (car_length - fcol)) * " ","X", sep='')
                if car_height+ carup ==row and row == 3 and car_length - fcol >= 5: print((car_length - fcol) * "X", sep='')
                if car_height+ carup ==row and row == 3 and car_length - fcol < 5: print((car_length - fcol) * "X",(4 - (car_length - fcol)) * " ","X", sep='')
                if row == 4 and carup + 1 > row: print("XXXXX")
                if carup + 1 == row and row == 4 and car_length - fcol >= 5: print((car_length - fcol) * "X", sep='')
                if carup + 1 == row and row == 4 and car_length - fcol < 5: print((car_length - fcol) * "X",(5 - (car_length - fcol)) * "X", sep='')
                if carup + 1 < row < carup + car_height and row == 4 and car_length - fcol >= 5: print((car_length - fcol-1) * " ","X", sep='')
                if carup + 1 < row < carup + car_height and row == 4 and car_length - fcol < 5: print((car_length - fcol-1) * " ","X",(5 - (car_length - fcol)) * "X", sep='')
                if car_height+ carup ==row and row == 4 and car_length - fcol >= 5: print((car_length - fcol) * "X", sep='')
                if car_height+ carup ==row and row == 4 and car_length - fcol < 5: print((car_length - fcol) * "X",(5 - (car_length - fcol)) * "X", sep='')
                if row == 5 and car_length -fcol >= 3:
                    if carup + 1 > row :print("  X")
                    if carup + 1 == row :print((car_length - fcol) * "X", sep='')
                    if carup + 1 < row < carup + car_height: print((car_length - fcol-1) * " ","X",sep='')
                    if car_height+ carup ==row : print((car_length - fcol) * "X", sep='')
                elif row == 5 and car_length -fcol < 3:
                    if carup + 1 > row: print("  X")
                    if carup + 1 == row: print((car_length - fcol) * "X", (2 - (car_length - fcol)) * " ","X",sep='')
                    if carup + 1 < row < carup + car_height: print((car_length - fcol - 1) * " ", "X",(2 - (car_length - fcol)) * " ","X", sep='')
                    if car_height + carup == row: print((car_length - fcol) * "X", (2 - (car_length - fcol)) * " ","X",sep='')
                if row == 6 and carup + 1 > row: print("XXXXX")
                if carup + 1 == row and row == 6 and car_length - fcol >= 5: print((car_length - fcol) * "X", sep='')
                if carup + 1 == row and row == 6 and car_length - fcol < 5: print((car_length - fcol) * "X",(5 - (car_length - fcol)) * "X", sep='')
                if carup + 1 < row < carup + car_height and row == 6 and car_length - fcol >= 5: print((car_length - fcol - 1) * " ", "X", sep='')
                if carup + 1 < row < carup + car_height and row == 6 and car_length - fcol < 5: print((car_length - fcol - 1) * " ", "X", (5 - (car_length - fcol)) * "X", sep='')
                if car_height + carup == row and row == 6 and car_length - fcol >= 5: print((car_length - fcol) * "X",sep='')
                if car_height + carup == row and row == 6 and car_length - fcol < 5: print((car_length - fcol) * "X",(5 - (car_length - fcol)) * "X",sep='')
                if 7 <= row <= 6 + man_height and car_length -fcol >= 3:
                    if carup + 1 > row :print("  X")
                    if carup + 1 == row :print((car_length - fcol) * "X", sep='')
                    if carup + 1 < row < carup + car_height: print((car_length - fcol-1) * " ","X",sep='')
                    if car_height+ carup ==row : print((car_length - fcol) * "X", sep='')
                    if car_height + carup < row: print("  X")
                if 7 <= row <= 6 + man_height and car_length -fcol < 3:
                    if carup + 1 > row: print("  X")
                    if carup + 1 == row: print((car_length - fcol) * "X", (2 - (car_length - fcol)) * " ","X",sep='')
                    if carup + 1 < row < carup + car_height: print((car_length - fcol - 1) * " ", "X",(2 - (car_length - fcol)) * " ","X", sep='')
                    if car_height + carup == row: print((car_length - fcol) * "X", (2 - (car_length - fcol)) * " ","X",sep='')
                    if car_height + carup < row: print("  X")
                if row == man_height + 7:print(' X X')
                if row == man_height + 8: print('X   X')
                elif row == man_height + 9: print(" ")

        if car_length - (col - 16) == 0:
            for row in range(1, 8+man_height+1):
                if row == 1:print(5*"X")
                elif row == 2:print("X   X")
                elif row == 3:print("X   X")
                elif row == 4:print(5*"X")
                elif row == 5:print("  X")
                elif row == 6:print(5*"X")
                elif 7 <= row <= 6 + man_height:print("  X")
                elif row == man_height +7:print(' X X')
                elif row == man_height +8:print("X   X")

            exit()
elif car_length == 3:
    for col in range(1, colnumber + 1):
        if col <= 11:
            for row in range(1, 8 + man_height + 2):
                if row == 1:
                    if row == carup + 1:
                        print(5 * 'X', (11 - col) * ' ', car_length * 'X', sep='')
                    else:
                        print(5 * 'X', (11 - col) * ' ', sep='')
                elif row == 2:
                    if row == carup + 1:
                        print("X   X", (11 - col) * ' ', car_length * 'X', sep='')
                    elif row == carup + 2:
                        print("X   X", (11 - col) * ' ', 'X', (car_length - 2) * ' ', 'X', sep='')
                    else:
                        print('X   X')
                elif row == 3:
                    if row == carup + 1:print("X   X", (11 - col) * ' ', car_length * 'X', sep='')

                    elif carup + 1 < row < carup + car_height:
                        print("X   X", (11 - col) * ' ', 'X', (car_length - 2) * ' ', 'X', sep='')
                    elif row == carup + car_height:
                        print("X   X", (11 - col) * ' ', car_length * 'X', sep='')
                    else:
                        print('X   X')
                elif row == 4:
                    if row == carup + 1:
                        print(5 * "X", (11 - col) * ' ', car_length * 'X', sep='')
                    elif carup + 1 < row < carup + car_height:
                        print(5 * "X", (11 - col) * ' ', 'X', (car_length - 2) * ' ', 'X', sep='')
                    elif row == carup + car_height:
                        print(5 * "X", (11 - col) * ' ', car_length * 'X', sep='')
                    else:
                        print(5 * 'X')
                elif row == 5:
                    if row == carup + 1:
                        print('  X  ', (11 - col) * ' ', car_length * 'X', sep='')
                    elif carup + 1 < row < carup + car_height:
                        print('  X  ', (11 - col) * ' ', 'X', (car_length - 2) * ' ', 'X', sep='')
                    elif row == carup + car_height:
                        print('  X  ', (11 - col) * ' ', car_length * 'X', sep='')
                    else:
                        print('  X')
                elif row == 6:
                    if row == carup + 1:
                        print('XXXXX', (11 - col) * ' ', car_length * 'X', sep='')
                    elif carup + 1 < row < carup + car_height:
                        print('XXXXX', (11 - col) * ' ', 'X', (car_length - 2) * ' ', 'X', sep='')
                    elif row == carup + car_height:
                        print('XXXXX', (11 - col) * ' ', car_length * 'X', sep='')
                    else:
                        print('XXXXX')
                elif 7 <= row <= 6 + man_height:
                    if row == carup + 1:
                        print('  X  ', (11 - col) * ' ', car_length * 'X', sep='')
                    elif carup + 1 < row < carup + car_height:
                        print('  X  ', (11 - col) * ' ', 'X', (car_length - 2) * ' ', 'X', sep='')
                    elif row == carup + car_height:
                        print('  X  ', (11 - col) * ' ', car_length * 'X', sep='')
                    else:
                        print('  X')
                elif row == man_height + 7:
                    print(' X X')
                elif row == man_height + 8:
                    print("X   X")
                elif row == man_height + 9:
                    print(" ")
        if colnumber + 2 > col > 11:
            for row in range(1, 8 + man_height + 2):
                if col == 12:
                    if carup + 1 > row and row == 1: print("XXXXX")
                    if carup + 1 == row and row == 1: print((16 - col) * "X", car_length * "X", sep='')
                    if row == 2 and carup + 1 == row: print("X", (15 - col) * ' ', car_length * "X", sep='')
                    if row == 2 and carup + 1 < row < carup + car_height: print("X", (15 - col) * ' ', "X",
                                                                                (car_length - 2) * " ", "X", sep='')
                    if row == 2 and carup + 1 > row: print("X   X")
                    if row == 2 and car_height + carup == row: print("X", (15 - col) * ' ', car_length * "X", sep='')
                    if row == 3 and carup + 1 == row: print("X", (15 - col) * ' ', car_length * "X", sep='')
                    if row == 3 and carup + 1 < row < carup + car_height: print("X", (15 - col) * ' ', "X",
                                                                                (car_length - 2) * " ", "X", sep='')
                    if row == 3 and carup + 1 > row: print("X   X")
                    if row == 3 and car_height + carup == row: print("X", (15 - col) * ' ', car_length * "X", sep='')
                    if row == 4 and carup + 1 == row: print((16 - col) * "X", car_length * "X", sep='')
                    if row == 4 and carup + 1 < row < carup + car_height: print((16 - col) * "X", "X",
                                                                                (car_length - 2) * " ", "X", sep='')
                    if row == 4 and car_height + carup == row: print((16 - col) * "X", car_length * 'X', sep='')
                    if row == 4 and carup + 1 > row: print("XXXXX")
                    if row == 5 and carup + 1 == row: print("  X ", car_length * "X", sep='')
                    if row == 5 and carup + 1 < row < carup + car_height: print("  X ", "X", (car_length - 2) * " ",
                                                                                "X", sep='')
                    if row == 5 and car_height + carup == row: print("  X ", car_length * 'X', sep='')
                    if row == 5 and carup + 1 > row: print("  X  ")
                    if row == 6 and carup + 1 == row: print((16 - col) * "X", car_length * "X", sep='')
                    if row == 6 and carup + 1 < row < carup + car_height: print((16 - col) * "X", "X",
                                                                                (car_length - 2) * " ", "X", sep='')
                    if row == 6 and car_height + carup == row: print((16 - col) * "X", car_length * 'X', sep='')
                    if row == 6 and carup + 1 > row: print("XXXXX")
                    if 7 <= row <= 6 + man_height and carup + 1 == row: print("  X ", car_length * "X", sep='')
                    if 7 <= row <= 6 + man_height and car_height + carup == row: print("  X ", car_length * "X", sep='')
                    if 7 <= row <= 6 + man_height and car_height + carup < row: print("  X")
                    if 7 <= row <= 6 + man_height and carup + 1 < row < carup + car_height: print("  X ", "X", (
                                car_length - 2) * " ", "X", sep='')
                    if 7 <= row <= 6 + man_height and carup + 1 > row:
                        print("  X")
                    elif row == man_height + 7:
                        print(' X X')
                    elif row == man_height + 8:
                        print("X   X")
                    elif row == man_height + 9:
                        print(" ")
                if col == 13:
                    if carup + 1 > row and row == 1: print("XXXXX")
                    if carup + 1 == row and row == 1: print((16 - col) * "X", car_length * "X", sep='')
                    if row == 2 and carup + 1 == row: print("X", (15 - col) * ' ', car_length * "X", sep='')
                    if row == 2 and carup + 1 < row < carup + car_height: print("X", (15 - col) * ' ', "X",
                                                                                (car_length - 2) * " ", "X", sep='')
                    if row == 2 and carup + 1 > row: print("X   X")
                    if row == 2 and car_height + carup == row: print("X", (15 - col) * ' ', car_length * "X", sep='')
                    if row == 3 and carup + 1 == row: print("X", (15 - col) * ' ', car_length * "X", sep='')
                    if row == 3 and carup + 1 < row < carup + car_height: print("X", (15 - col) * ' ', "X",
                                                                                (car_length - 2) * " ", "X", sep='')
                    if row == 3 and carup + 1 > row: print("X   X")
                    if row == 3 and car_height + carup == row: print("X", (15 - col) * ' ', car_length * "X", sep='')
                    if row == 4 and carup + 1 == row: print((16 - col) * "X", car_length * "X", sep='')
                    if row == 4 and carup + 1 < row < carup + car_height: print((16 - col) * "X", "X",
                                                                                (car_length - 2) * " ", "X", sep='')
                    if row == 4 and car_height + carup == row: print((16 - col) * "X", car_length * 'X', sep='')
                    if row == 4 and carup + 1 > row: print("XXXXX")
                    if row == 5 and carup + 1 == row: print("  X", car_length * "X", sep='')
                    if row == 5 and carup + 1 < row < carup + car_height: print("  X", "X", (car_length - 2) * " ", "X",
                                                                                sep='')
                    if row == 5 and car_height + carup == row: print("  X", car_length * 'X', sep='')
                    if row == 5 and carup + 1 > row: print("  X  ")
                    if row == 6 and carup + 1 == row: print((16 - col) * "X", car_length * "X", sep='')
                    if row == 6 and carup + 1 < row < carup + car_height: print((16 - col) * "X", "X",
                                                                                (car_length - 2) * " ", "X", sep='')
                    if row == 6 and car_height + carup == row: print((16 - col) * "X", car_length * 'X', sep='')
                    if row == 6 and carup + 1 > row: print("XXXXX")
                    if 7 <= row <= 6 + man_height and carup + 1 == row: print("  X", car_length * "X", sep='')
                    if 7 <= row <= 6 + man_height and car_height + carup == row: print("  X", car_length * "X", sep='')
                    if 7 <= row <= 6 + man_height and car_height + carup < row: print("  X  ")
                    if 7 <= row <= 6 + man_height and carup + 1 < row < carup + car_height: print("  X", "X", (
                                car_length - 2) * " ", "X", sep='')
                    if 7 <= row <= 6 + man_height and carup + 1 > row:
                        print("  X  ")
                    elif row == man_height + 7:
                        print(' X X')
                    elif row == man_height + 8:
                        print("X   X")
                    elif row == man_height + 9:
                        print(" ")

                if col == 14:
                    if carup + 1 > row and row == 1: print("XXXXX")
                    if carup + 1 == row and row == 1: print((16 - col) * "X", car_length * "X", sep='')
                    if row == 2 and carup + 1 == row: print("X", (15 - col) * ' ', car_length * "X", sep='')
                    if row == 2 and carup + 1 < row < carup + car_height: print("X", (15 - col) * ' ', "X",
                                                                                (car_length - 2) * " ", "X", sep='')
                    if row == 2 and carup + 1 > row: print("X   X")
                    if row == 2 and car_height + carup == row: print("X", (15 - col) * ' ', car_length * "X", sep='')
                    if row == 3 and carup + 1 == row: print("X", (15 - col) * ' ', car_length * "X", sep='')
                    if row == 3 and carup + 1 < row < carup + car_height: print("X", (15 - col) * ' ', "X",
                                                                                (car_length - 2) * " ", "X", sep='')
                    if row == 3 and carup + 1 > row: print("X   X")
                    if row == 3 and car_height + carup == row: print("X", (15 - col) * ' ', car_length * "X", sep='')
                    if row == 4 and carup + 1 == row: print((16 - col) * "X", car_length * "X", sep='')
                    if row == 4 and carup + 1 < row < carup + car_height: print((16 - col) * "X", "X",
                                                                                (car_length - 2) * " ", "X", sep='')
                    if row == 4 and car_height + carup == row: print((16 - col) * "X", car_length * 'X', sep='')
                    if row == 4 and carup + 1 > row: print("XXXXX")
                    if row == 5 and carup + 1 == row: print("  ", car_length * "X", sep='')
                    if row == 5 and carup + 1 < row < carup + car_height: print("  ", "X", (car_length - 2) * " ", "X",
                                                                                sep='')
                    if row == 5 and car_height + carup == row: print("  ", car_length * 'X', sep='')
                    if row == 5 and carup + 1 > row: print("  X")
                    if row == 6 and carup + 1 == row: print((16 - col) * "X", car_length * "X", sep='')
                    if row == 6 and carup + 1 < row < carup + car_height: print((16 - col) * "X", "X",
                                                                                (car_length - 2) * " ", "X", sep='')
                    if row == 6 and car_height + carup == row: print((16 - col) * "X", car_length * 'X', sep='')
                    if row == 6 and carup + 1 > row: print("XXXXX")
                    if 7 <= row <= 6 + man_height and carup + 1 == row: print("  ", car_length * "X", sep='')
                    if 7 <= row <= 6 + man_height and car_height + carup == row: print("  ", car_length * "X", sep='')
                    if 7 <= row <= 6 + man_height and car_height + carup < row: print("  X")
                    if 7 <= row <= 6 + man_height and carup + 1 < row < carup + car_height: print("  ", "X", (
                                car_length - 2) * " ", "X", sep='')
                    if 7 <= row <= 6 + man_height and carup + 1 > row:
                        print("  X")
                    elif row == man_height + 7:
                        print(' X X')
                    elif row == man_height + 8:
                        print("X   X")
                    elif row == man_height + 9:
                        print(" ")
                if col == 15:
                    if carup + 1 > row and row == 1: print("XXXXX")
                    if carup + 1 == row and row == 1: print((16 - col) * "X", car_length * "X", "X",sep='')
                    if row == 2 and carup + 1 == row: print("X", (15 - col) * ' ', car_length * "X","X", sep='')
                    if row == 2 and carup + 1 < row < carup + car_height: print("X", (15 - col) * ' ', "X",(car_length - 2) * " ", "X","X", sep='')
                    if row == 2 and carup + 1 > row: print("X   X")
                    if row == 2 and car_height + carup == row: print("X", (15 - col) * ' ', car_length * "X","X", sep='')
                    if row == 3 and carup + 1 == row: print("X", (15 - col) * ' ', car_length * "X", "X",sep='')
                    if row == 3 and carup + 1 < row < carup + car_height: print("X", (15 - col) * ' ', "X",(car_length - 2) * " ", "X", "X",sep='')
                    if row == 3 and carup + 1 > row: print("X   X")
                    if row == 3 and car_height + carup == row: print("X", (15 - col) * ' ', car_length * "X","X", sep='')
                    if row == 4 and carup + 1 == row: print((16 - col) * "X", car_length * "X", "X",sep='')
                    if row == 4 and carup + 1 < row < carup + car_height: print((16 - col) * "X", "X",(car_length - 2) * " ", "X","X", sep='')
                    if row == 4 and car_height + carup == row: print((16 - col) * "X", car_length * 'X', "X",sep='')
                    if row == 4 and carup + 1 > row: print("XXXXX")
                    if row == 5 and carup + 1 == row: print(" ", car_length * "X", sep='')
                    if row == 5 and carup + 1 < row < carup + car_height: print(" ", "X", (car_length - 2) * " ", "X",sep='')
                    if row == 5 and car_height + carup == row: print(" ", car_length * 'X', sep='')
                    if row == 5 and carup + 1 > row: print("  X")
                    if row == 6 and carup + 1 == row: print((16 - col) * "X", car_length * "X", "X",sep='')
                    if row == 6 and carup + 1 < row < carup + car_height: print((16 - col) * "X", "X",(car_length - 2) * " ", "X","X", sep='')
                    if row == 6 and car_height + carup == row: print((16 - col) * "X", car_length * 'X',"X", sep='')
                    if row == 6 and carup + 1 > row: print("XXXXX")
                    if 7 <= row <= 6 + man_height and carup + 1 == row: print(" ", car_length * "X", sep='')
                    if 7 <= row <= 6 + man_height and car_height + carup == row: print(" ", car_length * "X", sep='')
                    if 7 <= row <= 6 + man_height and car_height + carup < row: print("  X")
                    if 7 <= row <= 6 + man_height and carup + 1 < row < carup + car_height: print(" ", "X", (
                                car_length - 2) * " ", "X", sep='')
                    if 7 <= row <= 6 + man_height and carup + 1 > row:
                        print("  X")
                    elif row == man_height + 7:
                        print(' X X')
                    elif row == man_height + 8:
                        print("X   X")
                    elif row == man_height + 9:
                        print(" ")
                if col == 16:

                    if carup + 1 > row and row == 1: print("XXXXX")
                    if carup + 1 == row and row == 1: print(car_length * "X", "X", "X",sep='')
                    if row == 2 and carup + 1 == row: print(car_length * "X"," ", "X", sep='')
                    if row == 2 and carup + 1 < row < carup + car_height: print("X", (car_length - 2) * " ", "X"," ", "X",sep='')
                    if row == 2 and carup + 1 > row: print("X   X")
                    if row == 2 and car_height + carup == row: print(car_length * "X"," ", "X", sep='')
                    if row == 3 and carup + 1 == row: print(car_length * "X", " ","X", sep='')
                    if row == 3 and carup + 1 < row < carup + car_height: print("X", (car_length - 2) * " ", "X"," ", "X",sep='')
                    if row == 3 and carup + 1 > row: print("X   X")
                    if row == 3 and car_height + carup == row: print(car_length * "X", " ","X", sep='')
                    if row == 4 and carup + 1 == row: print(car_length * "X", "X", "X",sep='')
                    if row == 4 and carup + 1 < row < carup + car_height: print("X", (car_length - 2) * " ", "X", "X","X",sep='')
                    if row == 4 and car_height + carup == row: print(car_length * 'X', "X","X", sep='')
                    if row == 4 and carup + 1 > row: print("XXXXX")
                    if row == 5 and carup + 1 == row: print(car_length * "X", sep='')
                    if row == 5 and carup + 1 < row < carup + car_height: print("X", (car_length - 2) * " ", "X",
                                                                                sep='')
                    if row == 5 and car_height + carup == row: print(car_length * 'X', sep='')
                    if row == 5 and carup + 1 > row: print("  X")
                    if row == 6 and carup + 1 == row: print(car_length * "X", "X","X", sep='')
                    if row == 6 and carup + 1 < row < carup + car_height: print("X", (car_length - 2) * " ", "X", "X","X",sep='')
                    if row == 6 and car_height + carup == row: print(car_length * 'X', "X","X", sep='')
                    if row == 6 and carup + 1 > row: print("XXXXX")
                    if 7 <= row <= 6 + man_height and carup + 1 == row: print(car_length * "X", sep='')
                    if 7 <= row <= 6 + man_height and car_height + carup == row: print(car_length * "X", sep='')
                    if 7 <= row <= 6 + man_height and car_height + carup < row: print("  X")
                    if 7 <= row <= 6 + man_height and carup + 1 < row < carup + car_height: print("X", (
                                car_length - 2) * " ", "X", sep='')
                    if 7 <= row <= 6 + man_height and carup + 1 > row:
                        print("  X")
                    elif row == man_height + 7:
                        print(' X X')
                    elif row == man_height + 8:
                        print("X   X")
                    elif row == man_height + 9:
                        print(" ")

        if colnumber - 1 >= col > 16 and car_length - (col - 16) > 0:
            fcol = col - 16
            for row in range(1, 8 + man_height + 2):

                if row == 1 and carup + 1 > row: print("XXXXX")
                if carup + 1 == row and row == 1 and car_length - fcol >= 5: print((car_length - fcol) * "X", sep='')
                if carup + 1 == row and row == 1 and car_length - fcol < 5: print((car_length - fcol) * "X",
                                                                                  (5 - (car_length - fcol)) * "X",
                                                                                  sep='')
                if row == 2 and carup + 1 > row: print("X   X")
                if carup + 1 == row and row == 2 and car_length - fcol >= 5: print((car_length - fcol) * "X", sep='')
                if carup + 1 == row and row == 2 and car_length - fcol < 5: print((car_length - fcol) * "X",
                                                                                  (4 - (car_length - fcol)) * " ", "X",
                                                                                  sep='')
                if carup + 1 < row < carup + car_height and row == 2 and car_length - fcol >= 5: print(
                    (car_length - fcol - 1) * " ", "X", sep='')
                if carup + 1 < row < carup + car_height and row == 2 and car_length - fcol < 5: print(
                    (car_length - fcol - 1) * " ", "X", (4 - (car_length - fcol)) * " ", "X", sep='')
                if car_height + carup == row and row == 2 and car_length - fcol >= 5: print((car_length - fcol) * "X",
                                                                                            sep='')
                if car_height + carup == row and row == 2 and car_length - fcol < 5: print((car_length - fcol) * "X", (
                            4 - (car_length - fcol)) * " ", "X", sep='')
                if row == 3 and carup + 1 > row: print("X   X")
                if carup + 1 == row and row == 3 and car_length - fcol >= 5: print((car_length - fcol) * "X", sep='')
                if carup + 1 == row and row == 3 and car_length - fcol < 5: print((car_length - fcol) * "X",
                                                                                  (4 - (car_length - fcol)) * " ", "X",
                                                                                  sep='')
                if carup + 1 < row < carup + car_height and row == 3 and car_length - fcol >= 5: print(
                    (car_length - fcol - 1) * " ", "X", sep='')
                if carup + 1 < row < carup + car_height and row == 3 and car_length - fcol < 5: print(
                    (car_length - fcol - 1) * " ", "X", (4 - (car_length - fcol)) * " ", "X", sep='')
                if car_height + carup == row and row == 3 and car_length - fcol >= 5: print((car_length - fcol) * "X",
                                                                                            sep='')
                if car_height + carup == row and row == 3 and car_length - fcol < 5: print((car_length - fcol) * "X", (
                            4 - (car_length - fcol)) * " ", "X", sep='')
                if row == 4 and carup + 1 > row: print("XXXXX")
                if carup + 1 == row and row == 4 and car_length - fcol >= 5: print((car_length - fcol) * "X", sep='')
                if carup + 1 == row and row == 4 and car_length - fcol < 5: print((car_length - fcol) * "X",
                                                                                  (5 - (car_length - fcol)) * "X",
                                                                                  sep='')
                if carup + 1 < row < carup + car_height and row == 4 and car_length - fcol >= 5: print(
                    (car_length - fcol - 1) * " ", "X", sep='')
                if carup + 1 < row < carup + car_height and row == 4 and car_length - fcol < 5: print(
                    (car_length - fcol - 1) * " ", "X", (5 - (car_length - fcol)) * "X", sep='')
                if car_height + carup == row and row == 4 and car_length - fcol >= 5: print((car_length - fcol) * "X",
                                                                                            sep='')
                if car_height + carup == row and row == 4 and car_length - fcol < 5: print((car_length - fcol) * "X", (
                            5 - (car_length - fcol)) * "X", sep='')
                if row == 5 and car_length - fcol >= 3:
                    if carup + 1 > row: print("  X")
                    if carup + 1 == row: print((car_length - fcol) * "X", sep='')
                    if carup + 1 < row < carup + car_height: print((car_length - fcol - 1) * " ", "X", sep='')
                    if car_height + carup == row: print((car_length - fcol) * "X", sep='')
                elif row == 5 and car_length - fcol < 3:
                    if carup + 1 > row: print("  X")
                    if carup + 1 == row: print((car_length - fcol) * "X", (2 - (car_length - fcol)) * " ", "X", sep='')
                    if carup + 1 < row < carup + car_height: print((car_length - fcol - 1) * " ", "X",
                                                                   (2 - (car_length - fcol)) * " ", "X", sep='')
                    if car_height + carup == row: print((car_length - fcol) * "X", (2 - (car_length - fcol)) * " ", "X",
                                                        sep='')
                if row == 6 and carup + 1 > row: print("XXXXX")
                if carup + 1 == row and row == 6 and car_length - fcol >= 5: print((car_length - fcol) * "X", sep='')
                if carup + 1 == row and row == 6 and car_length - fcol < 5: print((car_length - fcol) * "X",
                                                                                  (5 - (car_length - fcol)) * "X",
                                                                                  sep='')
                if carup + 1 < row < carup + car_height and row == 6 and car_length - fcol >= 5: print(
                    (car_length - fcol - 1) * " ", "X", sep='')
                if carup + 1 < row < carup + car_height and row == 6 and car_length - fcol < 5: print(
                    (car_length - fcol - 1) * " ", "X", (5 - (car_length - fcol)) * "X", sep='')
                if car_height + carup == row and row == 6 and car_length - fcol >= 5: print((car_length - fcol) * "X",
                                                                                            sep='')
                if car_height + carup == row and row == 6 and car_length - fcol < 5: print((car_length - fcol) * "X", (
                            5 - (car_length - fcol)) * "X", sep='')
                if 7 <= row <= 6 + man_height and car_length - fcol >= 3:
                    if carup + 1 > row: print("  X")
                    if carup + 1 == row: print((car_length - fcol) * "X", sep='')
                    if carup + 1 < row < carup + car_height: print((car_length - fcol - 1) * " ", "X", sep='')
                    if car_height + carup == row: print((car_length - fcol) * "X", sep='')
                    if car_height + carup < row: print("  X")
                if 7 <= row <= 6 + man_height and car_length - fcol < 3:
                    if carup + 1 > row: print("  X")
                    if carup + 1 == row: print((car_length - fcol) * "X", (2 - (car_length - fcol)) * " ", "X", sep='')
                    if carup + 1 < row < carup + car_height: print((car_length - fcol - 1) * " ", "X",
                                                                   (2 - (car_length - fcol)) * " ", "X", sep='')
                    if car_height + carup == row: print((car_length - fcol) * "X", (2 - (car_length - fcol)) * " ", "X",
                                                        sep='')
                    if car_height + carup < row: print("  X")
                if row == man_height + 7: print(' X X')
                if row == man_height + 8:
                    print('X   X')
                elif row == man_height + 9:
                    print(" ")

        if car_length - (col - 16) == 0:
            for row in range(1, 8 + man_height + 1):
                if row == 1:
                    print(5 * "X")
                elif row == 2:
                    print("X   X")
                elif row == 3:
                    print("X   X")
                elif row == 4:
                    print(5 * "X")
                elif row == 5:
                    print("  X")
                elif row == 6:
                    print(5 * "X")
                elif 7 <= row <= 6 + man_height:
                    print("  X")
                elif row == man_height + 7:
                    print(' X X')
                elif row == man_height + 8:
                    print("X   X")

# DO_NOT_EDIT_ANYTHING_BELOW_THIS_LINE
