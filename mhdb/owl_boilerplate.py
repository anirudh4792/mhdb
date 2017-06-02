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

    keep_chars = ('-', '.', '_')
    output_string = "".join(c for c in input_string if c.isalnum()
                            or c in keep_chars).rstrip()

    return output_string


def get_definition(Worksheet, Reference, index, exclude=[]):
    """
    This function expects that the Worksheet has a "Definition" and
    "DefinitionReference_index" column header, with the latter
    pointing to another "Reference" worksheet.

    Parameters
    ----------
    Worksheet : pandas dataframe
        worksheet containing "Definition" and
        "DefinitionReference" columns
    index : integer
        worksheet row index
    exclude : list
        exclusion list

    Returns
    -------
    definition_string : string
        output definition string

    """

    definition = Worksheet.Definition.iloc[[index][0]]
    if definition in exclude:
        definition = ''
    else:
        try:
            iref = Worksheet.DefinitionReference_index.iloc[[index][0]]
            ref = Reference.ReferenceName.iloc[[iref][0]]
            definition += " [{0}]".format(ref)
        except:
            pass


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


def print_object_properties_header():
    return """
#################################################################
#    Object Properties
#################################################################
"""


def print_object_property(property_name, label='', comment='',
                          equivalentURI='', subClassOf_uri='',
                          domain='', range='', exclude=[]):
    """
    This function prints output like::

        :expectsAnswerType rdf:type owl:ObjectProperty ;
                           rdfs:subPropertyOf :relational_property ;
                           rdf:type owl:FunctionalProperty ;
                           rdfs:domain :Question ;
                           rdfs:range :AnswerType .

    Parameters
    ----------
    property_name : string
        property name
    label : string
        label
    comment : string
        comment
    equivalentURI : string
        equivalent URI
    subClassOf_uri : string
        subClassOf URI
    domain : list of strings
        domain
    range : list of strings
        range
    exclude : list
        exclusion list

    Returns
    -------
    object_property_string : string
        owl object property

    """

    object_property_string = """
:{0} rdf:type owl:ObjectProperty ;
    rdfs:subPropertyOf :relational_property ;
    rdf:type owl:FunctionalProperty """.format(property_name)

    label = str(label)
    if label not in exclude:
        object_property_string += """;
        rdfs:label "{0}"^^rdfs:Literal """.format(label)

    comment = str(comment)
    if comment not in exclude:
        object_property_string += """;
        rdfs:comment "{0}"^^rdfs:Literal """.format(comment)

    equivalentURI = str(equivalentURI)
    if equivalentURI not in exclude:
        object_property_string += """;
        owl:equivalentClass [ rdf:type owl:Restriction ;
                              owl:onProperty <{0}>
                            ] """.format(equivalentURI)

    subClassOf_uri = str(subClassOf_uri)
    if subClassOf_uri not in exclude:
        object_property_string += """;
        rdfs:subClassOf :{0} """.format(subClassOf_uri)

    domain = str(domain)
    if domain not in exclude:
        object_property_string += """;
     rdfs:domain :{0} """.format(domain)

    range = str(range)
    if range not in exclude:
        object_property_string += """;
     rdfs:range :{0} """.format(range)

    object_property_string += """.
"""

    return object_property_string


def print_data_properties_header():
    return """
#################################################################
#    Data properties
#################################################################
"""


def print_data_property(property_name, label='', comment='',
                        equivalentURI='', subClassOf_uri='',
                        exclude=[]):
    """
    This function prints output like:

        :Answer rdf:type owl:DatatypeProperty ;
                rdfs:label "Answer"^^rdfs:Literal ;
                owl:equivalentClass [ rdf:type owl:Restriction ;
                                      owl:onProperty <http://schema.org/Answer>
                                    ] .

    Parameters
    ----------
    property_name : string
        property name
    label : string
        label
    comment : string
        comment
    equivalentURI : string
        equivalent URI
    subClassOf_uri : string
        subClassOf URI
    exclude : list
        exclusion list

    Returns
    -------
    data_property_string : string
        owl data property

    """

    data_property_string = """
:{0} rdf:type owl:DatatypeProperty """.format(property_name)

    label = str(label)
    if label not in exclude:
        data_property_string += """;
        rdfs:label "{0}"^^rdfs:Literal """.format(label)

    comment = str(comment)
    if comment not in exclude:
        data_property_string += """;
        rdfs:comment "{0}"^^rdfs:Literal """.format(comment)

    equivalentURI = str(equivalentURI)
    if equivalentURI not in exclude:
        data_property_string += """;
        owl:equivalentClass [ rdf:type owl:Restriction ;
                              owl:onProperty <{0}>
                            ] """.format(equivalentURI)

    subClassOf_uri = str(subClassOf_uri)
    if subClassOf_uri not in exclude:
        data_property_string += """;
        rdfs:subClassOf :{0} """.format(subClassOf_uri)

    data_property_string += """.
    """

    return data_property_string


def print_classes_header():
    return """
#################################################################
#    Classes
#################################################################
"""


def print_class(class_name, label='', comment='',
                equivalentURI='', subClassOf_uri='',
                exclude=[]):
    """
    This function prints output like:

    :IntellectualDisabilityIntellectualDevelopmentDisorder rdf:type owl:Class ;
            rdfs:label "Intellectual Disability (Intellectual Development Disorder)"^^rdfs:Literal ;
            rdfs:comment "None"^^rdfs:Literal ;
            owl:equivalentClass [ rdf:type owl:Restriction ;
                                  owl:onProperty <http://purl.bioontology.org/ontology/ICD10CM/F71>
                                ] ;
            rdfs:subClassOf :http://www.purl.org/mentalhealth#SchizophreniaSpectrumandOtherPsychoticDisorders .

    Parameters
    ----------
    class_name : string
        class name
    label : string
        label
    comment : string
        comment
    equivalentURI : string
        equivalent URI
    subClassOf_uri : string
        subClassOf URI
    exclude : list
        exclusion list

    Returns
    -------
    class_string : string
        owl class

    """

    class_string = """
:{0} rdf:type owl:Class """.format(class_name)

    label = str(label)
    if label not in exclude:
        class_string += """;
        rdfs:label "{0}"^^rdfs:Literal """.format(label)

    comment = str(comment)
    if comment not in exclude:
        class_string += """;
        rdfs:comment "{0}"^^rdfs:Literal """.format(comment)

    equivalentURI = str(equivalentURI)
    if equivalentURI not in exclude:
        class_string += """;
        owl:equivalentClass [ rdf:type owl:Restriction ;
                              owl:onProperty <{0}>
                            ] """.format(equivalentURI)

    subClassOf_uri = str(subClassOf_uri)
    if subClassOf_uri not in exclude:
        class_string += """;
        rdfs:subClassOf :{0} """.format(subClassOf_uri)

    class_string += """.
"""

    return class_string


def print_general_axioms_header():
    return """
#################################################################
#    General axioms
#################################################################
"""


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

