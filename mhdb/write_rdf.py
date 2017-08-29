#!/usr/bin/env python
"""
This program contains generic functions to build an RDF text document.

Authors:
    - Arno Klein, 2017  (arno@childmind.org)  http://binarybottle.com
    - Jon Clucas, 2017 (jon.clucas@childmind.org)

Copyright 2017, Child Mind Institute (http://childmind.org), Apache v2.0 License

"""

def build_import(uri):
    """
    Build a generic RDF import substring.

    Parameters
    ----------
    uri : string
        import IRI

    Returns
    -------
    rdf_string : string
        RDF triples

    """
    if len(uri):
        return "owl:imports <{0}> ".format(uri)
    else:
        return ""


def build_prefix(prefix, uri):
    """
    Build a generic RDF prefix.

    Parameters
    ----------
    prefix : string
        class URI stem
    uri : string
        prefix IRI

    Returns
    -------
    rdf_string : string
        RDF triples

    """
    return "@prefix {0}: <{1}> .".format(prefix, uri)
    
    
def build_rdf(uri_stem, rdf_type, label, comment=None,
              index=None, worksheet=None, worksheet2=None,
              equivalent_class_uri=None, subclassof_uri=None,
              property_domain=None, property_range=None,
              exclude=[]): #, no_nan=True):
    """
    Build a generic RDF text document (with \" to escape for some strings).

    Parameters
    ----------
    uri_stem : string
        class URI stem
    rdf_type : string
        rdf:type, such as:
        ':Disorder',
        'owl:Class',
        'owl:ObjectProperty',
        'owl:DatatypeProperty',
        'owl:FunctionalProperty'
    label : string
        label
    comment : string
        comment
    index : integer
        index to row of worksheet
    worksheet : pandas dataframe
        spreadsheet worksheet containing properties
    worksheet2 : pandas dataframe
        second worksheet containing references
    equivalent_class_uri : string
        equivalentClass URI (override worksheet)
    subclassof_uri : string
        subClassOf URI (override worksheet)
    property_domain : string
        property domain (override worksheet)
    property_range : string
        property range (override worksheet)
    exclude : list
        exclusions
    #no_nan : Boolean
    #    return None if NaN?

    Returns
    -------
    rdf_string : string
        RDF triples

    """
    from mhdb.spreadsheet_io import return_string, get_cells #, get_cell

    # Get worksheet contents:
    class_uri, subclass_uri, prop_domain, prop_range, \
    definition, definition_ref, definition_uri = get_cells(worksheet, index,
                                                           worksheet2, exclude,
                                                           True)
    #try:
    #    coding_system = get_cell(worksheet, "health-lifesci:codingSystem",
    #                            index, exclude=[], no_nan=True)
    #except:
    #    coding_system = None
    # If arguments not provided, get from worksheet:
    if comment in exclude:
        comment = definition
    if equivalent_class_uri in exclude:
        equivalent_class_uri = class_uri
    if subclassof_uri in exclude:
        subclassof_uri = subclass_uri
    if property_domain in exclude:
        property_domain = prop_domain
    if property_range in exclude:
        property_range = prop_range

    if ":" in uri_stem:
        rdf_string = """
### {0}
{1} rdf:type {2} """.format(label, uri_stem, rdf_type)
    else:
        rdf_string = """
### {0}
:{1} rdf:type {2} """.format(label, uri_stem, rdf_type)

    if label not in exclude:
        rdf_string += """;
    rdfs:label "{0}"^^rdfs:Literal """.format(label)

    if comment not in exclude:
        if definition_ref in exclude:
            refstring = ""
        else:
            refstring = " [from: {0}]".format(return_string(definition_ref,
                                                            ['"'], ["'"]))
        rdf_string += """;
    rdfs:comment "{0}{1}"^^rdfs:Literal """.\
            format(return_string(comment, ['"'], ["'"]), refstring)

    if definition_uri not in exclude:
        rdf_string += """;
    rdfs:isDefinedBy "{0}"^^rdfs:Literal """.format(return_string(definition_uri))

    if equivalent_class_uri not in exclude:
        if rdf_type=='owl:ObjectProperty':
            rdf_string += """;
        owl:equivalentProperty {0} """.format(return_string(equivalent_class_uri))
        else:
            rdf_string += """;
        owl:equivalentClass {0} """.format(return_string(equivalent_class_uri))

    if subclassof_uri not in exclude:
        if not subclassof_uri.startswith(':') and "//" in subclassof_uri:
            subclassof_uri = "{0}".format(return_string(subclassof_uri))
        if rdf_type=='owl:ObjectProperty':
            rdf_string += """;
    rdfs:subPropertyOf {0} """.format(return_string(subclassof_uri))
        else:
            rdf_string += """;
    rdfs:subClassOf {0} """.format(return_string(subclassof_uri))

    if property_domain not in exclude:
        rdf_string += """;
    rdfs:domain :{0} """.format(return_string(property_domain))

    if property_range not in exclude:
        rdf_string += """;
    rdfs:range :{0} """.format(return_string(property_range))

    rdf_string += """.
"""

    return rdf_string


def print_header(base_uri, version, label, comment, prefixes, imports):
    """
    Print out the beginning of an RDF text file.

    Parameters
    ----------
    base_uri : string
        base URI
    version : string
        version
    label : string
        label
    comment : string
        comment
    prefixes : list
        list of TTL prefix strings
    imports : list
        list of TTL import substrings
    
    Returns
    -------
    header : string
        owl header

    """

    prefix = "\n".join(prefixes)
    owl_import = "".join([";\n", ";\n".join(imports), " "]) if len(
                 imports) else ""
    header = """
@prefix : <{0}#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix xml: <http://www.w3.org/XML/1998/namespace> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix dcterms: <http://dublincore.org/documents/2012/06/14/dcmi-terms/> .
{4}
@base <{0}> .

<{0}> rdf:type owl:Ontology ;
    owl:versionIRI <{0}/{1}> ;
    owl:versionInfo "{1}"^^rdfs:Literal ;
    rdfs:label "{2}"^^rdfs:Literal ;
    rdfs:comment \"\"\"{3}\"\"\"^^rdfs:Literal {5}.

""".format(base_uri, version, label, comment, prefix, owl_import)

    return header


def print_subheader(object_type):
    """
    Print out a subheader for a text file.
    """

    return """
#################################################################
#    {0}
#################################################################
""".format(object_type)


def print_general_axioms(disjoint_classes_list=[]):
    """

    Parameters
    ----------
    disjoint_classes_list : list of strings
        list of disjoint classes

    Returns
    -------
    general_axioms_string : string
        owl general axioms

    """

    general_axioms_string = ""

    if disjoint_classes_list:
        general_axioms_string += """
[ rdf:type owl:AllDisjointClasses ;
  owl:members ( :{0} """.format(disjoint_classes_list[0])

        if len(disjoint_classes_list) > 1:
            for i in range(1, len(disjoint_classes_list)):
                general_axioms_string += """
  owl:members ( :{0} """.format(disjoint_classes_list[i])

        general_axioms_string += """
              )
] .
"""

    return general_axioms_string
