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
        self.castle = {'w': True, 'b': True}
        for i in range(8):
            for j in range(8):
                cur_id = test_position[i][j]
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
        new_board.castle = self.castle.copy()
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

class Move:
    def __init__(self, board, piece, piece_update:tuple[int, int, int, int], special = None):
        self.board = board
        self.piece = piece
        self.piece_update = piece_update
        # choices for special: enpassant, castle, promotion (format =[id])
        self.special = special
        

    # returns boolean, modified board object, move id
    def mega_move_func(self):
        if self.piece.id.lower() in 'rk':
            self.board.castle[self.piece.color] = False
        
        board_grid = self.board.grid
        board_grid_copy = board_grid.copy()
        old_row, old_col, new_row, new_col = self.piece_update

        # easy way out, changing the self.piece to the promoted one
        if self.special is not None and self.special[0] == '=':
            self.piece = Piece.create_piece(self.special[1:], new_row, new_col, self.board)

        board_grid[new_row][new_col] = self.piece
        self.piece.row = new_row
        self.piece.col = new_col


        if self.special is not None:
            if self.special == 'enpassant':
                captured_row = new_row + (1 if self.piece.color == 'w' else -1)
                board_grid[captured_row][new_col] = Piece.create_piece('_', captured_row, new_col, self.board)
                move_id = f'{Board.coords(0, old_col)[1]}x{Board.coords(new_row, new_col)} e.p.'

            elif self.special == 'castle':
                # queenside else kingside
                old_rook_col, new_rook_col, move_id = (0, 3, 'O-O-O') if new_col == 2 else (7, 5, 'O-O') 
                board_grid[new_row][old_rook_col] = Piece.create_piece('_', new_row, old_rook_col, self.board)
                new_rook_id = 'R' if self.piece.color == 'w' else 'r'
                board_grid[new_row][new_rook_col] = Piece.create_piece(new_rook_id, new_row, new_rook_col, self.board)
            else: # promotion
                move_id = f'{Board.coords(new_row, new_col)}={self.piece.id.upper()}'
            
            return True, self.board, move_id


        king = None
        for row in range(8):
            for col in range(8):
                cur_piece = board_grid[row][col]
                if cur_piece.id.lower() == 'k' and cur_piece.color == self.piece.color:
                    king = cur_piece
                    break
            if king is not None:
                break
        if king.is_incheck():
            return False, None, None


        old_coords = Board.coords(old_row, old_col)
        new_coords = Board.coords(new_row, new_col)
        capture = '' if board_grid_copy[new_row][new_col].id == '_' else 'x'
        match self.piece.id.lower():
            case 'p':
                move_id = new_coords if capture == '' else f'{old_coords[1]}x{new_coords}'
            case 'k':
                move_id = f'K{capture}{new_coords}'
            case _:
                search_moves = {
                    "rq": ((1,0),(-1,0),(0,1),(0,-1)),
                    "bq": ((1,1),(1,-1),(-1,1),(-1,-1)),
                    "n": ((2,1),(2,-1),(-2,1),(-2,-1),(1,2),(1,-2),(-1,2),(-1,-2)),
                }
                board_grid_copy[old_row][old_col] = self.piece
                look_alike_rows = []
                look_alike_cols = []
                for piece_ids in search_moves:
                    if self.piece.id.lower() not in piece_ids:
                        continue
                    cur_row, cur_col = new_row, new_col
                    for row_move, col_move in search_moves[piece_ids]:
                        while True:
                            if not Piece.is_inbounds:
                                break
                            cur_square = board_grid_copy[cur_row][cur_col]
                            if cur_square.id == self.piece.id and (cur_row, cur_col) != (old_row, old_col):
                                look_alike_rows.append(cur_row)
                                look_alike_cols.append(cur_col)
                                break
                            if cur_square.id != '_':
                                break
                
                row_match = old_row in look_alike_rows
                col_match = old_col in look_alike_cols

                move_id = self.piece.upper()
                if row_match and col_match:
                    move_id += old_coords
                elif col_match:
                    move_id += old_coords[1]
                elif row_match:
                    move_id += old_coords[0]
                
                move_id += capture + new_coords
                


                
        return True, self.board, move_id







class King(Piece):
    def is_incheck(self):
        board_grid = self.board.grid
        is_same_color = lambda piece: piece.id != '_' and piece.color == self.color
        search_moves = {
            "qr": ((1,0),(-1,0),(0,1),(0,-1)),
            "qb": ((1,1),(1,-1),(-1,1),(-1,-1)),
            "n": ((2,1),(2,-1),(-2,1),(-2,-1),(1,2),(1,-2),(-1,2),(-1,-2)),
            "p": ((1,1),(1,-1),(-1,1),(-1,-1))
        }

        # looping through different types of searches
        for stranger_danger in search_moves:
            # determine which ids to look for
            look_out = stranger_danger
            if self.color == 'b':
                    look_out = look_out.upper()
            
            if stranger_danger in ('qr', 'qb', 'n'):
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





