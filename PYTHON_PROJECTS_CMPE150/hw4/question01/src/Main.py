print("Enter k:")
k = int(input())
print("Enter n:")
n = int(input())
board = [[0 for i in range(k**2)] for j in range(k**2)]

# DO_NOT_EDIT_ANYTHING_ABOVE_THIS_LINE

blank = ""
def print_board():
    for i in range(k**2):
        print("|",end="")
        for j in range(k**2):
            if board[i][j] != 0:

                print(f"{board[i][j]:>{len(str(n))}}", end = "")
                print("|",end="")
            else:

                print(f"{blank:<{len(str(n))}}", end="")
                print("|",end="")

        print()

def make_move(move):
    x, y, val = move
    row = (x // k) * k + y // k
    col = (x % k) * k + y % k
    a, b = row, col
    prev_val = board[x][y]
    board[a][b] = val
    return prev_val
def verify_board():
    for i in range(k**2):
        if sum(board[i]) > n or sum([board[j][i] for j in range(k**2)]) > n:
            return -1
    for i in range(0, k**2, k):
        for j in range(0, k**2, k):
            if sum([board[p][q] for p in range(i, i+k) for q in range(j, j+k)]) > n:
                return -1
    if all(sum(board[i]) == n for i in range(k**2)) and all(sum([board[j][i] for j in range(k**2)]) == n for i in range(k**2)):
        return 1
    return 0

# DO_NOT_EDIT_ANYTHING_BELOW_THIS_LINE

print_board()
print("Next Move:")
command = ""
while command != "end":
    usr_inp = input().split()
    command = usr_inp[0]
    if command == "move":
        move = int(usr_inp[1]), int(usr_inp[2]), int(usr_inp[3])
        prev_val = make_move(move)
        result = verify_board()
        # If not valid move, undo the move
        if -1 == result:
            move = move[0], move[1], prev_val
            make_move(move)
            print_board()
            print("Your move was invalid, please try again:")
        # If the board wins, end the game
        elif 1 == result:
            print_board()
            print("Congratulations! You have solved the puzzle!")
            break
        else:
            print_board()
            print("Next Move:")




