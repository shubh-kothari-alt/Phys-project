# Quantum Entanglement of a Binary Qubit System

This project demonstrates the creation, simulation, and visualization of quantum entanglement between two qubits (representing binary electron spins) using Qiskit and Python.

## Overview

Quantum entanglement is a fundamental phenomenon in quantum mechanics where two or more particles become linked and share quantum states, such that the state of one particle instantly influences the state of the other, no matter the distance between them. This property is a cornerstone for quantum computing, quantum cryptography, and teleportation.

In this repository, the entanglement between two qubits is generated and analyzed as a Bell state:

$$
|\Phi^+\rangle = \frac{1}{\sqrt{2}}(|00\rangle + |11\rangle)
$$

where $|00>$ and $|11>$ represent binary states of two electrons or spins.For more information on this topic,check the websites in the [References](#references) section.

## Features

- Builds a quantum circuit initializing two qubits in the Bell state
- Uses Qiskit Aer for quantum circuit simulation
- Displays measurement results as histograms
- Visualizes quantum statevectors for entangled states

## Getting Started

### Prerequisites

- Python 3.8+
- Qiskit (v1.0+)
- Matplotlib

Install dependencies:


pip install qiskit , matplotlib , qiskit_aer , qiskit_ibm_runtime





### Usage

Run the Flask file in a Python environment.

<img width="1036" height="849" alt="image" src="https://github.com/user-attachments/assets/48b7efb9-1e8e-4a1d-8b30-692280865a60" />

The chart here shows the quantum entanglement of $|00>$ and $|11>$ qubits while the input box is to specify the number of qubits (100 by default).

The number of qubits can be any integer greater than 1

## Results

- **Measurement outcomes:** Only $|00>$ and $|11>$ states appear, with near-equal probabilities, confirming quantum entanglement.
- **Statevector visualization:** Shows the symmetric superposition of both qubits.

## References

- [IBM Quantum Qiskit Documentation](https://quantum.cloud.ibm.com/docs/en/guides)
- [Visualizing Quantum Results](https://quantum.cloud.ibm.com/docs/en/guides/visualize-results)
- [Quantum Entanglement Theory](https://scienceexchange.caltech.edu/topics/quantum-science-explained/entanglement)


---

Contributions and improvements are welcome!
