from qiskit import QuantumCircuit
import matplotlib.pyplot as plt

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

def create_figure_1():
    qc = grover_example_circuit()
    qc.draw("mpl")
    plt.tight_layout()
    plt.savefig("fig1_grover_circuit.pdf", dpi=300)
    return

def create_figure_2():
    circuit_depths = [0, 0, 0, 0]
    grover_scores = [0, 0, 0, 0]     #  output from Grover engine
    stockfish_scores = [0, 0, 0, 0]  # Same positions, using Stockfish

    plt.plot(circuit_depths, grover_scores, label='Grover Engine', marker='o')
    plt.plot(circuit_depths, stockfish_scores, label='Stockfish', marker='s')
    plt.xlabel('Grover Iterations (Circuit Depth)')
    plt.ylabel('Chess Advantage Score')
    plt.title('FIG. 2: Circuit Depth vs Chess Advantage')
    plt.legend()
    plt.grid(True)
    plt.savefig('fig2_advantage_vs_depth.pdf', dpi=300)
    return

def create_figure_3():
    depths = [1, 2, 3, 4]
    grover_times = [0.0 ,0.0, 0.0, 0.0]
    stockfish_times = [0.0 ,0.0, 0.0, 0.0]

    plt.plot(grover_times, depths, label='Grover Engine', marker='o')
    plt.plot(stockfish_times, depths, label='Stockfish', marker='s')
    plt.xlabel('Time (seconds)')
    plt.ylabel('Search Depth')
    plt.title('FIG. 3: Time vs Search Depth')
    plt.legend()
    plt.grid(True)
    plt.savefig('fig3_time_vs_depth.pdf', dpi=300)
    return


if __name__== "__main__":
    create_figure_1()
    # create_figure_2()
    # create_figure_3()
    
