from components import Board
game_board = Board()
print(game_board)
print(game_board.grid[0][0].__dict__)
print()
game_board.grid[7][4].generate_moves()
