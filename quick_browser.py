from flask import Flask, render_template, request
import os
import pandas as pd
import rdflib

app = Flask(__name__)

def run_query(q):
    """
    function to run a pre-defined query from a file saved in the "queries"
    subdirectory
    
    Parameter
    ---------
    q : string
        filename of the SPARQL query to run
    
    Returns
    -------
    options : SPARQLResult
        rdflib SPARQL result from running said query
    """
    g = rdflib.Graph()
    result = g.parse("mhdb.ttl", format='n3')
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
        list of strings for naming columns in output DataFrame
    
    Returns
    -------
    options : DataFrame
        DataFrame with given column names
    """
    options = []
    for row in sparql_result:
        options.append([row[0], row[1]])
    return(pd.DataFrame(options, columns=column_names))


@app.route('/')
def main():    
    options = labeled_options(
              run_query("top_level_disorder.rq"), ['label', 'iri']
              )
    return(
        render_template('quick_browser.html',
                        option_list=options)
        )