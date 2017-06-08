#!/usr/bin/env python
"""
This is a program to construct boilerplate owl rdf document text.

Authors:
    - Arno Klein, 2017  (arno@childmind.org)  http://binarybottle.com

Copyright 2017, Child Mind Institute (http://childmind.org), Apache v2.0 License

"""


def convert_string_to_label(input_string):
    """
    Remove all non-alphanumeric characters from a string.

    Parameters
    ----------
    input_string : string
        input string

    Returns
    -------
    output_string : string
        output string

    """

    if input_string and isinstance(input_string, str):
        input_string = input_string.strip()
        input_string = input_string.replace(" ", "_")
        input_string = input_string.replace("_-_", "-")
        keep_chars = ('-', '.', '_')
        output_string = "".join(c for c in str(input_string) if c.isalnum()
                                or c in keep_chars).rstrip()
        return output_string
    else:
        raise Exception('"{0}" is not a string!'.format(input_string))

# def create_uri(base_uri, label):
#     """
#     Create a safe URI.
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
#     from mhdb.owl_boilerplate import convert_string_to_label
#
#     label_safe = convert_string_to_label(label)
#     output_uri = base_uri + "#" + label_safe
#
#     return output_uri
#
#
# def write_triple(subject_string, predicate_string, object_string,
#                  third_literal=False):
#     """
#     Writes a triple from three URIs.
#
#     Parameters
#     ----------
#     subject_string : string
#         subject URI
#     predicate_string : string
#         predicate URI or in ['a', 'rdf:type']
#     object_string : string
#         object URI or literal
#     third_literal : Boolean
#         is the object_string a literal?
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
#         object_string = "<0>".format(object_string)
#
#     output_triple = "<{0}> {1} {2}".format(subject_string,
#                                            predicate_string,
#                                            object_string)
#
#     return output_triple


def return_float(input_number):
    """
    Return input as a float if it's a number (or string of a number).

    Parameters
    ----------
    input_number : string or number

    Returns
    -------
    output_number : float
        raise exception if not a number or string of a number

    """
    import numpy as np

    def is_number(s):
        if s:
            if isinstance(s, float) and np.isnan(s):
                return False
            else:
                try:
                    float(s)
                    return True
                except ValueError:
                    return False
        else:
            return False

    if input_number and is_number(input_number):
        return float(input_number)
    else:
        return None


def clean_string(input_string):
    """
    Cleans up a string and creates a corresponding label.

    Parameters
    ----------
    input_string : string
        arbitrary string

    Returns
    -------
    output_string : string
        stripped input_string

    """

    if input_string and isinstance(input_string, str):
        output_string = input_string.strip()
        return output_string
    else:
        raise Exception('"{0}" is not a string!'.format(input_string))


def create_label(input_string):
    """
    This function cleans up a string and creates a corresponding label.

    Parameters
    ----------
    input_string : string
        arbitrary string
    exclude : list
        exclusion list

    Returns
    -------
    output_string : string
        stripped input_string
    label_string : string
        alphanumeric characters of input_string

    """
    from mhdb.owl_boilerplate import clean_string
    from mhdb.owl_boilerplate import convert_string_to_label

    if input_string and isinstance(input_string, str):
        output_string = clean_string(input_string)
        if output_string:
            label_string = convert_string_to_label(output_string)
            return output_string, label_string
        else:
            return '', ''
    else:
        raise Exception('"{0}" is not a string!'.format(input_string))


def get_cell(worksheet, column_label, index):
    """
    Fetch a worksheet cell given a row index and column header.

    Parameters
    ----------
    worksheet : pandas dataframe
        worksheet with column headers
    column_label : string
        worksheet column header
    index : integer
        worksheet row index

    Returns
    -------
    cell : string or number
        worksheet cell

    """

    try:
        column = getattr(worksheet, column_label)
        cell = column[index]
        return cell
    except ValueError:
        return None


def get_index2(worksheet1, column1_label, index1, worksheet2, exclude=[]):
    """
    Find the location of an 'index' value in a worksheet.

    If index1 points to a row of column1 in worksheet1, the cell contains
    an integer value. Find the corresponding row of the "index" column
    in worksheet2 with that value.

    Parameters
    ----------
    worksheet1 : pandas dataframe
        worksheet with column headers
    column1_label : string
        worksheet1 column header
    index1 : integer
        worksheet1 row index
    worksheet2 : pandas dataframe
        second worksheet with 'index' column header
    exclude : list
        exclusion list

    Returns
    -------
    index2 : integer
        worksheet2 row index

    """
    #import pandas as pd

    from mhdb.owl_boilerplate import get_cell
    from mhdb.owl_boilerplate import return_float

    cell = get_cell(worksheet1, column1_label, index1)
    if cell in exclude:
        return None
    else:
        index1to2 = return_float(cell)
        if index1to2:
            try:
                index_column = worksheet2['index']
                if any(index_column.isin([index1to2])):
                    index2 = index_column[index_column == index1to2].index[0]
                    return index2
                else:
                    return None
            except ValueError:
                raise Exception("Either the worksheet2 doesn't exist or "
                                "it doesn't have an 'index' column.")
        else:
            return None


def get_cells(worksheet, index, worksheet2=None, exclude=[]):
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
    from mhdb.owl_boilerplate import get_cell
    from mhdb.owl_boilerplate import get_index2

    # equivalentClass and subClassOf:
    try:
        equivalent_class_uri = get_cell(worksheet, 'equivalentClass', index)
    except:
        equivalent_class_uri = None
    try:
        subclassof_uri = get_cell(worksheet, 'subClassOf', index)
    except:
        subclassof_uri = None

    # Property domain and range:
    try:
        property_domain = get_cell(worksheet, 'propertyDomain', index)
    except:
        property_domain = None
    try:
        property_range = get_cell(worksheet, 'propertyRange', index)
    except:
        property_range = None

    # Definition:
    try:
        definition = get_cell(worksheet, 'Definition', index)
    except:
        definition = None

    # Definition reference and link:
    definition_ref = None
    definition_ref_uri = None
    if worksheet2 is not None:
        try:
            index2 = get_index2(worksheet, 'DefinitionReference_index', index,
                                worksheet2, exclude)
            try:
                definition_ref = get_cell(worksheet2, 'ReferenceName', index2)
            except:
                definition_ref = None
            try:
                definition_ref_uri = get_cell(worksheet2, 'ReferenceLink', index2)
            except:
                definition_ref_uri = None
        except:
            definition_ref = None
            definition_ref_uri = None

    return equivalent_class_uri, subclassof_uri, \
           property_domain, property_range, \
           definition, definition_ref, definition_ref_uri


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


def build_rdf(uri_stem, rdf_type, label, comment=None,
              index=None, worksheet=None, worksheet2=None,
              equivalent_class_uri=None, subclassof_uri=None,
              property_domain=None, property_range=None,
              exclude=[None]):
    """

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

    Returns
    -------
    rdf_string : string
        owl class string

    """
    from mhdb.owl_boilerplate import get_cells

    # Get worksheet contents:
    class_uri, subclass_uri, prop_domain, prop_range, \
    definition, definition_ref, definition_uri = get_cells(worksheet, index, 
                                                           worksheet2, exclude)
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

    rdf_string = """
### {0}
:{1} rdf:type {2} """.format(label, uri_stem, rdf_type)

    label = str(label)
    if label not in exclude:
        rdf_string += """;
            rdfs:label "{0}"^^rdfs:Literal """.format(label)

    if comment not in exclude:
        if definition_ref in exclude:
            refstring = ""
        else:
            refstring = " [from: {0}]".format(definition_ref)
        rdf_string += """;
            rdfs:comment "{0}{1}"^^rdfs:Literal """.\
            format(definition, refstring)

    if definition_uri not in exclude:
        rdf_string += """;
            rdfs:isDefinedBy "{0}"^^rdfs:Literal """.format(definition_uri)

    equivalent_class_uri = str(equivalent_class_uri)
    if equivalent_class_uri not in exclude:
        rdf_string += """;
            owl:equivalentClass [ rdf:type owl:Restriction ;
                                  owl:onProperty <{0}>
                                ] """.format(equivalent_class_uri)

    subclassof_uri = str(subclassof_uri)
    if subclassof_uri not in exclude:
        if not subclassof_uri.startswith(':'):
            subclassof_uri = "<{0}>".format(subclassof_uri)
        rdf_string += """;
            rdfs:subClassOf {0} """.format(subclassof_uri)

    if property_domain not in exclude:
        rdf_string += """;
     rdfs:domain :{0} """.format(property_domain)

    if property_range not in exclude:
        rdf_string += """;
     rdfs:range :{0} """.format(property_range)

    rdf_string += """.
"""

    return rdf_string


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

