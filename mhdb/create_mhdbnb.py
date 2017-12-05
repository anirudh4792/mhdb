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


def gather_Rs(rb, Neutral_Behaviors):
    """
    Recursive function to gather "repetition" indicies.
    
    Parameters
    ----------
    rb: float or int or string
        "repetition_index" from xlsx
       
    Neutral_Behaviors: DataFrame
        from xlsx
        
    Returns
    -------
    all_r_indicies : list of ints
        all "repitition_index"es for the
        given "repetition_index" cell
    """
    all_r_indicies = []
    if type(rb) != float:
        rep_indicies = [
            rb
        ] if type(
            rb
        ) == int else list(eval(rb))
        all_r_indicies = {r for r in rep_indicies}
        for r in rep_indicies:
            nb = Neutral_Behaviors.loc[
                Neutral_Behaviors["index"] == r
            ]["neutral behaviour 1"].values[0]
            if nb in Rs:
                rb2 = Neutral_Behaviors.loc[
                    Neutral_Behaviors["index"] == r
                ]["repetition_index"].values[0]
                all_r_indicies = all_r_indicies | {
                    r2 for r2 in gather_Rs(
                        rb2,
                        Neutral_Behaviors
                    )
                }
        all_r_indicies = list(all_r_indicies)
    return(all_r_indicies)


def gen_questions(nb, p1=None, s1=None, dim_p1=None):
    """
    Generate the questions we can from the given prefixes and suffixes

    Parameters
    ----------
    nb: string
        "neutral behaviour"

    p1: string, optional
        prefix string

    dim_p1: string, optional
        prefix string

    s1: string, optional
        prefix string

    Returns
    -------
    qs: list of strings
        list of questions
    """
    qs = []
    nb = nb.strip()
    p1 = p1.strip() if p1 else None
    s1 = s1.strip().strip("?") if s1 else None
    dim_p1 = dim_p1.strip() if dim_p1 else None
    if p1:
        qs.append("{0} {1}?".format(p1, nb))
        if s1:
            qs.append("{0} {1} {2}?".format(p1, nb, s1))
            if dim_p1:
                qs.append("{3} {0} {1} {2}?".format(p1, nb, s1, dim_p1))
        elif dim_p1:
            qs.append("{2} {0} {1}?".format(p1, nb, dim_p1))
    elif s1:
        qs.append("{0} {1}?".format(nb, s1))
        if dim_p1:
            qs.append("{2} {0} {1}?".format(nb, s1, dim_p1))
    return(qs)


def nb_rdf(label, p1=None, s1=None, dim_p1=None):
    """
    Create neutral behaviour rdf string

    Parameters
    ----------
    label: string
        "neutral behaviour"

    p1: string, optional
        prefix string

    dim_p1: string, optional
        prefix string

    s1: string, optional
        prefix string

    Returns
    -------
    rdf: string
        rdf string
    """
    qs = gen_questions(label, p1, s1, dim_p1)
    each_q = [
        """mhdbnb:{0} rdf:type schema:Question ;
\trdfs:label \"\"\"{1}\"\"\"^^rdfs:Literal .\n\n""".format(
            convert_string_to_label(q),
            q
        ) for q in qs
    ]
    qstring = "".join([" ;\n\tschema:subjectOf mhdbnb:{0}".format(
        convert_string_to_label(q)) for q in qs
    ]) if len(qs) else ""
    return("".join([
        *each_q,
        "mhdbnb:{0} ".format(
            convert_string_to_label(label)
        ),
        "rdfs:subClassOf health-lifesci:MedicalSignOrSymptom",
        " ;\n\trdfs:label \"\"\"",
        label.replace("\n", " ").replace("\"", "\\\""),
        "\"\"\"^^rdfs:Literal",
        qstring,
        " ;\n\trdfs:comment \"\\\"neutral behaviour\\\"\"^^rdfs:Literal"
        " .\n\n"
    ]))


def rdf_nb(
    index,
    Neutral_Behaviors,
    mhdb,
    NBP,
    DimP,
    NBS,
    References,
    symptom_index=None
):
    """
    Create turtle for row in Neutral_Behaviors worksheet
    
    Parameters
    ----------
    index : int
        row number
        
    Neutral_Behaviors,
    mhdb,
    NBP,
    DimP,
    NBS,
    References: DataFrames
        from xlsx
        
    symptom_index: int
        index for symptom as indexed in
        Neutral_Behaviors worksheet
        
    Returns
    -------
    rdf_string : string
        turtle entries
    """
    rdf_string = ""
    symptom_index = index if not symptom_index else symptom_index
    label = Neutral_Behaviors.loc[
            Neutral_Behaviors["index"] == index
        ]["neutral behaviour 1"].values[0]
    labels = [label]
    for l in ["neutral behaviour 2", "neutral behaviour 3"]:
        nbl = Neutral_Behaviors.loc[
            Neutral_Behaviors["index"] == index
        ][l].values[0]
        if type(nbl) == str and nbl not in Rs:
            labels.append(nbl)
    rb = Neutral_Behaviors.loc[
        Neutral_Behaviors["index"] == index
    ]["repetition_index"].values[0]
    for rep_i in gather_Rs(rb, Neutral_Behaviors):
        rdf_string = "".join([
            rdf_string,
            rdf_nb(
                rep_i,
                Neutral_Behaviors,
                xls_mhdb,
                NBP,
                DimP,
                NBS,
                References,
                symptom_index=index
            )
        ])

    if label not in Rs:
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

        try:
            p1 = NBP.loc[NBP["index"] == int(Neutral_Behaviors.loc[
                Neutral_Behaviors["index"] == index
            ]["prefix 1"].values[0])]["neutral behaviour prefix"].values[0]
        except:
            p1 = None

        try:
            s1 = NBS.loc[NBS["index"] == int(Neutral_Behaviors.loc[
                Neutral_Behaviors["index"] == index
            ]["suffix 1"].values[0])]["neutral behaviour suffix"].values[0]
        except:
            s1 = None

        try:
            dim_p1 = DimP.loc[DimP["index"] == int(Neutral_Behaviors.loc[
                Neutral_Behaviors["index"] == index
            ]["dimensional prefix 1"].values[0])][
                "dimensional prefix"
            ].values[0]
        except:
            dim_p1 = None

        nb_labels = nb_rdf(label, p1, s1, dim_p1)

        if len(labels) > 1:
            try:
                p2 = NBP.loc[NBP["index"] == int(Neutral_Behaviors.loc[
                    Neutral_Behaviors["index"] == index
                ]["prefix 2"].values[0])][
                    "neutral behaviour prefix"
                ].values[0]
            except:
                p2 = None

            try:
                s2 = NBS.loc[NBS["index"] == int(Neutral_Behaviors.loc[
                    Neutral_Behaviors["index"] == index
                ]["suffix 2"].values[0])][
                    "neutral behaviour suffix"
                ].values[0]
            except:
                s2 = None

            try:
                dim_p2 = DimP.loc[DimP["index"] == int(
                    Neutral_Behaviors.loc[
                        Neutral_Behaviors["index"] == index
                    ]["dimensional prefix 2"].values[0]
                )][
                    "dimensional prefix"
                ].values[0]
            except:
                dim_p2 = None

            nb_labels = "".join([
                nb_labels,
                nb_rdf(labels[1], p2, s2, dim_p2)
            ])

            if len(labels) > 3:
                try:
                    p3 = NBP.loc[NBP["index"] == int(Neutral_Behaviors.loc[
                        Neutral_Behaviors["index"] == index
                    ]["prefix 3"].values[0])][
                        "neutral behaviour prefix"
                    ].values[0]
                except:
                    p3 = None

                try:
                    s3 = NBS.loc[NBS["index"] == int(Neutral_Behaviors.loc[
                        Neutral_Behaviors["index"] == index
                    ]["suffix 3"].values[0])][
                        "neutral behaviour suffix"
                    ].values[0]
                except:
                    s3 = None

                try:
                    dim_p3 = DimP.loc[DimP["index"] == int(
                        Neutral_Behaviors.loc[
                            Neutral_Behaviors["index"] == index
                        ]["dimensional prefix 3"].values[0]
                    )][
                        "dimensional prefix"
                    ].values[0]
                except:
                    dim_p3 = None

                nb_labels = "".join([
                    nb_labels,
                    nb_rdf(labels[2], p3, s3, dim_p3)
                ])

        rdf_string = "".join([
            rdf_string,
            nb_labels,
            "mhdb:{0} ".format(
                convert_string_to_label(
                    Neutral_Behaviors.loc[
                        Neutral_Behaviors["index"] == symptom_index
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
        
    return(rdf_string)


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
    Rs = ["R", "R\n", "", "\n"]

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
        rdf_string = "".join([rdf_string,
            rdf_nb(
                index,
                Neutral_Behaviors,
                mhdb,
                NBP,
                DimP,
                NBS,
                References
            )
        ])

    with open(stateoutfile, 'w') as fid:
        fid.write(header_string)
        fid.write(rdf_string)

if __name__ == "__main__":
    main()
