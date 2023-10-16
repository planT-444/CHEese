starting_position = [
    ['r','n','b','q','k','b','n','r'],
    ['p','p','p','p','p','p','p','p'],
    ['_','_','_','_','_','_','_','_'],
    ['_','_','_','_','_','_','_','_'],
    ['_','_','_','_','_','_','_','_'],
    ['_','_','_','_','_','_','_','_'],
    ['P','P','P','P','P','P','P','P'],
    ['R','N','B','Q','K','B','N','R'],
]

test_position_str = [
    "________",
    "________",
    "________",
    "_____q__",
    "________",
    "________",
    "________",
    "____K___",
]
test_position = [list(row) for row in test_position_str]

class Board:
    def __init__(self):
        self.grid = [['0'] * 8 for i in range(8)]
        self.castle = {'w': True, 'b': False}
        for i in range(8):
            for j in range(8):
                cur_id = starting_position[i][j]
                # cur_id = test_position[i][j]
                self.grid[i][j] = Piece.create_piece(cur_id, i, j, self)
    
    @staticmethod
    def coords(row, col):
        rank = str(8 - row)
        file = "abcdefgh"[col]
        return file + rank

    def copy(self):
        new_grid = [[p.copy() for p in row] for row in self.grid]
        new_board = Board()
        new_board.grid = new_grid
        return new_board
    
    def __str__(self):
        output = ""
        for r in range(8):
            output += str(8-r) + " "
            output += " ".join([p.id for p in self.grid[r]]) + '\n'
        output += "  a b c d e f g h"
        return output




class Piece:
    def __init__(self, id, color, row, col, board):
        self.id = id
        self.color = color
        self.row = row
        self.col = col
        self.board = board

    @staticmethod
    def is_inbounds(row, col):
        return (0 <= row < 8 and 0 <= col < 8)

    def copy(self):
        return Piece.create_piece(self.id, self.row, self.color, self.board)

    @staticmethod
    def create_piece(id, row, col, board):
        color = 'w' if id.isupper() else 'b'
        if id == '_':
            color = None
        piece_type = id_to_type[id.lower()]
        return piece_type(id, color, row, col, board)

class King(Piece):
    def is_incheck(self):
        board_grid = self.board.grid
        is_same_color = lambda piece: piece.id != '_' and piece.color == self.color
        search_moves = {
            "qrk": ((1,0),(-1,0),(0,1),(0,-1)),
            "qbk": ((1,1),(1,-1),(-1,1),(-1,-1)),
            "n": ((2,1),(2,-1),(-2,1),(-2,-1),(1,2),(1,-2),(-1,2),(-1,-2)),
            "p": ((1,1),(1,-1),(-1,1),(-1,-1))
        }

        # looping through different types of searches
        for stranger_danger in search_moves:
            # determine which ids to look for
            look_out = stranger_danger
            if self.color == 'b':
                    look_out = look_out.upper()
            
            if stranger_danger in ('qrk', 'qbk', 'n'):
                # loop to search in different directions
                for row_move, col_move in search_moves[stranger_danger]:
                    cur_row, cur_col = self.row + row_move, self.col + col_move
                
                    while True:
                        if not Piece.is_inbounds(cur_row, cur_col):
                            break
                        cur_square = board_grid[cur_row][cur_col]
                        if is_same_color(cur_square):
                            break
                        if cur_square.id in look_out:
                            return True
                        if stranger_danger == 'n':
                            break
                        cur_row += row_move
                        cur_col += col_move
            elif stranger_danger == 'p':
                # direction of search depends on color
                if self.color == 'w':
                    pawn_moves = search_moves[stranger_danger][2:]
                else:
                    pawn_moves = search_moves[stranger_danger][:2]
                for row_move, col_move in pawn_moves:
                    cur_square = board_grid[self.row + row_move][self.col + col_move]
                    if cur_square.id == look_out:
                        return True
        return False
    

    def generate_moves(self):
        king_moves = ((1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1))
        new_board = self.board.copy()
        
        # replace with empty square
        new_board.grid[self.row][self.col] = Piece.create_piece('_', self.row, self.col, new_board)

        # check surrounding squares
        for row_move, col_move in king_moves:
            new_row = self.row + row_move
            new_col = self.col + col_move
            if not (0 <= new_row < 8 and 0 <= new_col < 8):
                continue

            print(f"checking if {self.id} ({Board.coords(self.row, self.col)}) can move to {Board.coords(new_row, new_col)}")

            new_king = Piece.create_piece(self.id, new_row, new_col, new_board)
            # not necessary to add new_king to new_board
            # is_incheck() works fine, saves having to remove it after
            if not new_king.is_incheck():
                print(f"legal move to {Board.coords(new_row, new_col)}")
                # move is legal, add to moves
        
        # castling
        if not self.is_incheck() and self.board.castle[self.color]:
            print("CHECKING CASTLING")
            sides = {
                'kingside': {'range': range(5,7), 'can_castle': True},
                'queenside': {'range': range(2,4), 'can_castle': True}
            }
            for side in sides:
                properties = sides[side]
                for col in properties['range']:
                    new_king = Piece.create_piece(self.id, self.row, col, new_board)
                    if new_board.grid[self.row][col].id != '_' or new_king.is_incheck():
                        properties['can_castle'] = False
                        if new_king.is_incheck():
                            print(f"IN CHECK AT {Board.coords(self.row, col)}")
                        break
                if properties['can_castle']:
                    print(f"{side} castling is legal")
                    
                    # castling is legal, add to moves

        
# class Move():
#     def __init__(self, )

class Queen(Piece):
    pass

class Rook(Piece):
    pass

class Bishop(Piece):
    pass

class Knight(Piece):
    pass

class Pawn(Piece):
    pass

class EmptySquare(Piece):
    pass

id_to_type = {
    'k': King,
    'q': Queen,
    'r': Rook,
    'b': Bishop,
    'n': Knight,
    'p': Pawn,
    '_': EmptySquare
}





