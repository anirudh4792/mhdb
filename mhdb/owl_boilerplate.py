#!/usr/bin/env python
"""
This is a program to construct boilerplate owl rdf document text.

Authors:
    - Arno Klein, 2017  (arno@childmind.org)  http://binarybottle.com
    - Jon Clucas, 2017 (jon.clucas@childmind.org)

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
    from mhdb.owl_boilerplate import return_string

    if input_string and isinstance(input_string, str):
        input_string = input_string.strip()
        input_string = input_string.replace(" ", "_")
        input_string = input_string.replace("_-_", "-")
        keep_chars = ('-', '_')
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


def return_none_for_nan(input_value):
    """
    Return None if input is a NaN value; otherwise, return the input.

    Parameters
    ----------
    input_value : string or number or NaN

    Returns
    -------
    value_not_nan : string or number

    """
    import numpy as np

    def is_not_nan(s):
        if s:
            if isinstance(s, float) and np.isnan(s):
                return False
            elif str(s) in ['NaN', 'nan']:
                return False
            else:
                return True
        else:
            return False

    if is_not_nan(input_value):
        return input_value
    else:
        return None


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

    if is_number(input_number):
        return float(input_number)
    else:
        return None


def return_string(input_string, replace=[], replace_with=[]):
    """
    Returns a stripped string.

    Parameters
    ----------
    input_string : string
        arbitrary string
    replace : list of strings
        strings to substitute
    replace_with : list of strings
        strings with which to substitute 'replace' strings

    Returns
    -------
    output_string : string
        stripped input_string

    """

    if input_string:
        if not isinstance(input_string, str):
            input_string = str(input_string)
        output_string = input_string.strip()
        for s in replace:
            output_string = output_string.replace(s, ' ')
        return output_string
    else:
        return ""


def create_label(input_string):
    """
    This function cleans up a string and creates a corresponding label.

    Parameters
    ----------
    input_string : string
        arbitrary string

    Returns
    -------
    output_string : string
        stripped input_string
    label_string : string
        alphanumeric characters of input_string

    """
    from mhdb.owl_boilerplate import return_string
    from mhdb.owl_boilerplate import convert_string_to_label

    if input_string:
        if isinstance(input_string, str):
            output_string = return_string(input_string,
                                          replace=['"', '\n'],
                                          replace_with=['', ''])
            if output_string:
                label_string = convert_string_to_label(output_string)
                return output_string, label_string
            else:
                return '', ''
        else:
            raise Exception('input_string is not a string!')
    else:
        raise Exception('input_string is None!')


def get_cell(worksheet, column_label, index, exclude=[], no_nan=True):
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
    exclude : list
        exclusion list
    no_nan : Boolean
        return None if NaN?

    Returns
    -------
    cell : string or number
        worksheet cell

    """
    from mhdb.owl_boilerplate import return_none_for_nan

    if column_label in worksheet.columns:
        column = worksheet[column_label]
        if index < len(column):
            cell = column[index]
            if no_nan:
                cell = return_none_for_nan(cell)
            if exclude and cell in exclude:
                return None
            else:
                return cell
        else:
            raise Exception("index={0} for column length {1}.".
                            format(index, len(column)))
    else:
        return None
        #raise Exception("column {0} not in worksheet.".format(column_label))


def get_index2(worksheet1, column1_label, index1, worksheet2):
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

    Returns
    -------
    index2 : integer
        worksheet2 row index

    """
    #import pandas as pd

    from mhdb.owl_boilerplate import get_cell
    from mhdb.owl_boilerplate import return_float

    cell = get_cell(worksheet1, column1_label, index1, exclude=[], no_nan=True)
    if cell:
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
    else:
        return None


def get_cells(worksheet, index, worksheet2=None, exclude=[], no_nan=True):
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
    no_nan : Boolean
        return None for NaN values?

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
    equivalent_class_uri = get_cell(worksheet, 'equivalentClass', index, exclude, True)
    subclassof_uri = get_cell(worksheet, 'subClassOf', index, exclude, True)

    # Property domain and range:
    property_domain = get_cell(worksheet, 'propertyDomain', index, exclude, True)
    property_range = get_cell(worksheet, 'propertyRange', index, exclude, True)

    # Definition, reference and link:
    definition = get_cell(worksheet, 'Definition', index, exclude, True)
    definition_ref = None
    definition_ref_uri = None
    if worksheet2 is not None:
        index2 = get_index2(worksheet, 'DefinitionReference_index', index,
                            worksheet2)
        if index2:
            definition_ref = get_cell(worksheet2, 'ReferenceName', index2, exclude, True)
            definition_ref_uri = get_cell(worksheet2, 'ReferenceLink', index2, exclude, True)

    return equivalent_class_uri, subclassof_uri, \
           property_domain, property_range, \
           definition, definition_ref, definition_ref_uri


def build_rdf(uri_stem, rdf_type, label, comment=None,
              index=None, worksheet=None, worksheet2=None,
              equivalent_class_uri=None, subclassof_uri=None,
              property_domain=None, property_range=None,
              exclude=[], no_nan=True, **kwargs):
    """
    Build RDF (with \" to escape for some strings).

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
    no_nan : Boolean
        return None if NaN?

    Returns
    -------
    rdf_string : string
        RDF triples

    """
    from mhdb.owl_boilerplate import return_string

    # Get worksheet contents:
    class_uri, subclass_uri, prop_domain, prop_range, \
    definition, definition_ref, definition_uri = get_cells(worksheet, index,
                                                           worksheet2, exclude,
                                                           True)
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
        rdf_string += """;
    owl:equivalentClass <{0}> """.format(return_string(equivalent_class_uri))

    if subclassof_uri not in exclude:
        if not subclassof_uri.startswith(':'):
            subclassof_uri = "<{0}>".format(return_string(subclassof_uri))
        rdf_string += """;
    rdfs:subClassOf {0} """.format(return_string(subclassof_uri))

    if property_domain not in exclude:
        rdf_string += """;
    rdfs:domain :{0} """.format(return_string(property_domain))

    if property_range not in exclude:
        rdf_string += """;
    rdfs:range :{0} """.format(return_string(property_range))

    if kwargs is not None:
        for key, value in kwargs.iteritems():
            if ":" in key:
                if ":" in value:
                    rdf_string +=""";
    {0} {1} """.format(key, value)
                else:
                    rdf_string +=""";
    {0} \"{1}\"^^rdfs:Literal """.format(key, value)
            elif ":" in value:
                rdf_string +=""";
    :{0} {1} """.format(key, value)
            else:
                rdf_string +=""";
    :{0} \"{1}\"^^rdfs:Literal """.format(key, value)

    rdf_string += """.
"""

    return rdf_string


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
@prefix dcterms: <http://dublincore.org/documents/2012/06/14/dcmi-terms/> .
@prefix health-lifesci: <http://health-lifesci.schema.org/> .
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
