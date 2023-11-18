import sys
sys.path.append("../Qhyper")
from QHyper.problems.workflow_scheduling import (
    Workflow,
    WorkflowSchedulingProblem,
)
hyper_params = {'cost_function_weight': 1, # weight for: cost function
               'deadline_linear_form_weight': -2, # weight for: deadline constraint - linear form (-- this is from the unbalanced penalization approach)
                'deadline_quadratic_form_weight': 2} # weight for: deadline constraint - quadratic form
import numpy as np
import sympy
from sympy.core.expr import Expr

from QHyper.problems.base import Problem
from QHyper.util import Expression

from QHyper.problems.workflow_scheduling import (
    Workflow,
    WorkflowSchedulingProblem,
)

tasks_file =  "workflows_data/workflows/3_tasks_3_machines_1_path.json"
machines_file = "workflows_data/machines/machines_for_3_tasks_3_machines_1_path.json"
deadline = 13

class SimpleWorkflowProblem(Problem):


    def __init__(self) -> None:
        #uwaga: to jest na sztywno
        num_of_qubits = 6 #wsp.workflow.cost_matrix.shape[0] * wsp.workflow.cost_matrix.shape[1]
        self.variables = sympy.symbols(' '.join([f'x{i}' for i in range(num_of_qubits)]))
        self._set_objective_function()
        self._set_constraints()

    def _set_objective_function(self) -> None:

        C_f = (6.0*(1-self.variables[0])*(1-self.variables[1])
        + 8.0*(1-self.variables[0])*(self.variables[1])
        + 8.0*(self.variables[0])*(1-self.variables[1])
        + 2.0*(self.variables[0])*(self.variables[1])
        + 3.0*(1-self.variables[2])*(1-self.variables[3])
        + 4.0*(1-self.variables[2])*(self.variables[3])
        + 4.0*(self.variables[2])*(1-self.variables[3])
        + 1.0*(self.variables[2])*(self.variables[3])
        + 12.0*(1-self.variables[4])*(1-self.variables[5])
        + 16.0*(1-self.variables[4])*(self.variables[5])
        + 16.0*(self.variables[4])*(1-self.variables[5])
        + 4.0*(self.variables[4])*(self.variables[5])  )

        self.deadline_aux=(6.0*(1-self.variables[0])*(1-self.variables[1])
       + 2.0*(1-self.variables[0])*(self.variables[1])
        + 4.0*(self.variables[0])*(1-self.variables[1])
        + 16.0*(self.variables[0])*(self.variables[1])
        + 3.0*(1-self.variables[2])*(1-self.variables[3])
        + 1.0*(1-self.variables[2])*(self.variables[3])
        + 2.0*(self.variables[2])*(1-self.variables[3])
        + 8.0*(self.variables[2])*(self.variables[3])
        + 12.0*(1-self.variables[4])*(1-self.variables[5])
        + 4.0*(1-self.variables[4])*(self.variables[5])
        + 8.0*(self.variables[4])*(1-self.variables[5])
        + 32.0*(self.variables[4])*(self.variables[5])  )

        K_f4_linear = deadline - self.deadline_aux
        K_f4_squared=K_f4_linear**2
        K_f4_squared1=sympy.expand(K_f4_squared)

       # print(K_f4_squared1, "\n\n")

        for i in range(6):
            K_f4_squared1=K_f4_squared1.subs(self.variables[i]**2, self.variables[i])
        #print(K_f4_squared1,"\n\n")

       # print(K_f4_squared1)
        self.objective_function = (Expression(hyper_params['cost_function_weight'] * C_f
                                              + hyper_params['deadline_linear_form_weight'] *  K_f4_linear
                                   + hyper_params['deadline_quadratic_form_weight'] * K_f4_linear**2))

    def _set_constraints(self):
       # print(self.deadline_aux)




        self.constraints = []

    def get_score(self, result, penalty=0):

        x = [int(val) for val in result]

        if (6.0*(1.0-x[0])*(1-x[1])
        + 2.0*(1.0-x[0])*(x[1])
        + 4.0*(x[0])*(1.0-x[1])
        + 16.0*(x[0])*(x[1])
        + 3.0*(1.0-x[2])*(1.0-x[3])
        + 1.0*(1.0-x[2])*(x[3])
        + 2.0*(x[2])*(1.0-x[3])
        + 8.0*(x[2])*(x[3])
        + 12.0*(1.0-x[4])*(1.0-x[5])
        + 4.0*(1.0-x[4])*(x[5])
        + 8.0*(x[4])*(1.0-x[5])
        + 32.0*(x[4])*(x[5]) <=13 ):

            return (6.0*(1.0-x[0])*(1.0-x[1])
        + 8.0*(1.0-x[0])*(x[1])
        + 8.0*(x[0])*(1.0-x[1])
        + 2.0*(x[0])*(x[1])
        + 3.0*(1.0-x[2])*(1.0-x[3])
        + 4.0*(1.0-x[2])*(x[3])
        + 4.0*(x[2])*(1.0-x[3])
        + 1.0*(x[2])*(x[3])
        + 12.0*(1.0-x[4])*(1.0-x[5])
        + 16.0*(1.0-x[4])*(x[5])
        + 16.0*(x[4])*(1.0-x[5])
        + 4.0*(x[4])*(x[5]) )

        return penalty
    
    

problem = SimpleWorkflowProblem()
print(f"Variables used to describe objective function"
      f" and constraints: {problem.variables}")
print(f"Objective function: {problem.objective_function}")
print("Constraints (RHS == 0):")
for constraint in problem.constraints:
    print(f"    {constraint}")
    
params_config = {
       'angles': [[0.1e-13]*6, [np.pi/2]*6], # QAOA angles - first we have gammas (for the cost Hamiltonian), then we have betas (for the mixer)
    #'angles': [[3.23810485e-04,  3.89068182e-04,  4.08362541e-04,  2.18136406e-04,
   #3.91692476e-04,  3.01205096e-04],
 #[-2.51645530e+02, -1.22816763e+02, -1.20555243e+02, -9.45352537e+01,
  #-9.88528753e+01, -8.19648493e+01]] , 
    'hyper_args': [1, # do not change - this should be the weight for the 'cost function' but since in our cost function
                          # we also have the deadline in the linear form (as of now it needs to be implemented this way due to QHyper limitations)
                          # the weight for the actual cost function is set there. THIS WILL NOT WORK WELL WITH HYPER-QAOA.

                       ],
}

from QHyper.solvers import VQA
solver_config = {
    "pqc": {
        "type": "qml_qaoa",
        "layers": 6,
        "optimizer": "qng",
        "optimizer_args": {
            "stepsize": 0.0001,
            "steps": 1,
            "verbose": True,
        },
        "backend": "default.qubit",
    },
    "params_inits": params_config
}
vqa = VQA.from_config(problem, config=solver_config)


solver_results = vqa.solve()
print(f"Best params: {solver_results.params}")

from QHyper.util import (
    weighted_avg_evaluation, sort_solver_results, add_evaluation_to_results)

# Evaluate results with weighted average evaluation
print("Evaluation:")
print(weighted_avg_evaluation(
    solver_results.results_probabilities, problem.get_score,
    penalty=0, limit_results=64, normalize=True
))
print("Sort results:")
sorted_results = sort_solver_results(
    solver_results.results_probabilities, limit_results=64)

# Add evaluation to results
results_with_evaluation = add_evaluation_to_results(
    sorted_results, problem.get_score, penalty=0)

for result, (probability, evaluation) in results_with_evaluation.items():
    print(f"Result: {result}, "
          f"Prob: {probability:.5}, "
          f"Evaluation: {evaluation}")
    
from QHyper.solvers import VQA
tester_config = {
    'pqc': {
        'type': 'qaoa',
        'layers': 6,
    }
}

tester = VQA.from_config(problem, config=tester_config)
bp={'angles': ([[ 3.23810485e-04,  3.89068182e-04,  4.08362541e-04,
          2.18136406e-04,  3.91692476e-04,  3.01205096e-04],
        [-2.51645530e+02, -1.22816763e+02, -1.20555243e+02,
         -9.45352537e+01, -9.88528753e+01, -8.19648493e+01]]), 'hyper_args': [1]}

solver_results1=tester.solve(bp)
# Evaluate results with weighted average evaluation
print("Evaluation:")
print(weighted_avg_evaluation(
    solver_results1.results_probabilities, problem.get_score,
    penalty=0, limit_results=64, normalize=True
))
print("Sort results:")
sorted_results1 = sort_solver_results(
    solver_results1.results_probabilities, limit_results=64)

# Add evaluation to results
results_with_evaluation = add_evaluation_to_results(
    sorted_results1, problem.get_score, penalty=0)

for result, (probability, evaluation) in results_with_evaluation.items():
    print(f"Result: {result}, "
          f"Prob: {probability:.5}, "
          f"Evaluation: {evaluation}")


