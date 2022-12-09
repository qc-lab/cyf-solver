import multiprocessing as mp
from dataclasses import dataclass
from typing import Any, Callable

import numpy as np
import tqdm

from .optimizer import ArgsType, HyperparametersOptimizer, Optimizer, Worker


@dataclass
class Random(HyperparametersOptimizer):
    """Simple random search
    
    Attributes
    ----------
    number_of_samples : int
        number of random samples (default 100)
    processes : int
         number of processors that will be used (default cpu count)
    """
    number_of_samples: int = 100
    processes: int = mp.cpu_count()

    def minimize(
            self,
            func_creator: Callable[[ArgsType], Callable[[ArgsType], float]],
            optimizer: Optimizer,
            init: ArgsType,
            hyperparams_init: ArgsType = None,
            bounds: list[float] = [0, 10]
    ) -> ArgsType:
        """Returns hyperparameters which lead to the lowest values returned by the optimizer
    
        Parameters
        ----------
        func_creator : Callable[[ArgsType], Callable[[ArgsType], float]]
            function which receives hyperparameters and returns
            a function which will be optimized using the optimizer
        optimizer : Optimizer
            object of the Optimizer class
        init : ArgsType
            initial args for the optimizer
        hyperparams_init : ArgsType
            initial hyperparameters
        bounds : list[float]
            bounds for hyperparameters (default None)

        Returns
        -------
        ArgsType
            Returns hyperparameters which lead to the lowest values returned by the optimizer
        """
        hyperparams_init = np.array(hyperparams_init)

        hyperparams = (
                (bounds[1] - bounds[0])
                * np.random.rand(self.number_of_samples, *hyperparams_init.shape)
                + bounds[0])

        worker = Worker(func_creator, optimizer, init)

        with mp.Pool(processes=self.processes) as p:
            results = list(tqdm.tqdm(p.imap(worker.func, hyperparams), total=self.number_of_samples))

        min_idx = np.argmin([result for result in results])

        return hyperparams[min_idx]
