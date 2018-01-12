The p-Regions Problem
=====================



The task
--------

The `p-regions` problem is defined as a regionalization task where the number of regions (clusters) is known. This number is often denoted by `p` in the literature, hence the name of the problem. The goal is to construct regions with a large degree of similarity among a region's areas and with large dissimilarities between regions. Furthermore, each region has to consist of *spatially contiguous* areas. This condition distinguishes regionalization algorithms from conventional clustering algorithms like the k-Means-algorithm.

There are many approaches to solving the p-regions problem. One way to solve it is to translate it into an mixed integer program and solve it `exactly <#p-region-exact>`_ while another category of algorithms comprises `heuristic approaches <#p-region-heu>`_.



An example
----------

Let's have a look at an example. :numref:`input` is a map with nine areas. Each area has an attribute which is color-coded in the figure.

.. _input:
.. figure:: input.png

    Input

Assume we want to cluster the areas into two regions. :numref:`output` shows a possible solution.

.. _output:
.. figure:: output.png

   Output

Defining the input data, calculating the solution and saving both figures takes less than 40 lines of code -- `check it out <../../../../source/users/p-regions/generate_figures.py>`_.


.. _p-region-exact:

Exact methods
-------------

[DCM2011]_ describe three different ways to translate a p-regions problem into exact optimization models and call these approaches `Flow`, `Order`, and `Tree` respectively. While the objective function of these models ensures maximum homogeneity within the regions, the models' constraints ensure that the resulting regions are spatially contiguous. Implementations for all of the three approaches are available through the :class:`region.p_regions.exact.PRegionsExact` class. For detailed information on the three different methods please refer to [DCM2011]_.



.. _p-region-heu:

Heuristic methods
-----------------

While exact approaches ensure optimality, they can be rather slow in delivering the solution. That's why -- especially for clustering tasks including many areas -- it may be preferable to use an heuristic approach. Many heuristic algorithms have been designed aiming for a high probability of a good solution while keeping the run times low.

This category of algorithms includes the AZP described in [OR1995]_. One drawback of this algorithm is that it can get caught in a local optimum and thus may fail to reach the global optimum. That's why [OR1995]_ also present three more algorithms which aim to improve results. These algorithms use simulated annealing, a basic tabu queue, or a reactive tabu queue. You can find the implementations in the :mod:`region.p_regions.azp` module. For detailed information on the four different algorithms please refer to [OR1995]_.

