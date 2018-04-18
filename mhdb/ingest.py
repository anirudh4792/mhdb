#!/usr/bin/env python3
"""
This script contains specific functions to interpret a specific set of
spreadsheets

Authors:
    - Jon Clucas, 2017 – 2018 (jon.clucas@childmind.org)
    - Anirudh Krishnakumar, 2017 – 2018

Copyright 2018, Child Mind Institute (http://childmind.org), Apache v2.0 License

"""
try:
    from mhdb.spreadsheet_io import download_google_sheet, return_string
    from mhdb.write_ttl import check_iri, language_string
except:
    from mhdb.mhdb.spreadsheet_io import download_google_sheet, return_string
    from mhdb.mhdb.write_ttl import check_iri, language_string
import pandas as pd


def add_if(subject, predicate, object, statements={}):
    """
    Function to add an object and predicate to a dictionary, checking for that
    predicate first.

    Parameters
    ----------
    subject: string
        Turtle-formatted IRI

    predicate: string
        Turtle-formatted IRI

    object: string
        Turtle-formatted IRI

    statements: dictionary
        key: string
            RDF subject
        value: dictionary
            key: string
                RDF predicate
            value: {string}
                set of RDF objects

    Return
    ------
    statements: dictionary
        key: string
            RDF subject
        value: dictionary
            key: string
                RDF predicate
            value: {string}
                set of RDF objects

    Example
    -------
    >>> print(add_if(":goose", ":chases", ":it"))
    {':goose': {':chases': {':it'}}}
    """
    if subject not in statements:
        statements[subject] = {}
    if predicate not in statements[subject]:
        statements[subject][predicate] = {
            object
        }
    else:
        statements[subject][predicate].add(
            object
        )
    return(statements)


def audience_statements(statements={}):
    """
    Function to generate PeopleAudience subClasses.

    Parameter
    ---------
    statements: dictionary
        key: string
            RDF subject
        value: dictionary
            key: string
                RDF predicate
            value: {string}
                set of RDF objects

    Returns
    -------
    statements: dictionary
        key: string
            RDF subject
        value: dictionary
            key: string
                RDF predicate
            value: {string}
                set of RDF objects

    Example
    -------
    >>> print(
    ...     audience_statements()["mhdb:MaleAudience"]["rdfs:subClassOf"]
    ... )
    {'schema:PeopleAudience'}
    """
    for gendered_audience in {
        "Male",
        "Female"
    }:
        gendered_iri = check_iri(
            "".join([
                    gendered_audience,
                    "Audience"
            ])
        )
        schema_gender = "schema:{0}".format(
            gendered_audience
        )
        g_statements = {
            "rdfs:subClassOf": {
                "schema:PeopleAudience"
            },
            "rdfs:label": {
                 language_string(
                    " ".join([
                            gendered_audience,
                            "Audience"
                    ])
                )
            },
            "schema:requiredGender": {
                schema_gender
            }
        }
        if gendered_iri not in statements:
            statements[gendered_iri] = g_statements
        else:
            statements[gendered_iri] = {
                **statements[gendered_iri],
                **g_statements
            }
    return(statements)


def BehaviorSheet1(
    behavior_xls,
    mentalhealth_xls=None,
    sign_or_symptom=None,
    statements={}
):
    '''
    Function to ingest 1sQp63K5nGrYSgK2ZvsTfTDmlM4W5_eFHfy6Ckoi7yP4 Sheet1

    Parameters
    ----------
    sheet: spreadsheet workbook
        1sQp63K5nGrYSgK2ZvsTfTDmlM4W5_eFHfy6Ckoi7yP4

    mentalhealth_xls: spreadsheet workbook, optional
        1MfW9yDw7e8MLlWWSBBXQAC2Q4SDiFiMMb7mRtr7y97Q

    statements:  dictionary
        key: string
            RDF subject
        value: dictionary
            key: string
                RDF predicate
            value: {string}
                set of RDF objects

    Returns
    -------
    statements: dictionary
        key: string
            RDF subject
        value: dictionary
            key: string
                RDF predicate
            value: {string}
                set of RDF objects

    Example
    -------
    >>> try:
    ...     from mhdb.spreadsheet_io import download_google_sheet
    ...     from mhdb.write_ttl import turtle_from_dict
    ... except:
    ...     from mhdb.mhdb.spreadsheet_io import download_google_sheet
    ...     from mhdb.mhdb.write_ttl import turtle_from_dict
    >>> import os
    >>> import pandas as pd
    >>> try:
    ...     behaviorFILE = download_google_sheet(
    ...         'data/separating.xlsx',
    ...         "1sQp63K5nGrYSgK2ZvsTfTDmlM4W5_eFHfy6Ckoi7yP4"
    ...     )
    ... except:
    ...     behaviorFILE = 'data/separating.xlsx'
    >>> behavior_xls = pd.ExcelFile(behaviorFILE)
    >>> statements = BehaviorSheet1(
    ...     behavior_xls
    ... )
    >>> print(turtle_from_dict({
    ...     statement: statements[
    ...         statement
    ...     ] for statement in statements if statement == "mhdb:despair"
    ... }).split("\\n\\t")[0])
    mhdb:despair rdfs:label """despair"""@en ;
    '''
    sheet = behavior_xls.parse("Sheet1")
    gender = behavior_xls.parse("gender")
    statements = audience_statements(statements)

    if not mentalhealth_xls:
        try:
            mentalhealthFILE = download_google_sheet(
                'data/mentalhealth.xlsx',
                "1MfW9yDw7e8MLlWWSBBXQAC2Q4SDiFiMMb7mRtr7y97Q"
            )
        except:
            mentalhealthFILE = 'data/mentalhealth.xlsx'
        mentalhealth_xls = pd.ExcelFile(mentalhealthFILE)

    mh_reference = mentalhealth_xls.parse("Reference")

    for row in sheet.iterrows():
        sign_or_symptom = "health-lifesci:MedicalSign" if (row[1][
            "sign_or_symptom_index"
        ]) == 1 else "health-lifesci:MedicalSymptom" if (row[1][
            "sign_or_symptom_index"
        ] == 2) else "health-lifesci:MedicalSignOrSymptom"

        source = mh_reference[
            mh_reference["index"] == row[1][
                "reference_index (refer to reference in our master spreadsheet."
                " 8=dsm, 84=us)"
            ]
        ]["ReferenceLink"].values[0]
        source = None if isinstance(
            source,
            float
        ) else check_iri(source)

        symptom_label = language_string(row[1]["symptom"])

        symptom_iri = check_iri(row[1]["symptom"])

        audience_gender = gender[
            gender["index"] == row[1]["gender_index"]
        ]["gender"]

        audience_gender = None if not audience_gender.size else \
        audience_gender.values[
            0
        ]

        for predicates in [
            ("rdfs:label", symptom_label),
            ("rdfs:subClassOf", sign_or_symptom),
            ("dcterms:source", source)
        ]:
            statements = add_if(
                symptom_iri,
                predicates[0],
                predicates[1],
                statements
            )

        if audience_gender:
            for prop in [
                "schema:audience",
                "schema:epidemiology"
            ]:
                statements = add_if(
                    symptom_iri,
                    prop,
                    audience_gender,
                    statements
                )

    return(statements)


def disorder_iri(
        index,
        mentalhealth_xls=None,
        pre_specifiers_indices=[
            6,
            7,
            24,
            25,
            26
        ],
        post_specifiers_indices=[
            27,
            28,
            56,
            78
        ]
    ):
    """
    Function to figure out IRIs for disorders based on
    mentalhealth.xls::Disorder

    Parameters
    ----------
    index: int
        key to lookup in Disorder table

    mentalhealth_xls: spreadsheet workbook, optional
        1MfW9yDw7e8MLlWWSBBXQAC2Q4SDiFiMMb7mRtr7y97Q

    pre_specifiers_indices: [int], optional
        list of indices of diagnostic specifiers to precede disorder names

    post_specifiers_indices: [int], optional
        list of indices of diagnostic specifiers to be preceded by disorder
        names

    Returns
    -------
    statements: dictionary
        key: string
            RDF subject
        value: dictionary
            key: string
                RDF predicate
            value: {string}
                set of RDF objects
    """
    disorder = mentalhealth_xls.parse("Disorder")
    severity = mentalhealth_xls.parse("DisorderSeverity")
    specifier = mentalhealth_xls.parse("DiagnosticSpecifier")
    criterion = mentalhealth_xls.parse("DiagnosticCriterion")
    disorderSeries = disorder[disorder["index"]==index]
    disorder_name = disorderSeries["DisorderName"]
    if disorderSeries["DiagnosticSpecifier"]:
        disorder_name = " ".join([
            specifier[
                specifier[
                    "index"
                ]==disorderSeries[
                    "DiagnosticSpecifier"
                ]
            ],
            disorder_name
        ]) if disorderSeries[
            "DiagnosticSpecifier"
        ] in pre_specifiers_indices else " ".join([
            disorder_name,
            specifier[
                specifier[
                    "index"
                ]==disorderSeries[
                    "DiagnosticSpecifier"
                ]
            ]
        ]) if disorderSeries[
            "DiagnosticSpecifier"
        ] in post_specifiers_indices else ", ".join([
            disorder_name,
            specifier[
                specifier[
                    "index"
                ]==disorderSeries[
                    "DiagnosticSpecifier"
                ]
            ]
        ])
    #TODO: criteria (inclusion, exclusion), severity
    iri = check_iri(disorder_name)
    label = language_string(disorder_name)
    statements = {iri: {"rdfs:label": [label]}}
    return(statements)


def MHealthPeople(
    technology_xls,
    statements={}
):
    '''
    Function to ingest 1cuJXT1Un7HPLYcDyHAXprH-wGS1azuUNmVQnb3dV1cY
    MHealthPeople

    Parameters
    ----------
    sheet: spreadsheet workbook
        1cuJXT1Un7HPLYcDyHAXprH-wGS1azuUNmVQnb3dV1cY

    statements: dictionary
        key: string
            RDF subject
        value: dictionary
            key: string
                RDF predicate
            value: {string}
                set of RDF objects

    Returns
    -------
    statements: dictionary
        key: string
            RDF subject
        value: dictionary
            key: string
                RDF predicate
            value: {string}
                set of RDF objects

    Example
    -------
    # TODO
    '''
    for pred in [
        ("rdfs:label", language_string("site")),
        ("rdfs:comment", language_string(
            "Site, place or location of anything."
        )),
        ("rdfs:range", "schema:Place"),
        ("rdfs:range", "dcterms:Location"),
        ("rdf:type", "rdf:Property")
    ]:
        statements = add_if(
            "mhdb:site",
            pred[0],
            pred[1],
            statements
        )

    mhealthpeople = technology_xls.parse("MHealthPeople")

    for row in mhealthpeople.iterrows():
        predicates = set()
        person_iri = check_iri(row[1]["URL"])
        person_label = language_string(
            row[1]["MHealthPeople/Labs"]
        ) if (
            (
                len(str(row[1]["MHealthPeople/Labs"]))
            ) and not (
                isinstance(
                    row[1]["MHealthPeople/Labs"],
                    float
                )
            ) and not (
                str(row[1]["MHealthPeople/Labs"]).startswith("Also")
            )
        ) else None
        person_place = check_iri(row[1]["Site"]) if (
            len(
                str(row[1]["Site"]).strip()
            ) and not (
                isinstance(
                    row[1]["Site"],
                    float
                )
            )
        ) else None

        if person_label:
            predicates.add(
                ("rdfs:label", person_label)
            )

        if person_place:
            predicates.add(
                ("mhdb:site", person_place)
            )
            statements = add_if(
                person_place,
                "rdfs:label",
                language_string(row[1]["Site"]),
                statements
            )

        if "<" in person_iri:
            predicates.add(
                ("schema:WebPage", person_iri)
            )

        if len(predicates):
            for prop in predicates:
                statements = add_if(
                    person_iri,
                    prop[0],
                    prop[1],
                    statements
                )

        for affiliate_i in range(1, 10):
            affiliate = "{0}{1}".format(
                "Affiliate",
                str(affiliate_i)
            )
            if row[1][affiliate] and len(
                str(row[1][affiliate])
            ) and not isinstance(
                row[1][affiliate],
                float
            ):
                affiliate_iri = check_iri(
                    row[1][affiliate].split("(")[1].rstrip(")")
                ) if (
                    (
                        "@" in row[1][affiliate]
                    ) or (
                        "://" in row[1][affiliate]
                    )
                ) else check_iri(", ".join([
                    " ".join(list(
                        row[1][affiliate].strip().split(
                            "("
                        )[0].split(" ")[1:])).strip(),
                    row[1][affiliate].strip().split(
                        "("
                    )[0].split(" ")[0].strip()
                ])) if "(" in row[1][affiliate] else check_iri(", ".join([
                    " ".join(list(
                        row[1][affiliate].strip().split(" ")[1:])).strip(),
                    row[1][affiliate].strip().split(" ")[0].strip()
                ]))
                affiliate_preds = {
                    (
                        property,
                        language_string(
                            row[1][affiliate].strip().split(
                                "("
                            )[0].strip() if "(" in row[1][
                                affiliate
                            ] else row[1][affiliate]
                        )
                    ) for property in ["rdfs:label", "foaf:name"]
                }
                if "(" in row[1][affiliate]:
                    if "@" in row[1][affiliate]:
                        affiliate_preds.add(
                            (
                                "schema:email",
                                check_iri(row[1][affiliate].split(
                                    "("
                                )[1].rstrip(")").strip())
                            )
                        )
                    elif "://" in row[1][affiliate]:
                        affiliate_webpage = row[1][affiliate].split(
                            "("
                        )[1].rstrip(")").strip()
                        affiliate_preds.add(
                            (
                                "schema:WebPage",
                                check_iri(row[1][affiliate].split(
                                    "("
                                )[1].rstrip(")").strip())
                            )
                        )
                    elif "lab pup" in row[1][affiliate]:
                        affiliate_preds.add(
                            (
                                "rdfs:comment",
                                language_string("lab pup")
                            )
                        )
                    else:
                        affiliate_preds.add(
                            (
                                "mhdb:site",
                                check_iri(
                                    row[1][affiliate].split(
                                        "("
                                    )[1].rstrip(")").strip()
                                )
                            )
                        )

                for pred in affiliate_preds:
                    statements = add_if(
                        affiliate_iri,
                        pred[0],
                        pred[1],
                        statements
                    )

                statements = add_if(
                    person_iri,
                    "dcterms:contributor",
                    affiliate_iri,
                    statements
                )

    return(statements)


def object_split_lookup(
    object_indices,
    lookup_sheet,
    lookup_key_column,
    lookup_value_column,
    separator = ","
):
    """
    Function to lookup values from comma-separated key columns.

    Parameters
    ----------
    object_indices: string
        maybe-separated string of foreign keys

    lookup_sheet: DataFrame
        foreign table

    lookup_key_column: string
        foreign table key column header

    lookup_value_column: string
        foreign table value column header

    separator: string
        default=","

    Returns
    -------
    object_iris: list of strings
        list of Turtle-formatted IRIs or empty list if none

    Example
    -------
    >>> import pandas as pd
    >>> sheet = pd.DataFrame({
    ...     "index": list(range(3)),
    ...     "bird": [":duck", ":goose", ":swan"]
    ... })
    >>> print(object_split_lookup(
    ...     object_indices="0/2",
    ...     lookup_sheet=sheet,
    ...     lookup_key_column="index",
    ...     lookup_value_column="bird",
    ...     separator="/"
    ... ))
    [':duck', ':swan']
    """
    try:
        if not isinstance(
            object_indices,
            float
        ) and len(str(object_indices).strip()):
            object_indices = str(object_indices)
            if separator not in object_indices:
                object_iris = [check_iri(
                    lookup_sheet[
                        lookup_sheet[
                            lookup_key_column
                        ] == int(
                            object_indices
                        )
                    ][lookup_value_column].values[0]
                )] if lookup_sheet[
                    lookup_sheet[
                        lookup_key_column
                    ] == int(
                        object_indices
                    )
                ][lookup_value_column].values.size else None
            else:
                object_iris = [
                    int(
                        s.strip()
                    ) for s in object_indices.split(
                        separator
                    )
                ]
                object_iris = [check_iri(
                    lookup_sheet[
                        lookup_sheet[lookup_key_column] == object_i
                    ][lookup_value_column].values[0]
                ) for object_i in object_iris]
            return(object_iris)
        else:
            return([])
    except:
        print(str(object_indices))
        return([])


def Project(
    technology_xls,
    mentalhealth_xls=None,
    statements={}
):
    '''
    Function to ingest 1cuJXT1Un7HPLYcDyHAXprH-wGS1azuUNmVQnb3dV1cY Project

    Parameters
    ----------
    sheet: spreadsheet workbook
        1cuJXT1Un7HPLYcDyHAXprH-wGS1azuUNmVQnb3dV1cY

    mentalhealth_xls: spreadsheet workbook, optional
        1MfW9yDw7e8MLlWWSBBXQAC2Q4SDiFiMMb7mRtr7y97Q

    statements:  dictionary
        key: string
            RDF subject
        value: dictionary
            key: string
                RDF predicate
            value: {string}
                set of RDF objects

    Returns
    -------
    statements: dictionary
        key: string
            RDF subject
        value: dictionary
            key: string
                RDF predicate
            value: {string}
                set of RDF objects

    Example
    -------
    # TODO
    '''
    for subject in [
        "schema:Book",
        "schema:Article"
    ]:
        statemets = add_if(
            subject,
            "rdfs:subClassOf",
            "mhdb:BookOrArticle",
            statements
        )

    for pred in [
        ("rdfs:subClassOf", "schema:CreativeWork"),
        ("rdfs:subClassOf", "dcterms:BibliographicResource"),
        ("rdfs:label", language_string("Book / Article"))
    ]:
        statements = add_if(
            "mhdb:BookOrArticle",
            pred[0],
            pred[1],
            statements
        )

    for pred in [
        ("rdfs:subClassOf", "schema:CreativeWork"),
        ("rdfs:subClassOf", "schema:MedicalTest"),
        ("rdfs:label", language_string("Assessment"))
    ]:
        statements = add_if(
            "mhdb:Assessment",
            pred[0],
            pred[1],
            statements
        )

    for pred in [
        ("rdfs:subClassOf", "schema:Product"),
        ("rdfs:comment", language_string(
            "A smart electronic device (electronic device with "
            "micro-controller(s)) that can be worn on the body as implants or "
            "accessories."
        )),
        ("rdfs:isDefinedBy", check_iri(
            "https://en.wikipedia.org/wiki/Wearable_technology"
        )),
        ("rdfs:label", language_string("Wearable"))
    ]:
        statements = add_if(
            "mhdb:Wearable",
            pred[0],
            pred[1],
            statements
        )

    for pred in [
        ("rdfs:subClassOf", "schema:Game"),
        ("owl:disjointWith", "schema:VideoGame"),
        ("rdfs:label", language_string("Non-Digital Game"))
    ]:
        statements = add_if(
            "mhdb:NonDigitalGame",
            pred[0],
            pred[1],
            statements
        )

    project = technology_xls.parse("Project")
    homepage = technology_xls.parse("HomePageLink")
    mhealthpeople = technology_xls.parse("MHealthPeople")
    research_study = technology_xls.parse("ResearchStudyOnProject")

    for row in project.iterrows():
        project_iri = check_iri(row[1]["project"])
        project_label = language_string(row[1]["project"])

        homepage_iris = object_split_lookup(
            row[1]["HomePageLink_index"],
            homepage,
            "index",
            "HomePageLink",
            ","
        )

        mhealthpeople_iris = object_split_lookup(
            row[1]["MHealthPeople_index"],
            mhealthpeople,
            "index",
            "URL",
            ","
        )

        study_iris = object_split_lookup(
            row[1]["ResearchStudyOnProjectLink_index"],
            research_study,
            "index",
            "ResearchStudyOnProjectLink",
            ","
        )

        if homepage_iris and len(homepage_iris):
            for homepage_iri in homepage_iris:
                for prop in [
                    ("schema:about", project_iri),
                    ("rdf:type", "schema:WebPage")
                ]:
                    statements = add_if(
                        homepage_iri,
                        prop[0],
                        prop[1],
                        statements
                    )

        if mhealthpeople_iris and len(mhealthpeople_iris):
            for mhealthpeople_iri in mhealthpeople_iris:
                for prop in [
                    ("dcterms:contributor", mhealthpeople_iri)
                ]:
                    statements = add_if(
                        project_iri,
                        prop[0],
                        prop[1],
                        statements
                    )

        if study_iris and len(study_iris):
            for study_iri in study_iris:
                for prop in [
                    ("schema:about", project_iri),
                    ("rdf:type", "schema:ScholarlyArticle")
                ]:
                    statements = add_if(
                        study_iri,
                        prop[0],
                        prop[1],
                        statements
                    )

        for prop in [
            ("rdfs:label", project_label),
            ("rdfs:subClassOf", "schema:Product")
        ]:
            statemets = add_if(
                project_iri,
                prop[0],
                prop[1],
                statements
            )

    return(statements)


def technology(
    technology_xls,
    mentalhealth_xls=None,
    statements={}
):
    '''
    Function to ingest 1cuJXT1Un7HPLYcDyHAXprH-wGS1azuUNmVQnb3dV1cY workbook

    Parameters
    ----------
    sheet: spreadsheet workbook
        1cuJXT1Un7HPLYcDyHAXprH-wGS1azuUNmVQnb3dV1cY

    mentalhealth_xls: spreadsheet workbook, optional
        1MfW9yDw7e8MLlWWSBBXQAC2Q4SDiFiMMb7mRtr7y97Q

    statements:  dictionary
        key: string
            RDF subject
        value: dictionary
            key: string
                RDF predicate
            value: {string}
                set of RDF objects

    Returns
    -------
    statements: dictionary
        key: string
            RDF subject
        value: dictionary
            key: string
                RDF predicate
            value: {string}
                set of RDF objects

    Example
    -------
    # TODO
    '''
    return(
        Project(
            technology_xls,
            mentalhealth_xls,
            MHealthPeople(
                technology_xls,
                statements
            )
        )
    )
