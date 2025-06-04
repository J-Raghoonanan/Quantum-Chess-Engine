from qiskit import QuantumCircuit
import matplotlib.pyplot as plt
import numpy as np

def grover_example_circuit(n:int =5) -> QuantumCircuit:
    qc = QuantumCircuit(n)
    qc.h(range(n))
    # One iteration of Grover (oracle + diffuser) — placeholder
    qc.z(n-1)
    qc.h(range(n))
    qc.x(range(n))
    qc.h(n-1)
    qc.mcx(list(range(n - 1)), n - 1)
    qc.h(n-1)
    qc.x(range(n))
    qc.h(range(n))
    qc.measure_all()
    return qc

def create_circuit_fig():
    qc = grover_example_circuit()
    qc.draw("mpl")
    plt.tight_layout()
    plt.savefig("fig_grover_circuit.pdf", dpi=300)
    return

def create_depth_adv_fig():
    circuit_depths = [0, 0, 0, 0]
    grover_scores = [0, 0, 0, 0]     #  output from Grover engine
    stockfish_scores = [0, 0, 0, 0]  # Same positions, using Stockfish

    plt.plot(circuit_depths, grover_scores, label='Grover Engine', marker='o')
    plt.plot(circuit_depths, stockfish_scores, label='Stockfish', marker='s')
    plt.xlabel('Grover Iterations (Circuit Depth)')
    plt.ylabel('Chess Advantage Score')
    plt.title('Circuit Depth vs Chess Advantage')
    plt.legend()
    plt.grid(True)
    plt.savefig('fig_advantage_vs_depth.pdf', dpi=300)
    return

def create_time_depth_fig():
    depths = [1, 2, 3, 4]
    grover_times = [0.0 ,0.0, 0.0, 0.0]
    stockfish_times = [0.0 ,0.0, 0.0, 0.0]

    plt.plot(grover_times, depths, label='Grover Engine', marker='o')
    plt.plot(stockfish_times, depths, label='Stockfish', marker='s')
    plt.xlabel('Time (seconds)')
    plt.ylabel('Search Depth')
    plt.title('Time vs Search Depth')
    plt.legend()
    plt.grid(True)
    plt.savefig('fig_time_vs_depth.pdf', dpi=300)
    return

def create_cqSearch_fig():
    depths = np.arange(1, 11)
    B_values = [20, 30, 35, 40]
    colors = ['tab:blue', 'tab:green', 'tab:orange', 'tab:red']

    plt.figure()
    for B, color in zip(B_values, colors):
        classical = B ** depths
        quantum = B ** (depths / 2)
        plt.plot(depths, classical, label=f"Classical B={B}", linestyle='--', color=color)
        plt.plot(depths, quantum, label=f"Grover B={B}", linestyle='-', color=color)

    plt.yscale("log")
    plt.xlabel("Search Depth (d)")
    plt.ylabel("Nodes Needed to Explore")
    plt.title("Classical vs Grover Search Scaling")
    plt.legend()
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.savefig("fig_grover_vs_classical_scaling.pdf", dpi=300)


if __name__== "__main__":
    create_circuit_fig()
    # create_depth_adv_fig()
    # create_time_depth_fig()
    create_cqSearch_fig()
    
