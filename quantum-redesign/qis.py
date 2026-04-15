from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram
import matplotlib
matplotlib.use('Agg')

# 2-qubit Bell State
qc = QuantumCircuit(2, 2)
qc.h(0)
qc.cx(0, 1)
qc.measure([0, 1], [0, 1])

backend = AerSimulator()

def q(s):
    job = backend.run(qc, shots=s)
    result = job.result()
    counts = result.get_counts(qc)
    c = {"00": 0, "01": 0, "10": 0, "11": 0}
    c.update(counts)
    return plot_histogram(c)
