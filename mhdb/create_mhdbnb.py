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


def main():
    STATEFILE = download_google_sheet(
        "data/neutralstates.xlsx",
        "1REHmDXldCZ_L403Zq0N0LdhwNNEAXEIJHcNHzOIjnSQ"
    )
    stateoutfile = os.path.join(os.getcwd(), 'mhdb/mhdb_states.ttl')
    base_uri = "http://www.purl.org/mentalhealth/neutralstates"
    # --------------------------------------------------------------------------
    # Import spreadsheet
    # --------------------------------------------------------------------------
    xls = pd.ExcelFile(STATEFILE)
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

    rdf_string = ""

    for index, label in enumerate(
        Neutral_Behaviors["neutral behaviour 1"].dropna()
    ):
        try:
            rdf_string = "{0}{1}{2}".format(
                rdf_string,
                build_rdf(
                    uri_stem="mhdbnb:{0}".format(
                        convert_string_to_label(label)
                    ),
                    rdf_type='owl:Class',
                    label=label.replace("\n", " "),
                    comment=None,
                    index=index,
                    worksheet=Neutral_Behaviors,
                    worksheet2=Neutral_Behaviors,
                    equivalent_class_uri=None,
                    subclassof_uri=None,
                    property_domain=None,
                    property_range=None,
                    exclude=X
                ),
                build_rdf(
                    uri_stem="mhdb:{0}".format(
                        convert_string_to_label(
                            Neutral_Behaviors.symptom[index].strip("\n")
                        )
                    ),
                    rdf_type=None,
                    label=None,
                    comment=None,
                    index=index,
                    worksheet=Neutral_Behaviors,
                    worksheet2=Neutral_Behaviors,
                    equivalent_class_uri=None,
                    subclassof_uri=None,
                    property_domain=None,
                    property_range=None,
                    exclude=X
                )
            )
        except:
            print(index, label)

    with open(stateoutfile, 'w') as fid:
        fid.write(header_string)
        fid.write(rdf_string)

if __name__ == "__main__":
    main()
