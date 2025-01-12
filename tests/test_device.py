# Copyright 2018 Xanadu Quantum Technologies Inc.

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Tests that plugin devices are accessible and integrate with PennyLane"""
import numpy as np
import pennylane as qml
import pytest

from conftest import shortnames


class TestDeviceIntegration:
    """Test the devices work correctly from the PennyLane frontend."""

    @pytest.mark.parametrize("d", shortnames)
    def test_load_device(self, d):
        """Test that the device loads correctly"""
        dev = qml.device(d, wires=2, shots=1024)
        assert dev.num_wires == 2
        assert dev.shots == 1024
        assert dev.short_name == d

    @pytest.mark.parametrize("d", shortnames)
    def test_args(self, d):
        """Test that the device requires correct arguments"""
        with pytest.raises(TypeError, match="missing 1 required positional argument"):
            qml.device(d)

        # IonQ devices do not allow shots=None
        with pytest.raises(ValueError, match="does not support analytic"):
            qml.device(d, wires=1, shots=None)

    @pytest.mark.parametrize("shots", [8192])
    def test_one_qubit_circuit(self, shots, tol):
        """Test that devices provide correct result for a simple circuit"""
        dev = qml.device("ionq.simulator", wires=1, shots=shots)

        a = 0.543
        b = 0.123
        c = 0.987

        @qml.qnode(dev)
        def circuit(x, y, z):
            """Reference QNode"""
            qml.BasisState(np.array([1]), wires=0)
            qml.Hadamard(wires=0)
            qml.Rot(x, y, z, wires=0)
            return qml.expval(qml.PauliZ(0))

        assert np.allclose(circuit(a, b, c), np.cos(a) * np.sin(b), **tol)

    @pytest.mark.parametrize("shots", [8192])
    def test_one_qubit_ordering(self, shots, tol):
        """Test that probabilities are returned with the correct qubit ordering"""
        dev = qml.device("ionq.simulator", wires=2, shots=shots)

        @qml.qnode(dev)
        def circuit():
            qml.PauliX(wires=1)
            return qml.probs(wires=[0, 1])

        res = circuit()
        assert np.allclose(res, np.array([0., 1., 0., 0.]), **tol)

    @pytest.mark.parametrize("d", shortnames)
    def test_prob_no_results(self, d):
        """Test that the prob attribute is
        None if no job has yet been run."""
        dev = qml.device(d, wires=1, shots=1)
        assert dev.prob is None
