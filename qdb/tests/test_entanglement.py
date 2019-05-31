import pytest

from qdb.control_flow_graph import QuilControlFlowGraph
from qdb.utils import get_necessary_qubits
from pyquil import Program
from pyquil.gates import X, CNOT, CCNOT


@pytest.mark.parametrize(
    "pq",
    [
        Program(CCNOT(0, 1, 2)),
        Program(CNOT(0, 1), CNOT(1, 2)),
        Program(CNOT(0, 1), CNOT(0, 2)),
    ],
)
def test_simple(pq):
    G = QuilControlFlowGraph(pq)
    assert len(G.blocks) == 1
    for qubits in ([0], [1], [2]):
        assert get_necessary_qubits(G, 0, qubits) == set([0, 1, 2])


@pytest.mark.parametrize(
    "pq",
    [
        Program(CCNOT(0, 1, 2), CNOT(3, 4)),
        Program(CNOT(0, 1), CNOT(1, 2), CNOT(3, 4)),
        Program(CNOT(0, 1), CNOT(0, 2), CNOT(3, 4)),
    ],
)
def test_disjoint(pq):
    G = QuilControlFlowGraph(pq)
    assert len(G.blocks) == 1
    for qubits in ([0], [1], [2]):
        assert get_necessary_qubits(G, 0, qubits) == set([0, 1, 2])
    for qubits in ([3], [4]):
        assert get_necessary_qubits(G, 0, qubits) == set([3, 4])


def test_simple_control_flow():
    pq = Program(CNOT(0, 1), CNOT(2, 3))
    ro = pq.declare("ro")
    ro2 = pq.declare("ro2")
    pq.measure(0, ro)
    pq.measure(2, ro2)
    pq.if_then(ro, Program(X(0)))
    pq.if_then(ro2, Program(X(0)))

    G = QuilControlFlowGraph(pq)

    assert len(G.blocks) == 5
    # FIXME: Need to figure out correct behavior
    assert get_necessary_qubits(G, 0, [0]) == set([0, 1, 2, 3])
    assert get_necessary_qubits(G, 1, [0]) == set([0, 1])
    assert get_necessary_qubits(G, 2, [0]) == set([0, 1])
    assert get_necessary_qubits(G, 3, [0]) == set([0, 1])
    assert get_necessary_qubits(G, 4, [0]) == set([0, 1])

    assert get_necessary_qubits(G, 0, [2]) == set([0, 1, 2, 3])
    assert get_necessary_qubits(G, 1, [2]) == set([2, 3])
    assert get_necessary_qubits(G, 2, [2]) == set([2, 3])
    assert get_necessary_qubits(G, 3, [2]) == set([2, 3])
    assert get_necessary_qubits(G, 4, [2]) == set([2, 3])
