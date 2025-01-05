import pennylane as qml
from pennylane import numpy as np

from numpy.typing import NDArray
from typing import Any, Callable, cast

from dataclasses import dataclass, field

from QHyper.problems.base import Problem
from QHyper.optimizers import OptimizationResult, Optimizer, Dummy, OptimizationParameter

from QHyper.converter import Converter
from QHyper.polynomial import Polynomial
from QHyper.solvers.base import Solver, SolverResult, SolverException
from QHyper.util import weighted_avg_evaluation

from QHyper.solvers.gate_based.pennylane.qaoa import QAOA


@dataclass
class WF_QAOA(QAOA):
    """
    Different implementation of QAOA.
    This implementation uses different function to evaluate the hamiltonian -
    this function doesn't return expectation value but the score of the
    solution.

    Attributes
    ----------
    problem : Problem
        The problem to be solved.
    layers : int
        Number of layers.
    gamma : OptimizationParameter
        Vector of gamma angles used in cost Hamiltonian. Size of the vector
        should be equal to the number of layers.
    beta : OptimizationParameter
        Vector of beta angles used in mixing Hamiltonian. Size of the vector    
        should be equal to the number of layers.
    optimizer : Optimizer
        Optimizer used in the classical part of the algorithm.
    weights : list[float] | None
        Weights used for converting Problem to QUBO. They connect cost function
        with constraints. If not specified, all weights are set to 1.
    limit_results : int | None, default None
        Specifies how many results should be considered in the evaluation of
        the objective function. If None, all results are considered.
    penalty : float, default 0
        When calculating the score of the solution, the penalty is the score 
        for the solution that doesn't satisfy the constraints.
    backend : str, default 'default.qubit'
        Backend for PennyLane.
    mixer : str, default 'pl_x_mixer'
        Mixer name. Currently only 'pl_x_mixer' is supported.
    qubo_cache : dict[tuple[float, ...], qml.Hamiltonian]
        Cache for QUBO.
    dev : qml.Device
        PennyLane device instance.
    """

    problem: Problem
    layers: int
    gamma: OptimizationParameter
    beta: OptimizationParameter
    optimizer: Optimizer
    weights: list[float] | None
    penalty: float = 0
    backend: str = "default.qubit"
    mixer: str = "pl_x_mixer"
    limit_results: int | None = None
    qubo_cache: dict[tuple[float, ...], qml.Hamiltonian] = field(
        default_factory=dict, init=False)
    dev: qml.Device | None = field(default=None, init=False)

    def __init__(
            self,
            problem: Problem,
            layers: int,
            gamma: OptimizationParameter,
            beta: OptimizationParameter,
            weights: list[float] | None = None,
            penalty: float = 0,
            backend: str = "default.qubit",
            mixer: str = "pl_x_mixer",
            limit_results: int | None = None,
            optimizer: Optimizer = Dummy(),
    ) -> None:
        self.problem = problem
        self.optimizer = optimizer
        self.gamma = gamma
        self.beta = beta
        self.penalty = penalty
        self.weights = weights
        self.limit_results = limit_results
        self.layers = layers
        self.backend = backend
        self.mixer = mixer
        self.qubo_cache = {}

    def get_expval_circuit(self, weights: list[float]
                           ) -> Callable[[list[float]], float]:
        cost_operator = self.create_cost_operator(self.problem, weights)

        self.dev = qml.device(self.backend, wires=cost_operator.wires)

        probs_func = self.get_probs_func(self.problem, weights)

        def wrapper(angles: list[float]) -> float:
            probs = probs_func(angles)
            if isinstance(probs, np.numpy_boxes.ArrayBox):
                probs = probs._value

            dtype = [
                (wire, 'i4') for wire in self.dev.wires]+[('probability', 'f8')]
            recarray = np.recarray((len(probs),), dtype=dtype)
            for i, probability in enumerate(probs):
                solution = format(i, "b").zfill(self._get_num_of_wires())
                recarray[i] = *solution, probability

            result = weighted_avg_evaluation(
                recarray, self.problem.get_score, self.penalty,
                limit_results=self.limit_results
            )
            return OptimizationResult(result, angles)
        return wrapper
