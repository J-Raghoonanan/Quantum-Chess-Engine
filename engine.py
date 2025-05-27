import chess
import numpy as np
from quantum_backend import run_grover_search

class QuantumChessEngine:
    def __init__(self, threshold=0.6):
        self.threshold = threshold

    def evaluate(self, board, move):
        return np.random.rand()  # placeholder for fast classical eval

    def select_quantum_move(self, board):
        legal_moves = list(board.legal_moves)
        evaluations = [self.evaluate(board, m) for m in legal_moves]
        marked_indices = [i for i, score in enumerate(evaluations) if score >= self.threshold]

        if not marked_indices:
            return legal_moves[np.argmax(evaluations)]  # fallback

        return run_grover_search(legal_moves, marked_indices)