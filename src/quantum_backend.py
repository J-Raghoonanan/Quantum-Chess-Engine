from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer 
import numpy as np
import chess
import math
from classical_evaluation import evaluate_position


# # Simple evaluation based on material balance and mobility
# PIECE_VALUES = {
#     "P": 1, "N": 3, "B": 3, "R": 5, "Q": 9, "K": 0
# }

def run_circuit(qc, shots=1024):
    qc.measure_all()
    backend = Aer.get_backend("aer_simulator")
    transpiled_qc = transpile(qc, backend)
    job = backend.run(transpiled_qc, shots=shots) # type: ignore
    return job.result().get_counts()


def quantum_minimax(board: chess.Board, depth: int) -> tuple[int, chess.Move]:
    '''
    Recursive depth-d search using Grover-style amplification for move selection.
    '''

    if depth == 0 or board.is_game_over():
        return evaluate_position(board), chess.Move.null()

    legal_moves = list(board.legal_moves)
    if len(legal_moves) == 0:
        return evaluate_position(board), chess.Move.null()

    move_scores = []
    for move in legal_moves:
        board.push(move)
        score, _ = quantum_minimax(board, depth - 1)
        board.pop()
        move_scores.append(score)

    if len(legal_moves) == 1:
        return move_scores[0], legal_moves[0]

    is_white = board.turn
    best_score = max(move_scores) if is_white else min(move_scores)

    # Adaptive thresholding
    # Choose moves that have values >= half a std. dev above the mean
    mu = np.mean(move_scores)
    sigma = np.std(move_scores)
    theta = mu + 0.5 * sigma if is_white else mu - 0.5 * sigma
    marked_indices = [i for i, s in enumerate(move_scores)
                      if (s >= theta if is_white else s <= theta)]

    if len(marked_indices) == 0:
        best_index = np.argmax(move_scores) if is_white else np.argmin(move_scores)
        return move_scores[best_index], legal_moves[best_index]

    N = 2 ** int(np.ceil(np.log2(len(legal_moves))))
    n = int(np.log2(N))
    R = max(1, int(math.ceil(np.pi / 4 * np.sqrt(N / len(marked_indices)))))

    qc = QuantumCircuit(n)
    qc.h(range(n))

    for _ in range(R):
        # Oracle
        for idx in marked_indices:
            bits = format(idx, f"0{n}b")
            for i, bit in enumerate(reversed(bits)):
                if bit == "0": qc.x(i)
            if n > 1:
                qc.h(n - 1)
                qc.mcx(list(range(n - 1)), n - 1)
                qc.h(n - 1)
            else:
                qc.z(0)
            for i, bit in enumerate(reversed(bits)):
                if bit == "0": qc.x(i)
        qc.barrier()

        # Diffusion
        qc.h(range(n))
        qc.x(range(n))
        if n > 1:
            qc.h(n - 1)
            qc.mcx(list(range(n - 1)), n - 1)
            qc.h(n - 1)
        else:
            qc.z(0)
        qc.x(range(n))
        qc.h(range(n))

    counts = run_circuit(qc)
    best_bin = max(counts, key=counts.get)
    best_idx = int(best_bin, 2) % len(legal_moves)

    return move_scores[best_idx], legal_moves[best_idx]

def select_best_quantum_move(board: chess.Board, depth: int = 2) -> chess.Move:
    '''
    Interface for the engine to select the best move using quantum search.
    '''
    _, move = quantum_minimax(board, depth)
    return move