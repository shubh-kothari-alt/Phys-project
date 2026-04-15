from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

# 3-qubit GHZ State: (|000> + |111>) / sqrt(2)
qc3 = QuantumCircuit(3, 3)
qc3.h(0)
qc3.cx(0, 1)
qc3.cx(0, 2)
qc3.measure([0, 1, 2], [0, 1, 2])

backend = AerSimulator()

def q3(s):
    job = backend.run(qc3, shots=s)
    result = job.result()
    counts = result.get_counts(qc3)
    # All 8 possible 3-qubit states
    c = {"000": 0, "001": 0, "010": 0, "011": 0,
         "100": 0, "101": 0, "110": 0, "111": 0}
    c.update(counts)
    fig = plot_histogram(c)
    return fig
