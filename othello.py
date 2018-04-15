# Jan 12, 0952 version

import random
import math

#### Othello Shell
#### P. White 2016-2018


EMPTY, BLACK, WHITE, OUTER = '.', '@', 'o', '?'

# To refer to neighbor squares we can add a direction to a square.
N, S, E, W = -10, 10, 1, -1
NE, SE, NW, SW = N + E, S + E, N + W, S + W
DIRECTIONS = (N, NE, E, SE, S, SW, W, NW)
PLAYERS = {BLACK: "Black", WHITE: "White"}
OTHER = {BLACK: WHITE, WHITE: BLACK}
SCORING_MATRIX = [
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 6, -3, 2, 2, 2, 2, -3, 6, 0,
    0, -3, -4, -1, -1, -1, -1, -4, -3, 0,
    0, 2, -1, 1, 0, 0, 1, -1, 2, 0,
    0, 2, -1, 0, 1, 1, 0, -1, 2, 0,
    0, 2, -1, 0, 1, 1, 0, -1, 2, 0,
    0, 2, -1, 1, 0, 0, 1, -1, 2, 0,
    0, -3, -4, -1, -1, -1, -1, -4, -3, 0,
    0, 6, -3, 2, 2, 2, 2, -3, 6, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
]
STABLE_PIECES = {BLACK:set(), WHITE:set()}


########## ########## ########## ########## ########## ##########
# The strategy class for your AI
# You must implement this class
# and the method best_strategy
# Do not tamper with the init method's parameters, or best_strategy's parameters
# But you can change anything inside this you want otherwise
#############################################################
class Node:
    def __init__(self, board, move):
        self.board = board
        self.score = 0
        self.move = move


class Strategy():
    def __init__(self):
        pass

    def get_starting_board(self):
        """Create a new board with the initial black and white positions filled."""
        return '???????????........??........??........??...o@...??...@o...??........??........??........???????????'

    def get_pretty_board(self, board):
        """Get a string representation of the board."""
        for i in range(10):
            print(board[i * 10: (i + 1) * 10])

    def opponent(self, player):
        """Get player's opponent."""
        return OTHER[player]

    def find_match(self, board, player, square, direction):
        """
        Check if 'square' forms a match with a square for `player` in the given
        `direction`.  Returns None if no such square exists.
        """
        s = square + direction
        # print("S-----", s, "PLAYER-----", player)
        while board[s] == OTHER[player]:
            s += direction
            if board[s] == player:
                return square
        return None

    def is_move_valid(self, board, player, move):
        """Is this a legal move for the player?"""
        if board[move] == EMPTY:
            for d in DIRECTIONS:
                s = self.find_match(board, player, move, d)
                if s != None:
                    return True
        return False

    def make_move(self, board, player, move):
        """Update the board to reflect the move by the specified player."""
        # returns a new board/string
        for d in DIRECTIONS:
            s = self.find_match(board, player, move, d)
            if s != None:
                board = board[:s] + player + board[s + 1:]
                flip = s + d
                while board[flip] == OTHER[player]:
                    board = board[:flip] + player + board[flip + 1:]
                    flip += d
        return board

    def get_valid_moves(self, board, player):
        """Get a list of all legal moves for player."""
        moves = []
        # print("BOARD---------------", board)
        for j in [i for i, ltr in enumerate(board) if ltr == EMPTY]:
            if self.is_move_valid(board, player, j):
                moves.append(j)
        return moves

    def has_any_valid_moves(self, board, player):
        """Can player make any moves?"""
        if len(self.get_valid_moves(board, player)) != 0:
            return True
        return False

    def next_player(self, board, prev_player):
        """Which player should move next?  Returns None if no legal moves exist."""
        if self.has_any_valid_moves(board, OTHER[prev_player]):
            return OTHER[prev_player]
        elif self.has_any_valid_moves(board, prev_player):
            return prev_player
        else:
            return None

    def score(self, board, move):
        """Compute player's score). Takes into account weights of each square, move stability, mobility, and corners captured"""
        score = 10 * self.weight_score(board) + 30 * self.corner_score(board) + 5 * self.mobility_score(board) + 25 * self.stability_score(board, move)
        return score

    def weight_score(self, board):
        b = 0
        w = 0
        for i in range(11, 89):
            if board[i] == BLACK:
                b += SCORING_MATRIX[i]
            elif board[i] == WHITE:
                w += SCORING_MATRIX[i]
        return b - w

    def stability_score(self, board, move):
        stability = 0
        discs_flipped = []
        player = board[move]
        for d in DIRECTIONS:
            flip = move + d
            while board[flip] == player:
                discs_flipped.append(flip)
                flip += d
        for disc in discs_flipped:
            if self.is_stable(board, disc):
                STABLE_PIECES[player].add(disc)
        b = len(STABLE_PIECES[BLACK])
        w = len(STABLE_PIECES[WHITE])
        if (b + w != 0):
            stability = math.trunc(100 * (b - w) / (b + w))
        return stability

    def is_stable(self, board, move):
        player = board[move]
        s = move
        for d in DIRECTIONS:
            while board[s] == OTHER[player]:
                s += d
                if board[s] == player and board[move - d] == EMPTY:
                    return False
        return True

    def mobility_score(self, board):
        actual_mobility = 0
        b = len(self.get_valid_moves(board, BLACK))
        w = len(self.get_valid_moves(board, WHITE))
        if (b + w != 0):
            actual_mobility = math.trunc(100 * (b - w) / (b + w))
        # number of potential moves (any empty square adjacent to opponent's disc)
        potential_mobility = 0
        b = 0
        w = 0
        for j in [i for i, ltr in enumerate(board) if ltr == EMPTY]:
            for d in DIRECTIONS:
                s = board[j + d]
                if s == BLACK:
                    w += 1
                    # because this is a potential move for white
                elif s == WHITE:
                    b += 1
        if (b + w != 0):
            potential_mobility = math.trunc(100 * (b - w) / (b + w))
        return .7 * actual_mobility + .3 * potential_mobility

    def corner_score(self, board):
        b = 0
        w = 0
        for i in [11, 18, 81, 88]:
            if board[i] == BLACK:
                b += 3
            elif board[i] == WHITE:
                w += 3
            else:
                # scoring potential corners
                if self.surrounding_pieces(i) == BLACK:
                    w += 1
                elif self.surrounding_pieces(i) == WHITE:
                    b += 1
        if (b + w != 0):
            return math.trunc(100 * (b - w) / (b + w))
        return 0

    def is_corner(self, move):
        if move == 11 or move == 18 or move == 81 or move == 88:
            return True
        return False

    def surrounding_pieces(self, move):
        pieces = []
        for d in DIRECTIONS:
            pieces.append(move + d)
        return pieces

    def weight_flip(self, weights, move):
        """flips the weight of the squares surrounding a move. Mainly used on corner pieces"""
        for d in DIRECTIONS:
            weights[move + d] *= -1


    def game_over(self, board, player):
        """Return true if player and opponent have no valid moves"""
        return self.has_any_valid_moves(board, player)

    def score2(self, board):
        score = 1
        for i in range(0, 99):
            if board[i] == BLACK:
                score += 1
            elif board[i] == WHITE:
                score -= 1
        return score

    ### Monitoring players

    class IllegalMoveError(Exception):
        def __init__(self, player, move, board):
            self.player = player
            self.move = move
            self.board = board

        def __str__(self):
            return '%s cannot move to square %d' % (PLAYERS[self.player], self.move)

    ################ strategies #################

    def minmax_search(self, node, player, depth):
        # determine best move for player recursively
        # it may return a move, or a search node, depending on your design
        # feel free to adjust the parameters
        weights = SCORING_MATRIX[:]
        board = node.board
        if depth == 0:
            node.score = self.score(board)
            return node

        my_moves = self.get_valid_moves(player)

        children = []
        for move in my_moves:
            next_board = self.make_move(board, player, move)
            next_player = self.next_player(next_board, player)
            if self.is_corner(move):
                weight_flip(move)
            if next_player == None:
                c = Node(next_board, move)
                c.score = 1000 * self.score(next_board)
                children.append(c)
            else:
                c = Node(next_board, move)
                c.move = move
                c.score = self.minmax_search(c, next_player, depth=depth - 1).score
                children.append(c)

                # return max(children, key = lambda x: x.score)
        if player == BLACK:
            winner = max(children, key=lambda x: x.score)
        else:
            winner = min(children, key=lambda x: x.score)
        node.score = winner.score
        return winner

    def minmax_strategy(self, board, player, depth=4):
        # calls minmax_search
        # feel free to adjust the parameters
        # returns an integer move
        return self.minmax_search(Node(board, None), player, depth).move

    def alpha_beta(self, node, player, alpha, beta, depth):
        # determine best move for player recursively
        # it may return a move, or a search node, depending on your design
        # feel free to adjust the parameters
        board = node.board
        if depth == 0:
            node.score = self.score(board, node.move)
            return node

        my_moves = self.get_valid_moves(board, player)

        children = []
        for move in my_moves:
            next_board = self.make_move(board, player, move)
            next_player = self.next_player(next_board, player)
            if next_player == None:
                c = Node(next_board, move)
                c.score = 1000 * self.score(next_board, move)
                children.append(c)
            else:
                c = Node(next_board, move)
                c.score = self.alpha_beta(c, next_player, alpha, beta, depth - 1).score
                children.append(c)
                if player == BLACK:
                    alpha = max(c.score, alpha)
                else:
                    beta = min(c.score, beta)
                if alpha >= beta:
                    break

        if player == BLACK:
            winner = max(children, key=lambda x: x.score + random.random())
        else:
            winner = min(children, key=lambda x: x.score)
        node.score = winner.score
        return winner

    def alpha_beta_strategy(self, board, player, depth = 4, alpha=-math.inf, beta=math.inf):
        return self.alpha_beta(Node(board, None), player, alpha, beta, depth).move

    def random_strategy(self, board, player):
        return random.choice(self.get_valid_moves(board, player))

    def best_strategy(self, board, player, best_move, still_running):
        ## THIS IS the public function you must implement
        ## Run your best search in a loop and update best_move.value
        board = ''.join(board)
        depth = 1
        while (True):
            best_move.value = self.alpha_beta_strategy(board, player, depth)
            depth += 2

    standard_strategy = alpha_beta_strategy


###############################################
# The main game-playing code
# You can probably run this without modification
################################################
import time
from multiprocessing import Value, Process
import os, signal

silent = False


#################################################
# StandardPlayer runs a single game
# it calls Strategy.standard_strategy(board, player)
#################################################
class StandardPlayer():
    def __init__(self):
        pass

    def play(self):
        ### create 2 opponent objects and one referee to play the game
        ### these could all be from separate files
        ref = Strategy()
        black = Strategy()
        white = Strategy()

        print("Playing Standard Game")
        board = ref.get_starting_board()
        player = BLACK
        strategy = {BLACK: black.standard_strategy, WHITE: white.random_strategy}
        print(ref.get_pretty_board(board))

        while player is not None:
            move = strategy[player](board, player)
            print("Player %s chooses %i" % (player, move))
            board = ref.make_move(board, player, move)
            print(ref.get_pretty_board(board))
            player = ref.next_player(board, player)

        print("Final Score %i." % ref.score2(board), end=" ")
        print("%s wins" % ("Black" if ref.score2(board) > 0 else "White"))


#################################################
# ParallelPlayer simulated tournament play
# With parallel processes and time limits
# this may not work on Windows, because, Windows is lame
# This calls Strategy.best_strategy(board, player, best_shared, running)
##################################################
class ParallelPlayer():
    def __init__(self, time_limit=5):
        self.black = Strategy()
        self.white = Strategy()
        self.time_limit = time_limit

    def play(self):
        ref = Strategy()
        print("play")
        board = ref.get_starting_board()
        player = BLACK

        print("Playing Parallel Game")
        strategy = lambda who: self.black.best_strategy if who == BLACK else self.white.best_strategy
        while player is not None:
            best_shared = Value("i", -99)
            best_shared.value = -99
            running = Value("i", 1)

            p = Process(target=strategy(player), args=(board, player, best_shared, running))
            # start the subprocess
            t1 = time.time()
            p.start()
            # run the subprocess for time_limit
            p.join(self.time_limit)
            # warn that we're about to stop and wait
            running.value = 0
            time.sleep(0.01)
            # kill the process
            p.terminate()
            time.sleep(0.01)
            # really REALLY kill the process
            if p.is_alive(): os.kill(p.pid, signal.SIGKILL)
            # see the best move it found
            move = best_shared.value
            if not silent: print("move = %i , time = %4.2f" % (move, time.time() - t1))
            if not silent: print(board, ref.get_valid_moves(board, player))
            # make the move
            board = ref.make_move(board, player, move)
            if not silent: print(ref.get_pretty_board(board))
            player = ref.next_player(board, player)

        print("Final Score %i." % ref.score2(board), end=" ")
        print("%s wins" % ("Black" if ref.score2(board) > 0 else "White"))


if __name__ == "__main__":
    #game = ParallelPlayer(1)
    game = StandardPlayer()
    game.play()
