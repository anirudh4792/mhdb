#!/usr/bin/env python3
"""
This program contains generic functions to build a Turtle (Terse RDF Triple Language) document.

Authors:
    - Arno Klein, 2017        (arno@childmind.org)  http://binarybottle.com
    - Jon Clucas, 2017 – 2018 (jon.clucas@childmind.org)

Copyright 2018, Child Mind Institute (http://childmind.org), Apache v2.0 License

"""
import os
import sys
top_dir = os.path.abspath(os.path.join(
    (__file__),
    os.pardir,
    os.pardir
))
if top_dir not in sys.path:
    sys.path.append(top_dir)
try:
    from mhdb.spreadsheet_io import convert_string_to_label
except:
    from mhdb.mhdb.spreadsheet_io import convert_string_to_label
import numpy as np


def check_iri(iri, prefixes=None):
    """
    Function to format IRIs by type
    eg, <iri> or prefix:iri
    Parameter
    ---------
    iri: string

    Returns
    -------
    iri: string
    """
    iri = str(iri)
    prefix_strings = {"","_"} if not prefixes else {
        "",
        "_",
        *[prefix[0] for prefix in prefixes]
    }
    if ":" in iri and ": " not in iri:
        if iri.endswith(":"):
            return(check_iri(iri[:-1], prefixes))
        elif iri.split(":")[0] in prefix_strings:
            return(iri)
        elif ":/" in iri:
            return("<{0}>".format(iri))
        print("unknown prefix: {0}".format(iri.split(":")[0]))
    else:
        return(mhdb_iri(iri))


def mhdb_iri(label):
    """
    Function to prepend "mhdb:" to label or string

    Parameter
    ---------
    label: string

    Returns
    -------
    iri: string
    """
    return(":".join([
        "mhdb",
        convert_string_to_label(label)
    ]))


def turtle_from_dict(ttl_dict):
    """
    Function to convert a dictionary to a Terse Triple Language string

    Parameters
    ----------
    ttl_dict: dictionary
        key: string
            RDF subject
        value: dictionary
            key: string
                RDF predicate
            value: {string}
                set of RDF objects

    Returns
    -------
    ttl_string: str
        ttl

    Example
    -------
    >>> turtle_from_dict({
    ...     "duck": {
    ...         "continues": {
    ...             "sitting"
    ...         }
    ...     },
    ...    "goose": {
    ...         "begins": {
    ...             "chasing"
    ...         }
    ...     }
    ... })
    'duck continues sitting .\\n\\ngoose begins chasing .'
    """
    x = [
        "mhdb:None",
        "mhdb:nan",
        "nan",
        np.nan,
        None
    ]
    return(
        "\n\n".join([
            "{0} {1} .".format(
                subject,
                " ;\n\t".join([
                    "{0} {1}".format(
                        predicate,
                        object
                    ) for predicate in ttl_dict[
                        subject
                    ] for object in ttl_dict[
                        subject
                    ][
                        predicate
                    ]
                ])
            ) for subject in ttl_dict
        ])
    )


def write_about_statement(subject, predicate, object, predicates):
    """
    Function to write one or more rdf statements in terse triple format.

    Parameters
    ----------
    subject: string
        subject of this statement

    predicate: string
        predicate of this statement

    object: string
        object of this statement

    predicates: iterable of 2-tuples
        predicate: string
            nth property

        object: string
            nth object

    Returns
    -------
    ttl_string: string
        Turtle string
    """
    return(
        write_ttl(
            "_:{0}".format(convert_string_to_label("_".join([
                subject,
                predicate,
                object
            ]))),
            [
                ("rdf:type", "rdf:Statement"),
                ("rdf:subject", subject),
                ("rdf:predicate", predicate),
                ("rdf:object", object),
                *predicates
            ]
        )
    )


def write_header(base_uri, version, label, comment, prefixes):
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
        list of 2-tuples of TTL prefix strings and prefix IRIs
        eg, ("owl", "http://www.w3.org/2002/07/owl#")

    Returns
    -------
    header : string
        owl header

    """

    header = write_header_prefixes(
        [("", "{0}#".format(base_uri)), *prefixes]
    )

    header = """{4}<{0}> rdf:type owl:Ontology ;
    owl:versionIRI <{0}/{1}> ;
    owl:versionInfo "{1}"^^rdfs:Literal ;
    rdfs:label "{2}"^^rdfs:Literal ;
    rdfs:comment \"\"\"{3}\"\"\"@en .

""".format(base_uri, version, label, comment, header)

    return header


def write_header_prefixes(prefixes):
    """
    Write turtle-formatted header prefix string for given list of (prefix,
    iri) tuples.

    Parameter
    ---------
    prefixes: list of 2-tuples
        each tuple is a prefix string and an iri string

    Returns
    -------
    header_prefix: string
    """
    header_prefix = ""
    for prefix in prefixes:
        header_prefix = """{0}@prefix {1}: <{2}> .\n""".format(
            header_prefix,
            prefix[0],
            prefix[1]
        )
    header_prefix = """{0}@base <{1}> .\n""".format(
        header_prefix,
        prefixes[0][1][:-1]
    )
    return(header_prefix)


def write_ttl(subject, predicates, common_statements=None):
    """
    Function to write one or more rdf statements in terse triple format.

    Parameters
    ----------
    subject: string
        subject of all triples in these statements

    predicates: iterable of 2-tuples
        statements about subject
        predicate: string
            nth property

        object: string
            nth object

    common_statements: iterable of 2-tuples, optional
        statements about all previous statements
        predicate: string
            nth property

        object: string
            nth object

    Returns
    -------
    ttl_string: string
        Turtle string
    """
    ttl_string = ""
    if common_statements:
        ttl_string = "\n\n".join([
        write_about_statement(
            subject,
            predicate[0],
            predicate[1],
            common_statements
        ) for predicate in predicates
    ])
    ttl_string = "{0}\n\n".format(ttl_string) if len(ttl_string) else ""
    ttl_string = "".join([
        ttl_string,
        "{0} {1} .".format(
            subject,
            " ;\n\t".join([
                " ".join([
                    predicate[0],
                    predicate[1]
                ]) for predicate in predicates
            ])
        )
    ])
    return(ttl_string)
