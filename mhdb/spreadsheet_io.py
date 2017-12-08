#!/usr/bin/env python
"""
This program contains generic input/output functions
to read from a spreadsheet and return desired types/formats.

Authors:
    - Arno Klein, 2017  (arno@childmind.org)  http://binarybottle.com
    - Jon Clucas, 2017 (jon.clucas@childmind.org)

Copyright 2017, Child Mind Institute (http://childmind.org), Apache v2.0 License

"""
import os
import urllib

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
#     from mhdb.spreadsheet_io import convert_string_to_label
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
#     Write a triple from three URIs.
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


def download_google_sheet(filepath, docid):
    """
    Download latest version of a Google Sheet

    Parameters
    ----------
    filepath : string

    docid : string

    Returns
    -------
    filepath : sting
    """
    if not os.path.exists(os.path.abspath(os.path.dirname(filepath))):
        os.makedirs(os.path.abspath(os.path.dirname(filepath)))
    urllib.request.urlretrieve("{1}{0}{2}".format(
        docid,
        'https://docs.google.com/spreadsheets/d/',
        '/export?format=xlsx'
        ), filepath)
    return(filepath)

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
    Return a stripped string.

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
        input_string = "<{0}>".format(
            input_string
            ) if (
            "://" in input_string and
            not input_string.startswith("<")
            ) else input_string
        if not isinstance(input_string, str):
            input_string = str(input_string)
        output_string = input_string.strip()
        if replace:
            if len(replace) == len(replace_with):
                for i, s in enumerate(replace):
                    output_string = output_string.replace(s, replace_with[i])
                return output_string
            else:
                raise Exception("replace and replace_with should be the same length.")
        else:
            return output_string
    else:
        return ""


def create_label(input_string):
    """
    Clean up a string and create a corresponding (shortened) label.

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
    from mhdb.spreadsheet_io import return_string
    from mhdb.spreadsheet_io import convert_string_to_label

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
    from mhdb.spreadsheet_io import return_none_for_nan

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

    from mhdb.spreadsheet_io import get_cell
    from mhdb.spreadsheet_io import return_float

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
    Get cells from a worksheet with the following column headers:
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
    from mhdb.spreadsheet_io import get_cell
    from mhdb.spreadsheet_io import get_index2

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
