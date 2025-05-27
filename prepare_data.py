import chess
import chess.pgn
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

def board_to_tensor(board):
    """Convert a chess board to a 12x8x8 tensor (6 piece types x 2 colors)."""
    tensor = np.zeros((12, 8, 8), dtype=np.float32)
    piece_map = {
        chess.PAWN: 0, chess.KNIGHT: 1, chess.BISHOP: 2,
        chess.ROOK: 3, chess.QUEEN: 4, chess.KING: 5
    }
    
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            color_idx = 0 if piece.color == chess.WHITE else 6
            piece_idx = piece_map[piece.piece_type]
            rank = chess.square_rank(square)
            file = chess.square_file(square)
            tensor[color_idx + piece_idx, rank, file] = 1.0
    
    return tensor

def parse_pgn(pgn_file, max_games=1000):
    """Parse PGN file and extract board states and moves."""
    boards = []
    moves = []
    
    with open(pgn_file, 'r', encoding='utf-8') as pgn:
        for i in range(max_games):
            game = chess.pgn.read_game(pgn)
            if game is None:
                break
            board = game.board()
            for move in game.mainline_moves():
                boards.append(board_to_tensor(board))
                moves.append(move.uci())
                board.push(move)
    
    return np.array(boards), moves

def encode_moves(moves, max_moves=5000):
    """Encode UCI moves as integer labels."""
    unique_moves = list(set(moves))
    if len(unique_moves) > max_moves:
        unique_moves = unique_moves[:max_moves]
    move_to_idx = {move: idx for idx, move in enumerate(unique_moves)}
    labels = [move_to_idx.get(move, len(unique_moves)) for move in moves]
    return np.array(labels), move_to_idx

# Example usage
if __name__ == "__main__":
    pgn_file = r"E:\Project\Chess\lichess_elite_2023-08.pgn"
    X, y = parse_pgn(pgn_file, max_games=1000)
    y, move_to_idx = encode_moves(y)
    
    # Split into train and test sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Create data directory if it doesn't exist
    import os
    os.makedirs("data", exist_ok=True)
    
    # Save datasets
    np.save("data/X_train.npy", X_train)
    np.save("data/X_test.npy", X_test)
    np.save("data/y_train.npy", y_train)
    np.save("data/y_test.npy", y_test)
    
    # Save move mapping
    pd.Series(move_to_idx).to_json("data/move_to_idx.json")
    print(f"Processed {len(X)} board states with {len(move_to_idx)} unique moves.")