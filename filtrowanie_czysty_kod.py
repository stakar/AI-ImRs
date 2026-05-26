import os
from datetime import datetime

import pandas as pd


BASE_DIR = "/content/drive/MyDrive/Bielik/Projekt_bielik/Filtrowanie"


GAD7_COLS = [
    "G7S1_1", "G7S1_2", "G7S1_3", "G7S1_4", "G7S1_5",
    "G7S1_6", "G7S1_7", "G7S1_8", "G7S1_9", "G7S1_10"
]

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
    Filtruje dane screeningowe i zapisuje:
    1. pełną przefiltrowaną bazę,
    2. osobny plik kontaktowy z kodem osoby, mailem i telefonem.

    Parametry:
    - input_name: nazwa pliku wejściowego bez rozszerzenia .xlsx
    - output_prefix: prefiks plików wyjściowych, np. "bazaOB" albo "HS_bazaOB"
    - participant_code_prefix: prefiks kodu osoby, np. "C" albo "H"
    - gad7_condition: "high" dla GAD7_sum >= 8 albo "low" dla GAD7_sum < 8
    """

    today_str = datetime.today().strftime("%Y-%m-%d")

    input_path = f"{BASE_DIR}/{input_name}.xlsx"
    main_output_path = f"{BASE_DIR}/{output_prefix}_{today_str}.xlsx"
    contact_output_path = f"{BASE_DIR}/kontakty_{output_prefix}_{today_str}.xlsx"

    df = pd.read_excel(input_path).iloc[1:, :].copy()

    df["TAPS_alc"] = (
        df.loc[:, df.columns.str.contains("TAP.*[23]")]
        .astype("Float64")
        .max(axis=1)
    )

    taps_cols = ["TAPSS2", "TAPS_alc", "TAPSS4", "TAPSS5"]

    for col_list in [GAD7_COLS, PTSD_COLS, taps_cols]:
        df[col_list] = df[col_list].apply(pd.to_numeric, errors="coerce")

    df["GAD7_sum"] = df[GAD7_COLS].sum(axis=1)
    df["PTSD_mean"] = df[PTSD_COLS].mean(axis=1).fillna(0)

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
        raise ValueError('gad7_condition musi mieć wartość "high" albo "low".')

    filtered_df = df[base_filter & gad7_filter].copy()

    if os.path.exists(main_output_path):
        existing_df = pd.read_excel(main_output_path)
        existing_mails = existing_df["Mail"].astype(str).str.lower().tolist()

        filtered_df = filtered_df[
            ~filtered_df["Mail"].astype(str).str.lower().isin(existing_mails)
        ]

        filtered_df = pd.concat([existing_df, filtered_df], ignore_index=True)

    filtered_df = filtered_df.reset_index(drop=True)
    filtered_df["kod_osoby"] = [
        participant_code_prefix + str(i).zfill(3)
        for i in range(1, len(filtered_df) + 1)
    ]

    filtered_df.to_excel(main_output_path, index=False)

    contact_df = filtered_df[["kod_osoby", "Mail", "Telefon"]]
    contact_df.to_excel(contact_output_path, index=False)

    print(f"Zapisano {len(filtered_df)} rekordów do: {main_output_path}")
    print(f"Zapisano kontakty do: {contact_output_path}")


# Grupa z GAD7 >= 8
process_screening_file(
    input_name="Screening+-+FRBN_18+marca+2026_14.42",
    output_prefix="bazaOB",
    participant_code_prefix="C",
    gad7_condition="high",
)


# Grupa z GAD7 < 8
process_screening_file(
    input_name="Screening+-+FRBN_8+listopada+2025_12.07",
    output_prefix="HS_bazaOB",
    participant_code_prefix="H",
    gad7_condition="low",
)
