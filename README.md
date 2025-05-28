2D Chess Game with AI
A 2D chess game built with PyOpenGL and Pygame, featuring a machine learning-based AI opponent trained on the Lichess Elite Database.
Project Structure

prepare_data.py: Processes chess PGN files into ML-ready data (board states and moves).
train_chess_model.py: Trains a neural network to predict chess moves.
test_chess_ai.py: Tests the AI model by predicting moves on a starting board.
chess_game.py: Renders a 2D chessboard using PyOpenGL and Pygame.
data/: Contains generated data (excluded via .gitignore).

Setup

Clone the repository:git clone https://github.com/Tausifislam01/2D-Chess.git
cd 2D-Chess


Create a virtual environment and install dependencies:python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt


Run the chessboard:python chess_game.py



Next Steps

Add chess piece rendering and user input for moves.
Integrate the AI model for gameplay.

Requirements
See requirements.txt for dependencies.
