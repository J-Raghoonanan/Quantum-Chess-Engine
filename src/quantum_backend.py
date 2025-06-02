from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer 
import numpy as np
import chess


# # Simple evaluation based on material balance and mobility
# PIECE_VALUES = {
#     "P": 1, "N": 3, "B": 3, "R": 5, "Q": 9, "K": 0
# }

# Piece-square tables (simplified)
PSQT = {
    chess.PAWN:   [0, 5, 5, 0, 5, 10, 50, 0],
    chess.KNIGHT: [-50, -40, -30, -30, -30, -30, -40, -50],
    chess.BISHOP: [-20, -10, -10, -10, -10, -10, -10, -20],
    chess.ROOK:   [0, 0, 5, 10, 10, 5, 0, 0],
    chess.QUEEN:  [-20, -10, -10, 0, 0, -10, -10, -20],
    chess.KING:   [-30, -40, -40, -50, -50, -40, -40, -30],
}

PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 0
}

def evaluate_position(board: chess.Board) -> int:
    '''
    Evaluates a board position using Stockfish-inspired heuristics.
    '''

    if board.is_checkmate():
        return -99999 if board.turn else 99999
    if board.is_stalemate() or board.is_insufficient_material():
        return 0

    score = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            value = PIECE_VALUES[piece.piece_type]
            rank = chess.square_rank(square) if piece.color == chess.WHITE else 7 - chess.square_rank(square)
            psqt_bonus = PSQT.get(piece.piece_type, [0]*8)[rank]
            modifier = 1 if piece.color == chess.WHITE else -1
            score += modifier * (value + psqt_bonus)

    # Add mobility bonus
    # Material score + mobility; more available moves = better position generally; 
    # weighted to not outweight score of a single pawn
    score += 5 * (len(list(board.legal_moves))) * (1 if board.turn else -1)
    return score

def run_circuit(qc, shots=1024):
    qc.measure_all()
    backend = Aer.get_backend("aer_simulator")
    transpiled_qc = transpile(qc, backend)
    job = backend.run(transpiled_qc, shots=shots)
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
    R = max(1, int(np.floor(np.pi / 4 * np.sqrt(N / len(marked_indices)))))

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




############################################################################################################
# def evaluate_material(board):
#     '''
#     Returns material balance for the board.
#     '''

#     score = 0
#     for square in board.piece_map():
#         piece = board.piece_at(square)
#         value = PIECE_VALUES.get(piece.symbol().upper(), 0)
#         score += value if piece.color else -value
#     return score

# def evaluate_move(board, move):
#     '''
#     Returns heuristic score for a single move.
#     '''
#     board.push(move)
#     score = evaluate_material(board) + 0.1 * len(list(board.legal_moves))
#     # Material score + mobility; more available moves = better position generally; 
#     # weighted by 0.1 to not outweight score of a single pawn
#     board.pop()
#     return score

# def evaluate_depth_2(board, move):
#     '''
#     Evaluates a move based on the best response of the opponent.
#     '''
#     board.push(move)
#     if board.is_game_over():
#         board.pop()
#         return float("inf")  # Force winning moves
    
#     opponent_moves = list(board.legal_moves)
#     if not opponent_moves:
#         board.pop()
#         return float("inf")  # Mate or stalemate

#     # Opponent picks their best response (worst for us)
#     responses = [evaluate_move(board, opp_move) for opp_move in opponent_moves]
#     board.pop()
#     return -max(responses)  # Minimax: assume best opponent reply

# def run_circuit(qc, shots=1024):
#     qc.measure_all()
#     backend = Aer.get_backend("aer_simulator")
#     transpiled_qc = transpile(qc, backend)
#     job = backend.run(transpiled_qc, shots=shots)
#     return job.result().get_counts()


# def run_grover_search(board, moves, shots=1024):
#     '''
#     Runs Grover's algorithm to select the best move based on depth-2 evaluation.
#     '''

#     if len(moves) == 0:
#         return None  # no move possible
#     if len(moves) == 1:
#         return moves[0]  # only one legal move, no need for Grover
    
#     # Adaptive thresholding
#     # Choose moves that have values > half a std. dev above the mean
#     scores = [evaluate_depth_2(board, m) for m in moves]
#     mu, sigma = np.mean(scores), np.std(scores)
#     theta = mu + 0.5 * sigma
#     marked_indices = [i for i, s in enumerate(scores) if s >= theta]

#     N = 2 ** int(np.ceil(np.log2(len(moves))))
#     n = int(np.log2(N))
#     M = len(marked_indices)

#     if M == 0:
#         return moves[np.argmax(scores)]  # fallback to best by score

#     R = max(1, int(np.floor(np.pi / 4 * np.sqrt(N / M))))
#     qc = QuantumCircuit(n)
#     qc.h(range(n))

#     for _ in range(R):
#         # Oracle: flip marked indices
#         for idx in marked_indices:
#             bits = format(idx, f"0{n}b")
#             for i, bit in enumerate(reversed(bits)):
#                 if bit == "0":
#                     qc.x(i)

#             if n > 1:
#                 qc.h(n - 1)
#                 qc.mcx(list(range(n - 1)), n - 1)
#                 qc.h(n - 1)
#             else:
#                 qc.z(0)  # single-qubit phase flip fallback
#             # qc.h(n - 1)
#             # qc.mcx(list(range(n - 1)), n - 1)
#             # qc.h(n - 1)


#             for i, bit in enumerate(reversed(bits)):
#                 if bit == "0":
#                     qc.x(i)
#         qc.barrier()

#         # Diffusion operator
#         qc.h(range(n))
#         qc.x(range(n))

#         if n > 1:
#             qc.h(n - 1)
#             qc.mcx(list(range(n - 1)), n - 1)
#             qc.h(n - 1)
#         else:
#             qc.z(0)  # single-qubit phase flip fallback
#         # qc.h(n - 1)
#         # qc.mcx(list(range(n - 1)), n - 1)
#         # qc.h(n - 1)

#         qc.x(range(n))
#         qc.h(range(n))

#     counts = run_circuit(qc)

#     most_common = max(counts, key=counts.get)
#     index = int(most_common, 2) % len(moves)
#     return moves[index]