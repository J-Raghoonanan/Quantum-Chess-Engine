import chess
import sys
import os
import pytest
from qiskit import transpile, QuantumCircuit
from qiskit_aer import Aer 
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
from src.quantum_backend import select_best_quantum_move


@pytest.mark.parametrize("depth", [1, 2, 3])
def test_quantum_minimax(depth):
    board = chess.Board()
    move = select_best_quantum_move(board, depth=depth)

    assert move is not None, f"No move returned at depth {depth}"
    assert move in board.legal_moves, f"Returned move {move} is not legal at depth {depth}"
    print(f"Depth {depth}: Selected move {board.san(move)}")
    return

def test_grover_circuit_marked_state():
    # Simulate Grover's algorithm with a known marked state (index 5)
    n = 3  # 3 qubits → 8 states
    marked_index = 5
    bits = format(marked_index, "03b")

    qc = QuantumCircuit(n, n)
    qc.h(range(n))

    # Oracle for index 5
    for i, bit in enumerate(reversed(bits)):
        if bit == "0":
            qc.x(i)
    qc.h(n - 1)
    qc.mcx(list(range(n - 1)), n - 1)
    qc.h(n - 1)
    for i, bit in enumerate(reversed(bits)):
        if bit == "0":
            qc.x(i)

    # Diffusion operator
    qc.h(range(n))
    qc.x(range(n))
    qc.h(n - 1)
    qc.mcx(list(range(n - 1)), n - 1)
    qc.h(n - 1)
    qc.x(range(n))
    qc.h(range(n))

    qc.measure_all()
    backend = Aer.get_backend("aer_simulator")
    transpiled_qc = transpile(qc, backend)
    job = backend.run(transpiled_qc, shots=1024)  # type: ignore
    result = job.result()
    counts = result.get_counts()

    top_state = max(counts, key=counts.get)
    print(f"Most measured state: {top_state}, expected: {format(marked_index, '03b')}")
    assert top_state.strip().split()[0] == format(marked_index, "03b"), "Grover's algorithm did not amplify the correct state sufficiently"
    '''
    Note:
    Trims whitespace
    Takes the first group in case multiple bitstrings are returned (which can happen with classical + quantum registers)
    '''
    return

def test_grover_multiple_marked():
    n = 3  # 3 qubits → 8 states
    marked_indices = [2, 5]  # multiple marked states
    qc = QuantumCircuit(n, n)
    qc.h(range(n))

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

    qc.h(range(n))
    qc.x(range(n))
    qc.h(n - 1)
    qc.mcx(list(range(n - 1)), n - 1)
    qc.h(n - 1)
    qc.x(range(n))
    qc.h(range(n))

    qc.measure_all()
    backend = Aer.get_backend("aer_simulator")
    transpiled_qc = transpile(qc, backend)
    job = backend.run(transpiled_qc, shots=1024)  # type: ignore
    result = job.result()
    counts = result.get_counts()

    sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    print("Top measured states:", sorted_counts[:3])
    top_state = sorted_counts[0][0]
    assert top_state.strip().split()[0] in [format(i, "03b") for i in marked_indices], "Grover's algorithm did not amplify a marked state sufficiently"
    return
