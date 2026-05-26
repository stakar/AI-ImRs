
"""
Screening data filtering for the FRBN / AI-Based Imagery Rescripting study.

This script organizes data from screening questionnaires and selects participants
who meet the basic eligibility criteria for a pilot randomized study on the use
of generative models to create personalized Imagery Rescripting (ImRs) scripts.

Study context
-------------
In the study, participants describe autobiographical memories of parental criticism
and neutral childhood events. Based on these descriptions, personalized audio
scripts are generated and later used in a laboratory procedure. The purpose of
the screening procedure is to preselect participants who fall within the required
age range, report being able to recall suitable autobiographical memories, and do
not meet exclusion criteria related to current psychotherapy, severe PTSD symptoms,
or problematic substance use.

What does the script do?
------------------------
1. Loads an Excel file containing screening responses.
2. Computes auxiliary screening variables:
   - total GAD-7 score,
   - mean PTSD screening score,
   - substance-use indicators based on TAPS.
3. Applies inclusion and exclusion criteria.
4. Splits participants into the main study sample and an auxiliary / healthy
   comparison sample based on the GAD-7 threshold.
5. Assigns anonymous participant codes.
6. Saves two datasets:
   - the full filtered dataset,
   - a separate contact file containing only participant code, e-mail, and phone number.

Personal data note
------------------
The script creates a separate contact file to make it easier to keep research data
separate from identifiable participant information. Before sharing the repository
publicly, remove all personal data and output files containing e-mail addresses,
phone numbers, or other identifiers.
"""

import os
from datetime import datetime

import pandas as pd


# Working directory containing input and output files.
# If you use the script outside Google Colab, change this path to your local project folder.
BASE_DIR = "/content/drive/MyDrive/Bielik/Projekt_bielik/Filtrowanie"


# Columns containing GAD-7 questionnaire items in the exported screening file.
# The total score is used to distinguish participants with elevated generalized
# anxiety symptoms from those below the screening threshold.
GAD7_COLS = [
    "G7S1_1", "G7S1_2", "G7S1_3", "G7S1_4", "G7S1_5",
    "G7S1_6", "G7S1_7", "G7S1_8", "G7S1_9", "G7S1_10"
]

# Columns from the PTSD symptom screening scale.
# A high score is treated as an exclusion criterion according to the screening procedure.
PTSD_COLS = [
    "PTSD_3_19", "PTSD_3_20", "PTSD_3_21", "PTSD_3_22", "PTSD_3_23",
    "PTSD_3_24", "PTSD_3_25", "PTSD_3_26", "PTSD_3_27"
]


def process_screening_file(
    input_name: str,
    output_prefix: str,
    participant_code_prefix: str,
    gad7_condition: str,
) -> None:
    """
    Process a single screening data export and save the filtered results.

    This function selects participants who meet the basic formal and clinical
    criteria for the FRBN study on AI-assisted Imagery Rescripting. In practice,
    it makes it possible to prepare two versions of the dataset: the main study
    sample with a GAD-7 score of at least 8 points, and a group of participants
    below this threshold, which may serve as an auxiliary or comparison sample.

    Parameters
    ----------
    input_name:
        Name of the input file without the `.xlsx` extension.
    output_prefix:
        Prefix used for output files, e.g. `bazaOB` or `HS_bazaOB`.
    participant_code_prefix:
        Letter added at the beginning of the anonymous participant code,
        e.g. `C` or `H`.
    gad7_condition:
        Filtering rule for GAD-7:
        - `high` selects participants with GAD7_sum >= 8,
        - `low` selects participants with GAD7_sum < 8.

    Outputs
    -------
    The function saves two Excel files:
    - `{output_prefix}_{date}.xlsx` — the full filtered dataset,
    - `kontakty_{output_prefix}_{date}.xlsx` — the contact file with participant code,
      e-mail, and phone number.
    """

    today_str = datetime.today().strftime("%Y-%m-%d")

    input_path = f"{BASE_DIR}/{input_name}.xlsx"
    main_output_path = f"{BASE_DIR}/{output_prefix}_{today_str}.xlsx"
    contact_output_path = f"{BASE_DIR}/kontakty_{output_prefix}_{today_str}.xlsx"

    # The first row of the export usually contains labels or item descriptions,
    # so the analysis starts from the second row.
    df = pd.read_excel(input_path).iloc[1:, :].copy()

    # TAPS: for alcohol use, the highest response from the relevant columns is selected
    # to create a single indicator of alcohol-use frequency.
    df["TAPS_alc"] = (
        df.loc[:, df.columns.str.contains("TAP.*[23]")]
        .astype("Float64")
        .max(axis=1)
    )

    taps_cols = ["TAPSS2", "TAPS_alc", "TAPSS4", "TAPSS5"]

    # Convert questionnaire responses to numeric values.
    # Invalid or empty responses are converted to missing values.
    for col_list in [GAD7_COLS, PTSD_COLS, taps_cols]:
        df[col_list] = df[col_list].apply(pd.to_numeric, errors="coerce")

    df["GAD7_sum"] = df[GAD7_COLS].sum(axis=1)
    df["PTSD_mean"] = df[PTSD_COLS].mean(axis=1).fillna(0)

    # Common screening criteria:
    # - age between 18 and 35 years,
    # - no current psychotherapy or psychopharmacological treatment according to form coding,
    # - no history of prolonged physical or sexual abuse according to form coding,
    # - confirmed suitability of a criticism-related autobiographical memory,
    # - PTSD and TAPS scores below exclusion thresholds.
    base_filter = (
        (df["age"] >= 18)
        & (df["age"] <= 35)
        & (df["TiOT2"] == 2)
        & (df["wtkr_3"] == 2)
        & (df["wtkr_5"] == 2)
        & (df["Criticism_validation"] == 1)
        & (df["PTSD_mean"] < 3)
        & (df["TAPS_alc"] < 3)
        & (df["TAPSS4"] < 3)
        & (df["TAPSS5"] < 3)
    )

    if gad7_condition == "high":
        gad7_filter = df["GAD7_sum"] >= 8
    elif gad7_condition == "low":
        gad7_filter = df["GAD7_sum"] < 8
    else:
        raise ValueError('gad7_condition must be either "high" or "low".')

    filtered_df = df[base_filter & gad7_filter].copy()

    # If an output file with today's date already exists, add only new participants.
    # Duplicates are identified using the e-mail address stored in the `Mail` column.
    if os.path.exists(main_output_path):
        existing_df = pd.read_excel(main_output_path)
        existing_mails = existing_df["Mail"].astype(str).str.lower().tolist()

        filtered_df = filtered_df[
            ~filtered_df["Mail"].astype(str).str.lower().isin(existing_mails)
        ]

        filtered_df = pd.concat([existing_df, filtered_df], ignore_index=True)

    # Assign ordered anonymous participant codes, e.g. C001, C002, H001.
    filtered_df = filtered_df.reset_index(drop=True)
    filtered_df["kod_osoby"] = [
        participant_code_prefix + str(i).zfill(3)
        for i in range(1, len(filtered_df) + 1)
    ]

    filtered_df.to_excel(main_output_path, index=False)

    # A separate contact file helps separate identifiable information from research data.
    contact_df = filtered_df[["kod_osoby", "Mail", "Telefon"]]
    contact_df.to_excel(contact_output_path, index=False)

    print(f"Saved {len(filtered_df)} records to: {main_output_path}")
    print(f"Saved contact file to: {contact_output_path}")


# Main study sample: participants aged 18–35 who meet the screening criteria
# and have a GAD-7 score of at least 8 points.
process_screening_file(
    input_name="Screening+-+FRBN_18+marca+2026_14.42",
    output_prefix="bazaOB",
    participant_code_prefix="C",
    gad7_condition="high",
)


# Auxiliary / comparison sample: participants who meet the common screening criteria
# but have a GAD-7 score below 8 points.
process_screening_file(
    input_name="Screening+-+FRBN_8+listopada+2025_12.07",
    output_prefix="HS_bazaOB",
    participant_code_prefix="H",
    gad7_condition="low",
)
