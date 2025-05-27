from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer
import numpy as np


def run_circuit(qc, shots=1024):
    qc.measure_all()
    backend = Aer.get_backend("aer_simulator")
    transpiled_qc = transpile(qc, backend)
    job = backend.run(transpiled, shots=shots)
    return job.result().get_counts()


def run_grover_search(moves, marked_indices):
    n = int(np.ceil(np.log2(len(moves))))
    N = 2**n
    M = len(marked_indices)
    R = max(1, int(np.round(np.pi/4 * np.sqrt(N/M))))

    qc = QuantumCircuit(n)
    qc.h(range(n))

    for _ in range(R):
        # Oracle
        for idx in marked_indices:
            bits = format(idx, f'0{n}b')
            for i, bit in enumerate(reversed(bits)):
                if bit == '0': qc.x(i)
            qc.h(n-1)
            qc.mcx(list(range(n-1)), n-1)
            qc.h(n-1)
            for i, bit in enumerate(reversed(bits)):
                if bit == '0': qc.x(i)
        qc.barrier()
        # Diffusion
        qc.h(range(n))
        qc.x(range(n))
        qc.h(n-1)
        qc.mcx(list(range(n-1)), n-1)
        qc.h(n-1)
        qc.x(range(n))
        qc.h(range(n))

    counts = run_circuit(qc)
    top = max(counts, key=counts.get)
    selected_index = int(top, 2)
    return moves[selected_index % len(moves)]