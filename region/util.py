import collections
import random

import numpy as np
import networkx as nx


def dataframe_to_dict(df, cols):
    """

    Parameters
    ----------
    df : `pandas.DataFrame` or `geopandas.GeoDataFrame`
    cols : list
        A list of strings. Each string is the name of a column of `df`.

    Returns
    -------
    result : dict
        The keys are the elements of the DataFrame's index.
        Each value is an `numpy.ndarray` holding the corresponding values in
        the columns specified by `cols`.

    """
    return dict(zip(df.index, np.array(df[cols])))


def find_sublist_containing(el, lst, index=False):
    """

    Parameters
    ----------
    el :
        The element to search for in the sublists of `lst`.
    lst : collections.Sequence
        A sequence of sequences or sets.
    index : bool, default: False
        If False (default), the subsequence or subset containing `el` is
        returned.
        If True, the index of the subsequence or subset in `lst` is returned.

    Returns
    -------
    result : collections.Sequence, collections.Set or int
        See the `index` argument for more information.
    """
    for idx, sublst in enumerate(lst):
        if el in sublst:
            return idx if index else sublst
    raise LookupError(
            "{} not found in any of the sublists of {}".format(el, lst))


def dissim_measure(v1, v2):
    """
    Parameters
    ----------
    v1 : float or ndarray
    v2 : float or ndarray

    Returns
    -------
    result : numpy.float64
        The dissimilarity between the values v1 and v2.
    """
    return np.linalg.norm(v1 - v2)


def distribute_regions_among_components(n_regions, graph):
    """

    Parameters
    ----------
    n_regions : `int`
        The overall number of regions.
    graph : `networkx.Graph`
        An undirected graph whose number of connected components is not greater
        than `n_regions`.

    Returns
    -------
    result : `dict`
        Each key (of type `networkx.Graph`) is a connected component of
        `graph`.
        Each value is an `int` defining the number of regions in the key
        component.
    """
    print("distribute_regions_among_components got a ", type(graph))
    comps = list(nx.connected_component_subgraphs(graph, copy=False))
    n_regions_to_distribute = n_regions
    result = {}
    comps_multiplied = []
    # make sure each connected component has at least one region assigned to it
    for comp in comps:
        comps_multiplied += [comp] * (len(comp)-1)
        result[comp] = 1
        n_regions_to_distribute -= 1
    # distribute the rest of the regions to random components with bigger
    # components being likely to get more regions assigned to them
    while n_regions_to_distribute > 0:
        position = random.randrange(len(comps_multiplied))
        picked_comp = comps_multiplied.pop(position)
        result[picked_comp] += 1
        n_regions_to_distribute -= 1
    return result


def make_move(area, from_idx, to_idx, region_list):
    print("  move", area,
          "  from", region_list[from_idx],
          "  to", region_list[to_idx])
    region_list[from_idx].remove(area)
    region_list[to_idx].add(area)


def objective_func(region_list, graph, attr="data"):
    return sum(dissim_measure(graph.node[list(region_list[r])[i]][attr],
                              graph.node[list(region_list[r])[j]][attr])
               for r in range(len(region_list))
               for i in range(len(region_list[r]))
               for j in range(len(region_list[r]))
               if i < j)


def generate_initial_sol(graph, n_regions):
    """

    Parameters
    ----------
    graph : networkx.Graph
    n_regions : int
        Number of regions to divide the graph into.

    Returns
    -------
    result : `dict`
        Each key (of type `networkx.Graph`) consists of the nodes of a
        connected component of `graph`. Some of the edges between the nodes are
        removed potentially rendering the nodes disconnected.
        Each value (an integer) specifies into how many connected components
        the nodes were split due to the removal of edges.
    """
    print("generate_initial_sol got a ", type(graph))
    print("step 1")
    if len(graph) > 1:
        n_regions_per_comp = distribute_regions_among_components(
                n_regions, graph)
    else:
        try:
            n_regions_per_comp = {graph[0].copy(): n_regions}
        except IndexError:
            raise ValueError("The graph argument must not be "
                             "empty.")

    # step 1: generate a random zoning system of n_regions regions
    #         from num_areas areas
    for comp, n_regions_in_comp in n_regions_per_comp.items():
        # cut edges until we have the desired number of regions in comp
        while nx.number_connected_components(comp) < n_regions_in_comp:
            num_edges = len(comp.edges())
            position = random.randrange(num_edges)
            edge_to_rm = comp.edges()[position]
            comp.remove_edge(*edge_to_rm)
    return n_regions_per_comp


def regionalized_components(initial_sol, graph):
    """

    Parameters
    ----------
    initial_sol : dict
        If `initial_sol` is a dict then the each key must be an area and each
        value must be the corresponding region-ID in the initial clustering.
    graph : networkx.Graph
        The graph with areas as nodes and links between bordering areas.

    Yields
    ------
    comp : networkx Graph
        The yielded value represents a connected component of graph but with
        links removed between regions.
    """
    graph_copy = graph.copy()
    for comp in nx.connected_component_subgraphs(graph_copy):
        # cut edges between regions
        for n1, n2 in comp.edges():
            if initial_sol[n1] != initial_sol[n2]:
                comp.remove_edge(n1, n2)
        yield comp


def region_list_to_dict(region_list):
    """

    Parameters
    ----------
    region_list : list of sets
        A list of sets. Each set consists of areas belonging to the same
        region. An example would be [{0, 1, 2, 5}, {3, 4, 6, 7, 8}].

    Returns
    -------
    result_dict : dict
        Each key is an area, each value is the corresponding region. An example
        would be {0: 0, 1: 0, 2: 0, 3: 1, 4: 1, 5: 0, 6: 1, 7: 1, 8: 1}.

    """
    result_dict = {}
    for region_idx, region in enumerate(region_list):
        for area in region:
            result_dict[area] = region_idx
    return result_dict


def dict_to_region_list(region_dict):
    """
    Inverse operation of `region_list_to_dict`.

    Parameters
    ----------
    region_dict : dict

    Returns
    -------
    region_list : list of sets

    """
    region_list = [set() for _ in range(max(region_dict.values()) + 1)]
    for area in region_dict:
        region_list[region_dict[area]].add(area)
    return region_list
