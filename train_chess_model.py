import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models
import pandas as pd

def build_model(num_moves):
    """Build a neural network for chess move prediction."""
    model = models.Sequential([
        layers.Input(shape=(12, 8, 8)),
        layers.Flatten(),
        layers.Dense(1024, activation='relu'),
        layers.Dropout(0.3),
        layers.Dense(512, activation='relu'),
        layers.Dropout(0.3),
        layers.Dense(num_moves, activation='softmax')
    ])
    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
    return model

# Load data
X_train = np.load("data/X_train.npy")
y_train = np.load("data/y_train.npy")
X_test = np.load("data/X_test.npy")
y_test = np.load("data/y_test.npy")
move_to_idx = pd.read_json("data/move_to_idx.json", typ='series')

# Build and train model
model = build_model(len(move_to_idx))
model.summary()

model.fit(
    X_train, y_train,
    validation_data=(X_test, y_test),
    epochs=10,
    batch_size=32,
    verbose=1
)

# Save model
model.save("data/chess_model.h5")

# Save move mapping for inference
idx_to_move = {v: k for k, v in move_to_idx.items()}
pd.Series(idx_to_move).to_json("data/idx_to_move.json")
print("Model training complete and saved as data/chess_model.h5")