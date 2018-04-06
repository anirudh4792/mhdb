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
    from mhdb.write_ttl import check_iri
except:
    from mhdb.mhdb.spreadsheet_io import download_google_sheet, return_string
    from mhdb.mhdb.write_ttl import check_iri
import pandas as pd


def BehaviorSheet1(
    sheet,
    mentalhealth_xls=None,
    sign_or_symptom=None,
    statements={}
):
    '''
    Function to ingest 1sQp63K5nGrYSgK2ZvsTfTDmlM4W5_eFHfy6Ckoi7yP4 Sheet1

    Parameters
    ----------
    sheet: DataFrame
        parsed spreadsheet

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
    ...     behavior_xls.parse("Sheet1")
    ... )
    >>> print(turtle_from_dict({
    ...     statement: statements[
    ...         statement
    ...     ] for statement in statements if statement == "mhdb:despair"
    ... }).split("\\n\\t")[0])
    mhdb:despair rdfs:label """despair"""@en ;
    '''
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
        source = check_iri(
            mh_reference[
                mh_reference["index"] == row[1][
                    "reference_index (refer to reference in our master "
                    "spreadsheet. 8=dsm, 84=us)"
                ]
            ]["ReferenceName"].values[0]
        ) if isinstance(
            source,
            float
        ) else check_iri(source)
        symptom_label = "\"\"\"{0}\"\"\"@en".format(
            return_string(
                row[1]["symptom"],
                [
                    '"'
                ],
                [
                    "'"
                ]
            )
        )
        symptom_iri = check_iri(row[1]["symptom"])
        if symptom_iri not in statements:
            statements[symptom_iri] = {}

        if "rdfs:label" not in statements[symptom_iri]:
            statements[symptom_iri]["rdfs:label"] = {
                symptom_label
            }
        else:
            statements[symptom_iri]["rdfs:label"].add(
                symptom_label
            )

        if "rdfs:subClassOf" not in statements[symptom_iri]:
            statements[symptom_iri]["rdfs:subClassOf"] = {
                sign_or_symptom
            }
        else:
            statements[symptom_iri]["rdfs:subClassOf"].add(
                sign_or_symptom
            )

        if "dcterms:source" not in statements[symptom_iri]:
            statements[symptom_iri]["dcterms:source"] = {
                source
            }
        else:
            statements[symptom_iri]["dcterms:source"].add(
                source
            )
    return(statements)
