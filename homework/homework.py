# flake8: noqa: E501
"""Limpieza de datos de la campaña de marketing bancario."""

import glob
import os

import pandas as pd  # type: ignore


def clean_campaign_data():
    """Lee los archivos comprimidos en files/input/ y genera
    client.csv, campaign.csv y economics.csv en files/output/."""

    input_dir = "files/input"
    output_dir = "files/output"
    os.makedirs(output_dir, exist_ok=True)

    # Leer y concatenar todos los .csv.zip sin descomprimir
    frames = []
    for path in sorted(glob.glob(os.path.join(input_dir, "*.csv.zip"))):
        frames.append(pd.read_csv(path, index_col=0, compression="zip"))
    df = pd.concat(frames, ignore_index=True)

    # ----------------------------------------------------------------
    # client.csv
    # ----------------------------------------------------------------
    client = df[
        [
            "client_id",
            "age",
            "job",
            "marital",
            "education",
            "credit_default",
            "mortgage",
        ]
    ].copy()

    client["job"] = (
        client["job"]
        .str.replace(".", "", regex=False)
        .str.replace("-", "_", regex=False)
    )
    client["education"] = (
        client["education"]
        .str.replace(".", "_", regex=False)
        .replace("unknown", pd.NA)
    )
    client["credit_default"] = client["credit_default"].map(
        lambda x: 1 if x == "yes" else 0
    )
    client["mortgage"] = client["mortgage"].map(lambda x: 1 if x == "yes" else 0)

    # ----------------------------------------------------------------
    # campaign.csv
    # ----------------------------------------------------------------
    campaign = df[
        [
            "client_id",
            "number_contacts",
            "contact_duration",
            "previous_campaign_contacts",
            "previous_outcome",
            "campaign_outcome",
            "day",
            "month",
        ]
    ].copy()

    campaign["previous_outcome"] = campaign["previous_outcome"].map(
        lambda x: 1 if x == "success" else 0
    )
    campaign["campaign_outcome"] = campaign["campaign_outcome"].map(
        lambda x: 1 if x == "yes" else 0
    )

    month_map = {
        "jan": "01",
        "feb": "02",
        "mar": "03",
        "apr": "04",
        "may": "05",
        "jun": "06",
        "jul": "07",
        "aug": "08",
        "sep": "09",
        "oct": "10",
        "nov": "11",
        "dec": "12",
    }
    campaign["last_contact_date"] = (
        "2022-"
        + campaign["month"].str.lower().map(month_map)
        + "-"
        + campaign["day"].astype(str).str.zfill(2)
    )
    campaign = campaign.drop(columns=["day", "month"])

    # ----------------------------------------------------------------
    # economics.csv
    # ----------------------------------------------------------------
    economics = df[
        ["client_id", "cons_price_idx", "euribor_three_months"]
    ].copy()

    # ----------------------------------------------------------------
    # Guardar
    # ----------------------------------------------------------------
    client.to_csv(os.path.join(output_dir, "client.csv"), index=False)
    campaign.to_csv(os.path.join(output_dir, "campaign.csv"), index=False)
    economics.to_csv(os.path.join(output_dir, "economics.csv"), index=False)