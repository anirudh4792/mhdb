#!/usr/bin/env python
"""
This is a program to construct boilerplate owl rdf document text.

Authors:
    - Arno Klein, 2017  (arno@childmind.org)  http://binarybottle.com

Copyright 2017, Child Mind Institute (http://childmind.org), Apache v2.0 License

"""


def convert_string_to_label(input_string):
    """
    This function removes all non-alphanumeric characters
    from a string, which is useful for creating safe URIs.

    Parameters
    ----------
    input_string : string
        input string

    Returns
    -------
    output_string : string
        output string

    """

    input_string = input_string.strip()
    input_string = input_string.replace(" ", "_")
    input_string = input_string.replace("_-_", "-")
    keep_chars = ('-', '.', '_')
    output_string = "".join(c for c in str(input_string) if c.isalnum()
                            or c in keep_chars).rstrip()

    return output_string


# def create_uri(base_uri, label):
#     """
#     This function creates a safe URI.
#
#     Parameters
#     ----------
#     base_uri : string
#         base URI
#     label : string
#         input string
#
#     Returns
#     -------
#     output_uri : string
#         output URI
#
#     """
#
#     label_safe = convert_string_to_label(label)
#     output_uri = base_uri + "#" + label_safe
#
#     return output_uri
#
#
# def write_triple(subject_string, predicate_string, owl_string,
#                  third_literal=False):
#     """
#     This function writes a triple from three URIs.
#
#     Parameters
#     ----------
#     subject_string : string
#         subject URI
#     predicate_string : string
#         predicate URI or in ['a', 'rdf:type']
#     owl_string : string
#         object URI or literal
#     third_literal : Boolean
#         is the owl_string a literal?
#
#     Returns
#     -------
#     output_triple : string
#         output triple
#
#     """
#
#     if predicate_string not in ['a', 'rdf:type']:
#         predicate_string = "<0>".format(predicate_string)
#     if not third_literal:
#         owl_string = "<0>".format(owl_string)
#
#     output_triple = "<{0}> {1} {2}".format(subject_string,
#                                            predicate_string,
#                                            owl_string)
#
#     return output_triple


def safestr(cell, exclude=[None]):
    """
    This function cleans up a string.

    Parameters
    ----------
    cell : string
        arbitrary string
    exclude : list
        exclusion list

    Returns
    -------
    cell : string or integer
    cell_safe : string [only generated if cell is a string]
        alphanumeric characters of cell string

    """
    from mhdb.owl_boilerplate import convert_string_to_label

    def is_number(s):
        try:
            float(s)
            return True
        except ValueError:
            return False

    if is_number(cell):
        return float(cell)
    else:
        cell = str(cell)
        cell = cell.strip()
        if cell not in exclude:
            cell_safe = convert_string_to_label(cell)
        else:
            cell = None
            cell_safe = None

        return cell, cell_safe


def get_cells(worksheet, index, worksheet2=None, exclude=[None]):
    """
    This function looks for the following worksheet column headers:
    "equivalentClass"
    "subClassOf"
    "propertyDomain"
    "propertyRange"
    "Definition"
    "DefinitionReference_index"

    Where "DefinitionReference_index" points to worksheet2 column headers:
    "ReferenceName"
    "ReferenceLink"

    Parameters
    ----------
    worksheet : pandas dataframe
        worksheet with column headers
    index : integer
        worksheet row index
    worksheet2 : pandas dataframe
        second worksheet with definition reference information
    exclude : list
        exclusion list

    Returns
    -------
    equivalent_class_uri : string
        equivalentClass URI
    subclassof_uri : string
        subClassOf URI
    property_domain : string
        property domain
    property_range : string
        property range
    definition : string
        definition string
    definition_source_name : string
        definition source name
    definition_source_uri : string
        definition source URI

    """
    import pandas as pd

    from mhdb.owl_boilerplate import safestr

    # equivalentClass and subClassOf:
    try:
        equivalent_class_uri, f = safestr(worksheet.equivalentClass[index],
                                          exclude)
    except:
        equivalent_class_uri = None
    try:
        subclassof_uri, f = safestr(worksheet.subClassOf[index], exclude)
    except:
        subclassof_uri = None

    # Property domain and range:
    try:
        property_domain, f = safestr(worksheet.propertyDomain[index], exclude)
    except:
        property_domain = None
    try:
        property_range, f = safestr(worksheet.propertyRange[index], exclude)
    except:
        property_range = None

    # Definition:
    try:
        definition, f = safestr(worksheet.Definition[index], exclude)
    except:
        definition = None

    # Definition source and link:
    definition_source_name = None
    definition_source_uri = None
    if worksheet2 is not None:
        try:
            iref, f = safestr(worksheet.DefinitionReference_index[index], exclude)
            if iref not in exclude:
                index2 = pd.Index(worksheet2['index']).get_loc(iref)
                try:
                    definition_source_name, foo = safestr(
                        worksheet2.ReferenceName[index2], exclude)
                except:
                    definition_source_name = None
                try:
                    definition_source_uri, foo = safestr(
                        worksheet2.ReferenceLink[index2], exclude)
                except:
                    definition_source_uri = None
        except:
            pass

    return equivalent_class_uri, subclassof_uri, \
           property_domain, property_range, \
           definition, definition_source_name, definition_source_uri


def print_header(base_uri, version, label, comment):
    """
    This function prints out the beginning of an owl file.

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

    Returns
    -------
    header : string
        owl header

    """

    header = """
@prefix : <{0}#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix xml: <http://www.w3.org/XML/1998/namespace> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@base <{0}> .

<{0}> rdf:type owl:Ontology ;
    owl:versionIRI <{0}/{1}> ;
    owl:versionInfo "{1}"^^rdfs:Literal ;
    rdfs:label "{2}"^^rdfs:Literal ;
    rdfs:comment "{3}"^^rdfs:Literal .

""".format(base_uri, version, label, comment)

    return header


def print_subheader(object_type):
    return """
#################################################################
#    {0}
#################################################################
""".format(object_type)


def build_owl_string(uri_stem, owl_type, label, comment=None,
                     index=None, worksheet=None, worksheet2=None,
                     equivalent_class_uri=None, subclassof_uri=None,
                     property_domain=None, property_range=None,
                     exclude=[None]):
    """

    Parameters
    ----------
    uri_stem : string
        class URI stem
    owl_type : string
        owl type, such as:
        'Class',
        'ObjectProperty',
        'DatatypeProperty',
        'FunctionalProperty'
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

    Returns
    -------
    owl_string : string
        owl class string

    """
    from mhdb.owl_boilerplate import get_cells

    # Get worksheet contents:
    class_uri, subclass_uri, prop_domain, prop_range, \
    definition, definition_source, definition_uri = get_cells(
        worksheet, index, worksheet2, exclude)

    if comment in exclude:
        comment = definition

    # If equivalent_class_uri or subclassof_uri not provided,
    # get from worksheet:
    if equivalent_class_uri in exclude:
        equivalent_class_uri = class_uri
    if subclassof_uri in exclude:
        subclassof_uri = subclass_uri

    # If property_domain or property_range not provided,
    # get from worksheet:
    if property_domain in exclude:
        property_domain = prop_domain
    if property_range in exclude:
        property_range = prop_range

    owl_string = """
### {0}
:{1} rdf:type owl:{2} """.format(label, uri_stem, owl_type)

    label = str(label)
    if label not in exclude:
        owl_string += """;
            rdfs:label "{0}"^^rdfs:Literal """.format(label)

    if comment not in exclude:
        owl_string += """;
            rdfs:comment "{0} [from: {1}]"^^rdfs:Literal """.\
            format(definition, definition_source)

    if definition_uri not in exclude:
        owl_string += """;
            rdfs:isDefinedBy "{0}"^^rdfs:Literal """.format(definition_uri)

    equivalent_class_uri = str(equivalent_class_uri)
    if equivalent_class_uri not in exclude:
        owl_string += """;
            owl:equivalentClass [ rdf:type owl:Restriction ;
                                  owl:onProperty <{0}>
                                ] """.format(equivalent_class_uri)

    subclassof_uri = str(subclassof_uri)
    if subclassof_uri not in exclude:
        if not subclassof_uri.startswith(':'):
            subclassof_uri = "<{0}>".format(subclassof_uri)
        owl_string += """;
            rdfs:subClassOf {0} """.format(subclassof_uri)

    if property_domain not in exclude:
        owl_string += """;
     rdfs:domain :{0} """.format(property_domain)

    if property_range not in exclude:
        owl_string += """;
     rdfs:range :{0} """.format(property_range)

    owl_string += """.
"""

    return owl_string


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

