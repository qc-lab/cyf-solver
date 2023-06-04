import sympy
from QHyper.problems.base import Problem
import networkx as nx
from QHyper.hyperparameter_gen.parser import Expression
from sympy.core.expr import Expr
from typing import cast

import csv
import time

from matplotlib import pyplot as plt
from QHyper.problems.base import Problem
import os, os.path
import networkx as nx
import numpy as np
import networkx.algorithms.community as nx_comm


COLORS = {0: 'blue', 1: 'red', 2: '#2a401f', 3: '#cce6ff',
          4:'pink', 5: '#4ebd1a', 6: '#66ff66', 7:'yellow',
          8: '#0059b3', 9: '#703243', 10: 'green', 11: 'black',
          12:'#3495eb', 13: '#525c4d', 14: '#1aff1a', 15: 'brown', 16: 'gray'}


def safe_open(path, permission):
    ''' 
    Open "path" for writing, creating any parent directories as needed.
    '''
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return open(path, permission)



class BrainCommunityDetectionProblem(Problem):
    def __init__(self, path, data_name, num_clusters):
            self.num_cases = num_clusters
            self.data_name = data_name
            self.A = np.genfromtxt(f'{path}/{data_name}.csv', delimiter='	')
            self.G = nx.from_numpy_matrix(self.A)
            self.B = nx.modularity_matrix(self.G)
            self._set_variables()
            self.objective_function = [] # Due to sympy expression err
            self.constraints = []

    
    def _set_variables(self) -> None:
        self.variables = sympy.symbols(' '.join(
            [f'x{i}' for i in range(len(self.G.nodes))]
        ))

    def _set_objective_function(self) -> None:
        """
        Create the objective function on defined in SymPy syntax
        """
        # xs = [f"x{i}" for i in range(len(self.G.nodes))]
        equation: Expr = cast(Expr, 0)
        for i in self.G.nodes():
            for j in range(i+1, len(self.G.nodes)):
                u_var, v_var = self.variables[i], self.variables[j]
                equation += u_var*v_var*self.B[i,j]
        equation *= -1
        
        self.objective_function = Expression(equation)
    
    
    def get_score(self, result: str) -> float | None:
        pass
    
    def compare_with_louvain(self):
        start = time.time()
        communities_class = nx_comm.louvain_communities(self.G)#, seed=123)
        end = time.time()

        mods_LCDA, times_LCDA, Ncomms = [], [], []
        total_time = end - start
        mods_LCDA.append(nx_comm.modularity(self.G, communities_class))
        times_LCDA .append(total_time)
        Ncomms.append(len(communities_class))

        return (communities_class, mods_LCDA, times_LCDA, Ncomms, total_time)
    
    
    def plot_results(self, output_folder, results):
        communities, run_time, energy, counts, sample = results
        communities_class, mods_LCDA, times_LCDA, Ncomms, total_time = self.compare_with_louvain()

        headers = ['modularity_classical', 'modularity_quantum', 'communities', 'run_time_dwave', 'energy', 'counts', 'sample', 'communities_class_louvain', 'time_louvain']
        data = [nx_comm.modularity(self.G, communities_class),  nx_comm.modularity(self.G, communities), communities, run_time, energy, counts, sample, communities_class, total_time]
        with safe_open(f'{output_folder}/{self.data_name}run{self.num_cases}.csv', 'w') as file:
            writer = csv.writer(file)
            writer.writerow(headers)
            writer.writerow(data)

        color_map = []

        for node in self.G: # 1, 2, 3
            color_map.append(COLORS[sample[node]])
        f = plt.figure()

        nx.draw(self.G, node_color=color_map, with_labels=True, ax=f.add_subplot(111))
        f.savefig(f"{output_folder}/{self.data_name}graph{self.num_cases}.png")

        clus = np.zeros((len(self.G.nodes), 2))

        for i, node in enumerate(self.G):
            clus[i, 0] = node
            clus[i, 1] = sample[node]

        np.savetxt(f"{output_folder}/{self.data_name}graph{self.num_cases}.csv", clus, delimiter=",")
        
