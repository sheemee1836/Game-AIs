import math

ROWS = [[x,x+1,x+2] for x in (0,3,6)]
COLS = [[x,x+3,x+6] for x in (0,1,2)]
DIAGS = [[0,4,8],[2,4,6]]
UNITS = ROWS+COLS+DIAGS

XWINS, OWINS, TIE, CONTINUE = 1,-1,2,3
X = "X"
O = "O"

SCORE = {XWINS:1, OWINS:-1, TIE:0}
result_string = {XWINS: "X wins", OWINS: "O Wins", TIE: "Tie", CONTINUE: "Error"}
NEXT = {X:O, O:X}

START_BOARD = "."*9
DEBUG = False

class node:
    def __init__(self, board, move):
        self.board = board
        self.score = None
        self.last_move = move

def print_board(board):
    print("%s\n%s\n%s" % ( board[:3],board[3:6],board[6:]))

def goal_test(board):
    for S in UNITS:
        if all([board[j]==X for j in S]): return XWINS
        if all([board[j]==O for j in S]): return OWINS
    if board.find(".") == -1:
        return TIE
    return CONTINUE

def get_moves(board, player):
    return [x for x in range(len(board)) if board[x]=="."]

def make_move(board, move, player):
    assert(board[move]==".")
    return board[:move]+player+board[move+1:]

def minimax(n, player):
    result = goal_test(n.board)
    if result != CONTINUE:
        node.score = SCORE[result]
        return node

    children = [node(make_move(n.board, x, player), x) for x in get_moves(n.board, player)]
    for c in children:
        c.score = minimax(c, NEXT[player]).score

    if player == X:
        return max(children, key = lambda x: x.score)
    if player == O:
        return min(children, key = lambda x: x.score)

def minimax_strategy(board, player):
    if board==START_BOARD: return 4
    return minimax(node(board, -1), player).last_move

def human_strategy(board, player):
    move = int(input("Which move, %s? " % player))
    return move

def play_game(p1, p2):
    board = START_BOARD
    over = False
    player = X
    strategy = p1 #this is a function pointer!
    other = {X:O, O:X, p1:p2, p2:p1}

    while(not over):
        move = strategy(board, player) # works because p1 and p2 have the same parameter list (board, player)
        print("Player %s makes move %i" % (player, move))
        board = make_move(board, move, player)
        # does not check for valid moves!
        print_board(board)

        result = goal_test(board)
        player = other[player]
        strategy = other[strategy]
        over = (result != CONTINUE)
    print(result_string[result])


# Main plays AI vs AI
if __name__ == "__main__":
    play_game(minimax_strategy, human_strategy)
