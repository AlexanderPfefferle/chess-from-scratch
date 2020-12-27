WHITE_PAWN=1
WHITE_KNIGHT=2
WHITE_BISHOP=3
WHITE_ROOK=4
WHITE_QUEEN=5
WHITE_KING=6
BLACK_PAWN=7
BLACK_KNIGHT=8
BLACK_BISHOP=9
BLACK_ROOK=10
BLACK_QUEEN=11
BLACK_KING=12

KNIGHT_MOVES = [[-2, -1], [+2, -1], [-2, +1], [+2, +1], [-1, -2], [+1, -2], [-1, +2], [+1, +2]]
KING_MOVES = [[-1, -1], [0, -1], [+1, -1], [-1, 0], [+1, 0], [-1, +1], [0, +1], [+1, +1]]
BISHOP_DIRECTIONS = [[-1, -1], [-1, +1], [+1, -1], [+1, +1]]

eval_table = {}

def copy_board(old_board):
    return [[old_board[x][y] for y in range(8)] for x in range(8)]

class GameState:

    def __init__(self):
        self.board =   [[4, 1, 0, 0, 0, 0, 7, 10],
                        [2, 1, 0, 0, 0, 0, 7, 8],
                        [3, 1, 0, 0, 0, 0, 7, 9],
                        [5, 1, 0, 0, 0, 0, 7, 11],
                        [6, 1, 0, 0, 0, 0, 7, 12],
                        [3, 1, 0, 0, 0, 0, 7, 9],
                        [2, 1, 0, 0, 0, 0, 7, 8],
                        [4, 1, 0, 0, 0, 0, 7, 10]]

        self.unicode_pieces = ' ♙♘♗♖♕♔♟♞♝♜♛♚'
        self.pieces = ' PNBRQKpnbrqk'
        self.is_whites_turn         = True
        self.white_castle_kingside  = True
        self.white_castle_queenside = True
        self.black_castle_kingside  = True
        self.black_castle_queenside = True
        self.en_passant_oppertunity = '-'
        self.halfmove_clock         = 0
        self.fullmove_num           = 1
        self.past_states = dict()
        self.past_states[' '.join(self.to_fen().split()[:4])]=1

            
    def pretty_print(self, unicode=False):
        print(' '+'-'*8+' ')
        for x in range(0, 8)[::-1]:
            row='|'
            for y in range(0, 8):
                if unicode:
                    row += self.unicode_pieces[self.board[y][x]]
                else:
                    row += self.pieces[self.board[y][x]]
            row+='|'
            print(row.replace(' ', '.'))
        print(' '+'-'*8+' ')

    def to_fen(self):
        fen=""
        empty_counter=0
        for y in reversed(range(8)):
            for x in range(8):
                if not self.is_empty(x, y):
                    fen+='' if empty_counter == 0 else str(empty_counter)
                    fen+=self.pieces[self.board[x][y]]
                    empty_counter=0
                else:
                    empty_counter+=1
            fen+='' if empty_counter == 0 else str(empty_counter)
            fen+='/'
            empty_counter=0
        fen = fen[0:-1]
        fen += ' '
        fen += 'w' if self.is_whites_turn else 'b'
        fen += ' '
        fen += 'K'*self.white_castle_kingside
        fen += 'Q'*self.white_castle_queenside
        fen += 'k'*self.black_castle_kingside
        fen += 'q'*self.black_castle_queenside
        fen += '-'*(not any([self.white_castle_kingside, self.white_castle_queenside, self.black_castle_kingside, self.black_castle_queenside]))
        fen += ' '
        fen += self.en_passant_oppertunity
        fen += ' '
        fen += str(self.halfmove_clock)
        fen += ' '
        fen += str(self.fullmove_num)
        return fen
    
    def set_fen(self, fen):
        groups=fen.split(' ')
        for c in groups[0]:
            for i in range(1, 9):
                if c.isdigit():
                    if int(c)==i:
                        groups[0]=groups[0].replace(c, ' '*i)
        groups[0]=groups[0].replace('/', '')
        for y in reversed(range(8)):
            for x in range(8):
                self.board[x][y]=self.pieces.index(groups[0][(7-y)*8+x])
        self.is_whites_turn = True if groups[1] == 'w' else False
        self.white_castle_kingside  = 'K' in groups[2]
        self.white_castle_queenside = 'Q' in groups[2]
        self.black_castle_kingside  = 'k' in groups[2]
        self.black_castle_queenside = 'q' in groups[2]
        self.en_passant_oppertunity = groups[3]
        self.halfmove_clock = int(groups[4])
        self.fullmove_num = int(groups[5])
    
    def index_to_name(self, x, y):
        return chr(x+97)+str(y+1)
        
    def is_white_piece(self, x, y):
        return self.board[x][y] <= 6 and self.board[x][y] != 0
    
    def is_black_piece(self, x, y):
        return self.board[x][y] >= 7
        
    def is_empty(self, x, y):
        return self.board[x][y] == 0
    
    def is_on_board(self, x, y):
        return ((x >= 0 and x <= 7) and (y >= 0 and y <= 7))
        
    def is_in_check(self):
        next_state=GameState()
        next_state.white_castle_kingside=self.white_castle_kingside
        next_state.white_castle_queenside=self.white_castle_queenside
        next_state.black_castle_kingside=self.black_castle_kingside
        next_state.black_castle_queenside=self.black_castle_queenside
        next_state.board=copy_board(self.board)
        next_state.is_whites_turn=not self.is_whites_turn
        for next_move in next_state.next_moves():
            dst_col = ord(next_move[2])-97
            dst_row = int(next_move[3])-1
            if self.board[dst_col][dst_row] == (WHITE_KING if self.is_whites_turn else BLACK_KING):
                return True
        return False

    def execute_move(self, move):
        if self.is_whites_turn:
            self.fullmove_num += 1
        self.halfmove_clock += 1
        self.en_passant_oppertunity = '-'
        src_col = ord(move[0])-96-1
        src_row = int(move[1])-1
        dst_col = ord(move[2])-96-1
        dst_row = int(move[3])-1
        if self.board[dst_col][dst_row] != 0:
            self.halfmove_clock = 0
        self.board[dst_col][dst_row] = self.board[src_col][src_row]
        self.board[src_col][src_row] = 0
        moved_piece=self.board[dst_col][dst_row]
        if moved_piece == WHITE_PAWN:
            self.halfmove_clock = 0
            if move[0:2] == self.en_passant_oppertunity:
                self.board[dst_col][3] = '0'
            if src_row == 1 and dst_row == 3:
                self.en_passant_oppertunity = self.index_to_name(src_col, 2)
            if dst_row == 7:
                if move[4] == 'q':
                    self.board[dst_col][dst_row] = WHITE_QUEEN
                if move[4] == 'r':
                    self.board[dst_col][dst_row] = WHITE_ROOK
                if move[4] == 'b':
                    self.board[dst_col][dst_row] = WHITE_BISHOP
                if move[4] == 'n':
                    self.board[dst_col][dst_row] = WHITE_KNIGHT
        if moved_piece == BLACK_PAWN:
            self.halfmove_clock = 0
            if move[0:2] == self.en_passant_oppertunity:
                self.board[dst_col][4] = '0'
            if src_row == 6 and dst_row == 4:
                self.en_passant_oppertunity = self.index_to_name(src_col, 5)
            if dst_row == 0:
                if move[4] == 'q':
                    self.board[dst_col][dst_row] = BLACK_QUEEN
                if move[4] == 'r':
                    self.board[dst_col][dst_row] = BLACK_ROOK
                if move[4] == 'b':
                    self.board[dst_col][dst_row] = BLACK_BISHOP
                if move[4] == 'n':
                    self.board[dst_col][dst_row] = BLACK_KNIGHT
        if moved_piece == WHITE_KING:
            if move == "e1g1" and self.white_castle_kingside:
                self.execute_move("h1f1")
            if move == "e1c1" and self.white_castle_queenside:
                self.execute_move("a1d1")
            self.white_castle_kingside  = False
            self.white_castle_queenside = False
        if moved_piece == BLACK_KING:
            if move == "e8g8" and self.black_castle_kingside:
                self.execute_move("h8f8")
            if move == "e8c8" and self.black_castle_queenside:
                self.execute_move("a8d8")
            self.black_castle_kingside  = False
            self.black_castle_queenside = False
        if moved_piece == WHITE_ROOK:
            if move[0:2] == "h1":
                self.white_castle_kingside = False
            if move[0:2] == "a1":
                self.white_castle_queenside = False
        if moved_piece == BLACK_ROOK:
            if move[0:2] == "h8":
                self.black_castle_kingside = False
            if move[0:2] == "a8":
                self.black_castle_queenside = False
        current_state = ' '.join(self.to_fen().split()[:4])
        self.past_states[current_state] = self.past_states.get(current_state,0) +1
        

    def next_moves(self):
        moves=[]
        for x in range(0,8):
            for y in range(0,8):
                if self.is_black_piece(x, y) and self.is_whites_turn:
                    continue
                if self.is_white_piece(x, y) and not self.is_whites_turn:
                    continue
                piece=self.board[x][y]
                if piece == WHITE_PAWN:
                    if y == 1:
                        if self.board[x][y+2] == 0:
                            moves.append(self.index_to_name(x, y)+self.index_to_name(x, y+2))
                    if self.board[x][y+1] == 0:
                        if y+1 != 7:
                            moves.append(self.index_to_name(x, y)+self.index_to_name(x, y+1))
                        else:
                            for c in "qrbn":
                                moves.append(self.index_to_name(x, y)+self.index_to_name(x, y+1)+c)
                    if x < 7:
                        if self.is_black_piece(x+1, y+1):
                            if y+1 != 7:
                                moves.append(self.index_to_name(x, y)+self.index_to_name(x+1, y+1))
                            else:
                                for c in "qrbn":
                                    moves.append(self.index_to_name(x, y)+self.index_to_name(x+1, y+1)+c)
                        elif self.index_to_name(x+1, y+1) == self.en_passant_oppertunity:
                            moves.append(self.index_to_name(x, y)+self.index_to_name(x+1, y+1))
                    if x > 0:
                        if self.is_black_piece(x-1, y+1):
                            if y+1 != 7:
                                moves.append(self.index_to_name(x, y)+self.index_to_name(x-1, y+1))
                            else:
                                for c in "qrbn":
                                    moves.append(self.index_to_name(x, y)+self.index_to_name(x-1, y+1)+c)
                        elif self.index_to_name(x-1, y+1) == self.en_passant_oppertunity:
                            moves.append(self.index_to_name(x, y)+self.index_to_name(x-1, y+1))
                if piece == BLACK_PAWN:
                    if y == 6:
                        if self.board[x][y-2] == 0:
                            moves.append(self.index_to_name(x, y)+self.index_to_name(x, y-2))
                    if self.board[x][y-1] == 0:
                        if y-1 != 0:
                            moves.append(self.index_to_name(x, y)+self.index_to_name(x, y-1))
                        else:
                            for c in "qrbn":
                                moves.append(self.index_to_name(x, y)+self.index_to_name(x, y-1)+c)
                    if x < 7:
                        if self.is_white_piece(x+1, y-1):
                            if y-1 != 0:
                                moves.append(self.index_to_name(x, y)+self.index_to_name(x+1, y-1))
                            else:
                                for c in "qrbn":
                                    moves.append(self.index_to_name(x, y)+self.index_to_name(x+1, y-1)+c)
                        elif self.index_to_name(x+1, y-1) == self.en_passant_oppertunity:
                            moves.append(self.index_to_name(x, y)+self.index_to_name(x+1, y-1))
                    if x > 0:
                        if self.is_white_piece(x-1, y-1):
                            if y-1 != 0:
                                moves.append(self.index_to_name(x, y)+self.index_to_name(x-1, y-1))
                            else:
                                for c in "qrbn":
                                    moves.append(self.index_to_name(x, y)+self.index_to_name(x-1, y-1)+c)
                        elif self.index_to_name(x-1, y-1) == self.en_passant_oppertunity:
                            moves.append(self.index_to_name(x, y)+self.index_to_name(x-1, y-1))
                if piece == WHITE_KNIGHT:
                    for dx, dy in KNIGHT_MOVES:
                        if self.is_on_board(x+dx, y+dy):
                            if not self.is_white_piece(x+dx, y+dy):
                                moves.append(self.index_to_name(x, y)+self.index_to_name(x+dx, y+dy))
                if piece == BLACK_KNIGHT:
                    for dx, dy in KNIGHT_MOVES:
                        if self.is_on_board(x+dx, y+dy):
                            if not self.is_black_piece(x+dx, y+dy):
                                moves.append(self.index_to_name(x, y)+self.index_to_name(x+dx, y+dy))
                if piece == WHITE_KING:
                    for dx, dy in KING_MOVES:
                        if self.is_on_board(x+dx, y+dy):
                            if not self.is_white_piece(x+dx, y+dy):
                                moves.append(self.index_to_name(x, y)+self.index_to_name(x+dx, y+dy))
                    if self.white_castle_kingside:
                        if self.is_empty(x+1, y) and self.is_empty(x+2, y):
                            if self.is_move_legal(self.index_to_name(x, y)+self.index_to_name(x+1, y)):
                                if self.is_move_legal(self.index_to_name(x, y)+self.index_to_name(x+2, y)):
                                    moves.append("e1g1")
                    if self.white_castle_queenside:
                        if self.is_empty(x-1, y) and self.is_empty(x-2, y):
                            if self.is_move_legal(self.index_to_name(x, y)+self.index_to_name(x-1, y)):
                                if self.is_move_legal(self.index_to_name(x, y)+self.index_to_name(x-2, y)):
                                    moves.append("e1c1")
                if piece == BLACK_KING:
                    for dx, dy in KING_MOVES:
                        if self.is_on_board(x+dx, y+dy):
                            if not self.is_black_piece(x+dx, y+dy):
                                moves.append(self.index_to_name(x, y)+self.index_to_name(x+dx, y+dy))
                    if self.black_castle_kingside:
                        if self.is_empty(x+1, y) and self.is_empty(x+2, y):
                            if self.is_move_legal(self.index_to_name(x, y)+self.index_to_name(x+1, y)):
                                if self.is_move_legal(self.index_to_name(x, y)+self.index_to_name(x+2, y)):
                                    moves.append("e8g8")
                    if self.black_castle_queenside:
                        if self.is_empty(x-1, y) and self.is_empty(x-2, y):
                            if self.is_move_legal(self.index_to_name(x, y)+self.index_to_name(x-1, y)):
                                if self.is_move_legal(self.index_to_name(x, y)+self.index_to_name(x-2, y)):
                                    moves.append("e8c8")
                if piece == WHITE_BISHOP or piece == WHITE_QUEEN:
                    for direction in BISHOP_DIRECTIONS:
                        dx=0
                        dy=0
                        while True:
                            dx=dx+direction[0]
                            dy=dy+direction[1]
                            if not self.is_on_board(x+dx, y+dy):
                                break;
                            if self.is_white_piece(x+dx, y+dy):
                                break;
                            moves.append(self.index_to_name(x, y)+self.index_to_name(x+dx, y+dy))
                            if self.is_black_piece(x+dx, y+dy):
                                break;
                if piece == BLACK_BISHOP or piece == BLACK_QUEEN:
                    for direction in BISHOP_DIRECTIONS:
                        dx=0
                        dy=0
                        while True:
                            dx=dx+direction[0]
                            dy=dy+direction[1]
                            if not self.is_on_board(x+dx, y+dy):
                                break;
                            if self.is_black_piece(x+dx, y+dy):
                                break;
                            moves.append(self.index_to_name(x, y)+self.index_to_name(x+dx, y+dy))
                            if self.is_white_piece(x+dx, y+dy):
                                break;
                if piece == WHITE_ROOK or piece == WHITE_QUEEN:
                    for direction in [[-1, 0], [+1, 0], [0, -1], [0, +1]]:
                        dx=0
                        dy=0
                        while True:
                            dx=dx+direction[0]
                            dy=dy+direction[1]
                            if not self.is_on_board(x+dx, y+dy):
                                break;
                            if self.is_white_piece(x+dx, y+dy):
                                break;
                            moves.append(self.index_to_name(x, y)+self.index_to_name(x+dx, y+dy))
                            if self.is_black_piece(x+dx, y+dy):
                                break;
                if piece == BLACK_ROOK or piece == BLACK_QUEEN:
                    for direction in [[-1, 0], [+1, 0], [0, -1], [0, +1]]:
                        dx=0
                        dy=0
                        while True:
                            dx=dx+direction[0]
                            dy=dy+direction[1]
                            if not self.is_on_board(x+dx, y+dy):
                                break;
                            if self.is_black_piece(x+dx, y+dy):
                                break;
                            moves.append(self.index_to_name(x, y)+self.index_to_name(x+dx, y+dy))
                            if self.is_white_piece(x+dx, y+dy):
                                break;
        return moves
    
    def is_move_legal(self, move):
        next_state=GameState()
        next_state.white_castle_kingside=self.white_castle_kingside
        next_state.white_castle_queenside=self.white_castle_queenside
        next_state.black_castle_kingside=self.black_castle_kingside
        next_state.black_castle_queenside=self.black_castle_queenside
        next_state.is_whites_turn=self.is_whites_turn
        next_state.board=copy_board(self.board)
        next_state.execute_move(move)
        return not next_state.is_in_check()
    
    def next_legal_moves(self):
        legal_moves=[]
        moves=self.next_moves()
        for move in moves:
            if self.is_move_legal(move):
                legal_moves.append(move)
        return legal_moves
        
    def is_checkmate(self):
        return len(self.next_legal_moves()) == 0 and self.is_in_check()

    def is_stalemate(self):
        return len(self.next_legal_moves()) == 0 and not self.is_in_check()
        
    def check_threefold_repetition(self):
        return max(self.past_states.values()) > 2
        
    def is_tie(self):
        return self.is_stalemate() or (self.halfmove_clock == 50) or self.check_threefold_repetition()
        
    def evaluate_position(self):
        fen = self.to_fen()
        if fen in eval_table:
            return eval_table[fen]
        value = 0
        for x in range(8):
            for y in range(8):
                piece=self.board[x][y]
                value += 1*(piece == WHITE_PAWN)
                value += 3*(piece == WHITE_KNIGHT)
                value += 3*(piece == WHITE_BISHOP)
                value += 5*(piece == WHITE_ROOK)
                value += 9*(piece == WHITE_QUEEN)
                value -= 1*(piece == BLACK_PAWN)
                value -= 3*(piece == BLACK_KNIGHT)
                value -= 3*(piece == BLACK_BISHOP)
                value -= 5*(piece == BLACK_ROOK)
                value -= 9*(piece == BLACK_QUEEN)
        if self.is_checkmate():
            value = -1000 if self.is_whites_turn else 1000
        if self.is_tie():
            value = 0
        eval_table[fen] = value
        return value
        
    def find_best_move(self, depth, alpha=float("-inf"), beta=float("inf")):
        best_move = ""
        best_move_value = float("-inf") if self.is_whites_turn else float("inf")
        next_state=GameState()
        next_state.white_castle_kingside=self.white_castle_kingside
        next_state.white_castle_queenside=self.white_castle_queenside
        next_state.black_castle_kingside=self.black_castle_kingside
        next_state.black_castle_queenside=self.black_castle_queenside
        next_state.is_whites_turn=not self.is_whites_turn
        next_state.past_states={key:value for key,value  in self.past_states.items()}
        for move in self.next_legal_moves():
            next_state.board=copy_board(self.board)
            next_state.execute_move(move)
            if depth == 1:
                next_evaluation = next_state.evaluate_position()
            else:
                _, next_evaluation = next_state.find_best_move(depth-1, alpha, beta)
            if self.is_whites_turn:
                if next_evaluation > best_move_value:
                    best_move_value = next_evaluation
                    best_move = move
                    alpha = max(alpha, best_move_value)
            else:
                if next_evaluation < best_move_value:
                    best_move_value = next_evaluation
                    best_move = move
                    beta = min(beta, best_move_value)
            if beta <= alpha:
                break
        return best_move, best_move_value
        
if __name__=='__main__':
    unicode_pieces=True
    testgame=GameState()
    while True:
        testgame.pretty_print(unicode_pieces)
        next_move = ""
        while next_move not in testgame.next_legal_moves():
            if testgame.is_whites_turn:
                next_move = input()
            else:
                next_move = testgame.find_best_move(1)[0]
                print(next_move)
        testgame.execute_move(next_move)
        testgame.is_whites_turn = not testgame.is_whites_turn
        if testgame.is_tie() or testgame.is_checkmate():
            testgame.pretty_print(unicode_pieces)
            break
    if testgame.is_tie():
        print("It's a tie!")
    else:
        print("Black" if testgame.is_whites_turn else "White", "won!")
