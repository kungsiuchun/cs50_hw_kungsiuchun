"""
Tic Tac Toe Player
"""

import math
import copy

X = "X"
O = "O"
EMPTY = None

def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """ 
    x_turn = 0
    o_turn = 0
    for i in board:
        for j in i:
            if j == X:
                x_turn += 1
            elif j == O:
                o_turn += 1
    if o_turn == x_turn:
        return X
    return O
                


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    free_spot = []
    for i in range(3):
        for j in range(3):
            if board[i][j] == EMPTY:
                action = (i, j)
                free_spot.append(action)
    return free_spot


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    currentPlayer = player(board)
    if action is None:
        raise "Empty action"
    resultBoard = copy.deepcopy(board)
    resultBoard[action[0]][action[1]] = currentPlayer
    return resultBoard

def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    #check horizontal and vertical
    for i in range(3):
        if board[i][0] == board[i][1]==board[i][2] and board[i][0] is not EMPTY:
            return board[i][0]
        elif board[0][i] == board[1][i]==board[2][i] and board[0][i] is not EMPTY:
            return board[0][i]
    #check diagonal
    if board[0][0] == board[1][1]==board[2][2] and board[0][0] is not EMPTY:
        return board[0][0]
    if board[0][2] == board[1][1]==board[2][0] and board[0][2] is not EMPTY:
        return board[0][2]
#     else:
    return None

def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if not actions(board):
        return True
    winner_var = utility(board)
    if winner_var == 1:
        return True
    elif winner_var == -1:
        return True
    else:
        return None      

def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    if winner(board) == None:
        return 0
    elif winner(board) == X:
        return 1
    else:
        return -1

def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if terminal(board):
        return None
    
    if player(board) == "X":
        print()
        # X is 1
        best = -math.inf
        best_move = None
        for action in actions(board):
           val = min_val(result(board, action))
           print("value:" + str(val) + "  Action"+ str(action))
           if val > best: # best = -2
               best = val
               best_move = action
        print("Best Move for X:" + str(best_move))
        return best_move
    else:
        # O is -1
        best = math.inf
        best_move = None
        for action in actions(board):
            val = max_val(result(board, action))
            print("value:" + str(val) + "  Action"+ str(action))
            if val < best:
                best = val
                best_move = action
        print("Best Move for O")
        print(best_move)
        return best_move


def max_val(board):
    if terminal(board):
        return utility(board)
    maxVal = -math.inf
    for action in actions(board):
        # find the max base on the opponent 
        maxList = min_val(result(board, action))
        maxVal = max(maxVal, maxList)
    return maxVal

def min_val(board):
    if terminal(board):
        return utility(board)
    minVal = math.inf
    for action in actions(board):
        #find the min base on the opponent
        maxList = max_val(result(board, action))
        minVal = min(minVal, maxList)
    return minVal

