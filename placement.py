def can_place_shape(board, shape, board_row, board_col):
    shape_rows, shape_cols = len(shape), len(shape[0])
    for i in range(shape_rows):
        for j in range(shape_cols):
            if shape[i][j] == 1:
                r = board_row + i
                c = board_col + j
                if r < 0 or c < 0 or r >= len(board) or c >= len(board[0]) or board[r][c] == 1:
                    return False
    return True

def place_shape_on_board(board, shape, row_offset, col_offset):
    new_board = [row[:] for row in board]
    for i in range(len(shape)):
        for j in range(len(shape[0])):
            if shape[i][j] == 1:
                new_board[row_offset + i][col_offset + j] = 1
    return new_board

# --- Count full rows and columns ---
def count_full_lines(board):
    full_rows = sum(all(cell == 1 for cell in row) for row in board)
    full_cols = sum(all(board[r][c] == 1 for r in range(len(board))) for c in range(len(board[0])))
    return full_rows + full_cols

# --- Clear full rows and columns (Block Blast style) ---
def clear_full_lines(board):
    # Clear full rows
    new_board = [row for row in board if not all(cell == 1 for cell in row)]
    while len(new_board) < len(board):
        new_board.insert(0, [0] * len(board[0]))

    # Clear full columns
    transposed = list(zip(*new_board))
    new_transposed = [col for col in transposed if not all(cell == 1 for cell in col)]
    while len(new_transposed) < len(board[0]):
        new_transposed.insert(0, tuple(0 for _ in range(len(new_board))))

    cleared = [list(row) for row in zip(*new_transposed)]
    return cleared

# --- Find best placement for maximum clear ---
def find_best_placement(board, shape):
    best_score = -1
    best_position = None
    board_rows, board_cols = len(board), len(board[0])
    shape_rows, shape_cols = len(shape), len(shape[0])

    for i in range(board_rows - shape_rows + 1):
        for j in range(board_cols - shape_cols + 1):
            if can_place_shape(board, shape, i, j):
                simulated = place_shape_on_board(board, shape, i, j)
                score = count_full_lines(simulated)
                if score > best_score:
                    best_score = score
                    best_position = (i, j)
    return best_position, best_score

# --- Smart shape placement ---
def smart_place_best_shape(board, shapes, verbose=True):
    best_score = -1
    best_pos = None
    best_shape_idx = -1
    best_shape_loc = None

    for idx, (shape, shape_loc) in enumerate(shapes):
        pos, score = find_best_placement(board, shape)
        if pos and score > best_score:
            best_score = score
            best_pos = pos
            best_shape_idx = idx
            best_shape_loc = shape_loc

    if best_pos is not None:
        if verbose:
            print(f"✅ Placing shape[{best_shape_idx}] at {best_pos} with score {best_score}")
        board = place_shape_on_board(board, shapes[best_shape_idx][0], *best_pos)
        board = clear_full_lines(board)
        return board, best_shape_idx, best_shape_loc, best_pos
    else:
        if verbose:
            print("🚫 No valid placement for any shape")
        return board, None, None, None