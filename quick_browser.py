from flask import Flask, render_template, request
import os
import pandas as pd
import rdflib

app = Flask(__name__)


def get_graph():
    """
    function to get the data to query
    
    Parameters
    ----------
    None
    
    Returns
    -------
    g : rdflib graph
        rdflib graph
    """
    g = rdflib.Graph()
    g.parse("mhdb/mhdb.ttl", format='ttl')
    g.parse(location=
            ("http://data.bioontology.org/ontologies/MESH/download?"
             "apikey=cf2fc1a7-fd1f-48bd-aa9e-e56335ba7235&"
             "format=xml"
            ), format='ttl'
           )
    return(g)

def run_query(q, g=get_graph()):
    """
    function to run a pre-defined query from a file saved in the "queries"
    subdirectory
    
    Parameter
    ---------
    q : string
        filename of the SPARQL query to run
        
    g : rdflib graph, optional
        rdflib graph, default=get_graph()
    
    Returns
    -------
    options : SPARQLResult
        rdflib SPARQL result from running said query
    """
    with open(os.path.join("queries", q), "r") as op_f:
        op_q = op_f.read()
    return(g.query(op_q))
    
    
def labeled_options(sparql_result, column_names):
    """
    function to run a pre-defined query from a file saved in the "queries"
    subdirectory
    
    Parameter
    ---------
    sparql_result : string
        rdflib SPARQL result
        
    column_names : list
        list of strings for naming columns in output DataFrame, optionally as
        2-tuples of ('name', datatype)
    
    Returns
    -------
    options : DataFrame
        DataFrame with given column names
    """
    options = []
    for row in sparql_result:
        options.append([str(r) if hasattr(column_names[i],
                       '__iter__') else r for i, r in enumerate(row)])
    cnames = [c[0] if hasattr(c, '__iter__') else c for c in column_names]
    return(pd.DataFrame(options, columns=cnames))


@app.route('/')
def main():
    g = get_graph()
    options = labeled_options(
               run_query("top_level_disorder.rq", g), [('label', str), 'iri']
              )
    return(
           render_template('quick_browser.html',
                           option_list=options
                          )
          )