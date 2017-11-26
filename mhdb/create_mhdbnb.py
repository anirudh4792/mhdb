#!/usr/bin/env python3
"""
This program converts a mental health nuetral behaviors spreadsheet workbook to
an RDF turtle text document.

Authors:
    - Arno Klein, 2017  (arno@childmind.org)  http://binarybottle.com
    - Jon Clucas, 2017 (jon.clucas@childmind.org)

Copyright 2017, Child Mind Institute (http://childmind.org), Apache v2.0 License

"""
import argparse
import os
from mhdb.info import __version__ as version
import pandas as pd
from mhdb.spreadsheet_io import convert_string_to_label, create_label, \
    get_index2, get_cell, download_google_sheet
from mhdb.write_rdf import build_rdf, print_header, print_subheader


def nb_rdf(label):
    """
    Create neutral behaviour rdf string
    """
    return("".join([
        "mhdbnb:{0} ".format(
            convert_string_to_label(label)
        ),
        "rdfs:subClassOf health-lifesci:MedicalSignOrSymptom",
        " ;\n\t rdfs:label \"\"\"",
        label.replace("\n", " ").replace("\"", "\\\""),
        "\"\"\"",
        " .\n\n"
    ]))

def main():
    STATEFILE = download_google_sheet(
        "data/neutralstates.xlsx",
        "1REHmDXldCZ_L403Zq0N0LdhwNNEAXEIJHcNHzOIjnSQ"
    )
    stateoutfile = os.path.join(os.getcwd(), 'mhdb_states.ttl')
    FILE = 'data/mentalhealth.xlsx'
    download_google_sheet(
        FILE,
        "13a0w3ouXq5sFCa0fBsg9xhWx67RGJJJqLjD_Oy1c3b0"
    )
    base_uri = "http://www.purl.org/mentalhealth/neutralstates"
    # --------------------------------------------------------------------------
    # Import spreadsheet
    # --------------------------------------------------------------------------
    xls = pd.ExcelFile(STATEFILE)
    xls_mhdb = pd.ExcelFile(FILE)
    X = ['', 'nan', 'None', None]

    # --------------------------------------------------------------------------
    # Create output RDF file and print header
    # --------------------------------------------------------------------------
    label = "mental health database: neutral states"
    comment="""
    ======================================
    Mental Health Database: Neutral States
    ======================================

    This mental health database inter-relates information about mental health
    diagnoses, symptoms, assessement questionnaires, etc., and is licensed
    under the terms of the Creative Commons BY license.
    Current information can be found on the website, http://mentalhealth.tech.
    """

    header_string = print_header(
        base_uri,
        version,
        label,
        comment,
        prefixes= [
            (
                "dcterms",
                "http://dublincore.org/documents/2012/06/14/dcmi-terms/"
            ),
            ("health-lifesci", "http://health-lifesci.schema.org/"),
            ("mhdb", "http://www.purl.org/mentalhealth#"),
            ("mhdbnb", "{0}#".format(base_uri)),
            ("owl", "http://www.w3.org/2002/07/owl#"),
            ("rdfs", "http://www.w3.org/2000/01/rdf-schema#"),
            ("schema", "http://schema.org/")
        ]
    )

    Neutral_Behaviors = xls.parse("Sheet1")
    NBP = xls.parse("neutral behaviour prefix")
    DimP = xls.parse("dimensional prefix")
    NBS = xls.parse("neutral behaviour suffix")
    References = xls_mhdb.parse("Reference")

    rdf_string = ""

    for index in Neutral_Behaviors["index"].dropna():
        label = Neutral_Behaviors.loc[
            Neutral_Behaviors["index"] == index
        ]["neutral behaviour 1"].values[0]
        labels = [label]
        for l in ["neutral behaviour 2", "neutral behaviour 3"]:
            nbl = Neutral_Behaviors.loc[
                Neutral_Behaviors["index"] == index
            ][l].values[0]
            if type(nbl) == str and nbl not in ["R", "R\n"]:
                labels.append(nbl)
        if label in ["R", "R\n"]:
            pass #TODO: handle Rs
        else:
            refindex = Neutral_Behaviors.loc[
                Neutral_Behaviors["index"]==index
            ]["{0}{1}{2}".format(
                "reference_index ",
                "(refer to reference in our master spreadsheet. ",
                "8=dsm, 84=us)"
            )].values[0]
            try:
                reference = References.loc[
                    References["index"] == refindex
                ]["ReferenceLink"].values[0]
                reference = "<{0}>".format(reference) if type(
                    reference
                ) == str else "mhdb:{0}".format(
                    convert_string_to_label(
                        References.loc[
                            References["index"] == refindex
                        ]["ReferenceName"].values[0]
                    )
                )
            except:
                reference = None

            nb_labels = "".join([nb_rdf(lab) for lab in labels])

            rdf_string = "".join([
                rdf_string,
                nb_labels,
                "mhdb:{0} ".format(
                    convert_string_to_label(
                        Neutral_Behaviors.loc[
                            Neutral_Behaviors["index"] == index
                        ]["symptom"].values[0]
                    )
                ),
                " ;\n".join([
                    "rdfs:subClassOf mhdbnb:{0}".format(
                            convert_string_to_label(lab)
                    )
                 for lab in labels]),
                " ;\n\tdcterms:source {0}".format(reference) if type(
                    reference
                ) == str else "",
                " .\n\n"
                #TODO: subclasses, neutrals 2+
            ])

    with open(stateoutfile, 'w') as fid:
        fid.write(header_string)
        fid.write(rdf_string)

if __name__ == "__main__":
    main()
