import chess
import numpy as np
from quantum_backend import select_best_quantum_move

class QuantumChessEngine:
    def __init__(self):
        pass  # threshold no longer needed here

    def select_quantum_move(self, board):
        return select_best_quantum_move(board, depth=2)

        
    # def select_quantum_move(self, board):
    #     legal_moves = list(board.legal_moves)
    #     # print("Legal moves:", legal_moves)
    #     if not legal_moves:
    #         return None # no legal moves, avoid running Grover
    #     return run_grover_search(board, legal_moves)
    

    # def __init__(self, threshold=0.6):
    #     self.threshold = threshold
    #     return

    # def evaluate_move(board, move):
    #     board.push(move)
    #     score = material_count(board) + mobility_score(board)
    #     board.pop()
    #     return score
    
    # def evaluate(self, board, move):
    #     return np.random.rand()  # placeholder for fast classical eval

    # def select_quantum_move(self, board):
    #     legal_moves = list(board.legal_moves)
    #     evaluations = [self.evaluate(board, m) for m in legal_moves]
    #     marked_indices = [i for i, score in enumerate(evaluations) if score >= self.threshold]

    #     if not marked_indices:
    #         return legal_moves[np.argmax(evaluations)]  # fallback

    #     return run_grover_search(legal_moves, marked_indices)