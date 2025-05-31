from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer
import numpy as np


# Simple evaluation based on material balance and mobility
PIECE_VALUES = {
    "P": 1, "N": 3, "B": 3, "R": 5, "Q": 9, "K": 0
}

def evaluate_material(board):
    '''
    Returns material balance for the board.
    '''

    score = 0
    for square in board.piece_map():
        piece = board.piece_at(square)
        value = PIECE_VALUES.get(piece.symbol().upper(), 0)
        score += value if piece.color else -value
    return score

def evaluate_move(board, move):
    '''
    Returns heuristic score for a single move.
    '''
    board.push(move)
    score = evaluate_material(board) + 0.1 * len(list(board.legal_moves))
    # Material score + mobility; more available moves = better position generally; 
    # weighted by 0.1 to not outweight score of a single pawn
    board.pop()
    return score

def evaluate_depth_2(board, move):
    '''
    Evaluates a move based on the best response of the opponent.
    '''
    board.push(move)
    if board.is_game_over():
        board.pop()
        return float("inf")  # Force winning moves
    
    opponent_moves = list(board.legal_moves)
    if not opponent_moves:
        board.pop()
        return float("inf")  # Mate or stalemate

    # Opponent picks their best response (worst for us)
    responses = [evaluate_move(board, opp_move) for opp_move in opponent_moves]
    board.pop()
    return -max(responses)  # Minimax: assume best opponent reply

def run_circuit(qc, shots=1024):
    qc.measure_all()
    backend = Aer.get_backend("aer_simulator")
    transpiled_qc = transpile(qc, backend)
    job = backend.run(transpiled_qc, shots=shots)
    return job.result().get_counts()


def run_grover_search(board, moves, shots=1024):
    '''
    Runs Grover's algorithm to select the best move based on depth-2 evaluation.
    '''

    scores = [evaluate_depth_2(board, m) for m in moves]
    mu, sigma = np.mean(scores), np.std(scores)
    theta = mu + 0.5 * sigma
    marked_indices = [i for i, s in enumerate(scores) if s >= theta]

    N = 2 ** int(np.ceil(np.log2(len(moves))))
    n = int(np.log2(N))
    M = len(marked_indices)

    if M == 0:
        return moves[np.argmax(scores)]  # fallback to best by score

    R = max(1, int(np.floor(np.pi / 4 * np.sqrt(N / M))))
    qc = QuantumCircuit(n)
    qc.h(range(n))

    for _ in range(R):
        # Oracle: flip marked indices
        for idx in marked_indices:
            bits = format(idx, f"0{n}b")
            for i, bit in enumerate(reversed(bits)):
                if bit == "0":
                    qc.x(i)
            qc.h(n - 1)
            qc.mcx(list(range(n - 1)), n - 1)
            qc.h(n - 1)
            for i, bit in enumerate(reversed(bits)):
                if bit == "0":
                    qc.x(i)
        qc.barrier()

        # Diffusion operator
        qc.h(range(n))
        qc.x(range(n))
        qc.h(n - 1)
        qc.mcx(list(range(n - 1)), n - 1)
        qc.h(n - 1)
        qc.x(range(n))
        qc.h(range(n))

    counts = run_circuit(qc)

    most_common = max(counts, key=counts.get)
    index = int(most_common, 2) % len(moves)
    return moves[index]

# def run_grover_search(moves, marked_indices):
#     n = int(np.ceil(np.log2(len(moves))))
#     N = 2**n
#     M = len(marked_indices)
#     R = max(1, int(np.round(np.pi/4 * np.sqrt(N/M))))

#     qc = QuantumCircuit(n)
#     qc.h(range(n))

#     for _ in range(R):
#         # Oracle
#         for idx in marked_indices:
#             bits = format(idx, f'0{n}b')
#             for i, bit in enumerate(reversed(bits)):
#                 if bit == '0': qc.x(i)
#             qc.h(n-1)
#             qc.mcx(list(range(n-1)), n-1)
#             qc.h(n-1)
#             for i, bit in enumerate(reversed(bits)):
#                 if bit == '0': qc.x(i)
#         qc.barrier()
#         # Diffusion
#         qc.h(range(n))
#         qc.x(range(n))
#         qc.h(n-1)
#         qc.mcx(list(range(n-1)), n-1)
#         qc.h(n-1)
#         qc.x(range(n))
#         qc.h(range(n))

#     counts = run_circuit(qc)
#     top = max(counts, key=counts.get)
#     selected_index = int(top, 2)
#     return moves[selected_index % len(moves)]