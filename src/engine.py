import chess
import numpy as np
from quantum_backend import select_best_quantum_move

class QuantumChessEngine:
    def __init__(self):
        pass  # threshold no longer needed here

    def select_quantum_move(self, board):
        return select_best_quantum_move(board, depth=2)