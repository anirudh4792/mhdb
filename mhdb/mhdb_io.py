#!/usr/bin/env python
"""
Functions using python-arango to input and output to an ArangoDB database.

Authors:
    - Arno Klein, 2017  (arno@childmind.org)  http://binarybottle.com

Copyright 2017, Child Mind Institute (http://childmind.org), Apache v2.0 License

"""


def dataframe2tree(db, df, nlevels, name='graph', overwrite_graph=True):
    """
    Create ArangoDB hierarchical graph from a pandas dataframe.

    Parameters
    ----------
    db : python-arango-initialized ArangoDB database
        ArangoDB database
    df : pandas dataframe
        columns contain hierarchical information
    nlevels : integer
        number of levels to hierarchy (rest included in node document)
    overwrite_graph : Boolean
        overwrite graph?

    Returns
    -------
    tree : python-arango hierarchical graph
        ArangoDB graph

    Examples
    --------
    >>> from mhdb_io import dataframe2tree  # doctest: +SKIP

    """
    import re


    # --------------------------------------------------------------------------
    # Overwrite/access graph
    # --------------------------------------------------------------------------
    if overwrite_graph:
        try:
            db.delete_graph(name)
        except:
            pass
    try:
        tree = db.create_graph(name)
    except:
        tree = db.graph(name)

    # --------------------------------------------------------------------------
    # Create vertex collections from unique entries in first nlevel columns
    # --------------------------------------------------------------------------
    column_names = df.columns
    columns = df.transpose()
    pattern = re.compile('[\W_]+', re.UNICODE)
    node_sets = []
    for level in range(nlevels):
        unique_column = columns.iloc[level].unique()
        unique_column = [x for x in unique_column if str(x) != 'nan']
        column_name = column_names[level]
        node_set_name = pattern.sub('', column_name)
        node_sets.append(node_set_name)
        if overwrite_graph:
            try:
                db.delete_collection(node_set_name)
            except:
                pass
        try:
            nodes = tree.create_vertex_collection(node_set_name)
            for element in unique_column:
                nodes.insert({'_id': '{0}/{1}'.
                             format(node_set_name,
                                    pattern.sub('', element)),
                              '_key': pattern.sub('', element),
                              'name': element})
        except:
            nodes = tree.vertex_collection(node_set_name)

    # --------------------------------------------------------------------------
    # Create edge collections
    # --------------------------------------------------------------------------
    edge_set_name = '{0}_to_{1}'.format(node_sets[0],
                                        node_sets[nlevels - 1])
    if overwrite_graph:
        try:
            tree.delete_edge_definition(edge_set_name)  #, purge=True)
        except:
            pass
    try:
        tree.create_edge_definition(edge_set_name,
                                    from_collections=node_sets[0 : nlevels - 2],
                                    to_collections=node_sets[1 : nlevels - 1])
        edge_set = db.collection(edge_set_name)
    except:
        edge_set = db.collection(edge_set_name)

    # --------------------------------------------------------------------------
    # Create edges
    # --------------------------------------------------------------------------
    edge_names = []
    rows = df.values
    for row in rows:
        for level_to in range(1, nlevels):
            for level_from in range(level_to):
                if str(row[level_from]) != 'nan' and \
                    str(row[level_to]) != 'nan':
                    element_from = pattern.sub('', row[level_from])
                    element_to = pattern.sub('', row[level_to])
                    edge_name = '{0}_to_{1}'.format(element_from, element_to)
                    if edge_name not in edge_names:
                        try:
                            edge_set.insert({
                                '_id': '{0}/{1}'.format(edge_set_name, edge_name),
                                '_key': edge_name,
                                '_from': '{0}/{1}'.format(node_sets[level_from],
                                                          element_from),
                                '_to': '{0}/{1}'.format(node_sets[level_to],
                                                        element_to),
                                'description': '{0} to {1}'.format(element_from,
                                                                   element_to)
                            })
                        except:
                            pass
                    edge_names.append(edge_name)

    return tree

