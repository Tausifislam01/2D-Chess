import chess
import numpy as np
import tensorflow as tf
import pandas as pd
import random

def board_to_tensor(board):
    """Convert a chess board to a 12x8x8 tensor."""
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

# Load model and move mapping
model = tf.keras.models.load_model("data/chess_model.h5")
idx_to_move = pd.read_json("data/idx_to_move.json", typ='series')

# Test the AI
board = chess.Board()
print("Initial board:")
print(board)

# Get legal moves
legal_moves = list(board.legal_moves)
legal_move_ucis = [move.uci() for move in legal_moves]

# Predict move
board_tensor = board_to_tensor(board)[np.newaxis, ...]  # Add batch dimension
predictions = model.predict(board_tensor)[0]
predicted_idx = np.argmax(predictions)

# Check if predicted move is legal
predicted_move = idx_to_move.get(str(predicted_idx), None)
if predicted_move in legal_move_ucis:
    move = chess.Move.from_uci(predicted_move)
else:
    # Fallback to random legal move if prediction is invalid
    move = random.choice(legal_moves)

print(f"AI predicted move: {move.uci()}")
board.push(move)
print("Board after AI move:")
print(board)