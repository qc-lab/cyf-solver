# This work was supported by the EuroHPC PL infrastructure funded at the
# Smart Growth Operational Programme (2014-2020), Measure 4.2
# under the grant agreement no. POIR.04.02.00-00-D014/20-00


from typing import Type
import copy

from .knapsack import KnapsackProblem
from .tsp import TSPProblem
from .maxcut import MaxCutProblem
from .workflow_scheduling import WorkflowSchedulingProblem
from .community_detection import CommunityDetectionProblem, Network

from QHyper.util import search_for

from .base import Problem


PROBLEMS_BY_NAME: dict[str, Type[Problem]] = {
    "knapsack": KnapsackProblem,
    "tsp": TSPProblem,
    "maxcut": MaxCutProblem,
    "workflow_scheduling": WorkflowSchedulingProblem,
    'community_detection': CommunityDetectionProblem
}
users_problems = search_for(Problem, 'QHyper/problems')
PROBLEMS_BY_NAME.update({
    problem.__name__.lower(): problem
    for problem in users_problems
})


class ProblemConfigException(Exception):
    pass


def problem_from_config(config: dict[str, dict[str, any]]) -> Problem:
    """
    Parameters
    ----------
    config : dict[str. Any]
        Configuration in form of dict

    Returns
    -------
    Problem
        Initialized Problem object
    """
    _config = copy.deepcopy(config)
    error_msg = ""
    try:
        error_msg = "Problem configuration was not provided"
        problem_type = str(_config.pop('type'))
        error_msg = f"There is no {problem_type} problem type"
        problem_class = PROBLEMS_BY_NAME[problem_type]
    except KeyError:
        raise ProblemConfigException(error_msg)

    return problem_class(**_config)
