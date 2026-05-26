# AI-ImRs
This repository contains materials for a **“A Randomized Controlled Pilot Study on AI-Based Imagery Rescripting for Childhood Criticism Memories”**.

The project investigates whether generative AI can support the preparation of personalized therapeutic scripts for **Imagery Rescripting (ImRs)**. Participants recall autobiographical memories of childhood parental criticism and neutral events and describe them in the questionnaire. These descriptions are used to generate personalized scripts with a large language model, which are then reviewed by trained experimenters and tested using model-as-a-judge appproach. Then, scripts are generated using Elevenlabs voice cloning technology (to create real-life intervention, using therapists' voice) and used in a laboratory procedure, measuring subjective emotional responses and skin conductance.

# Aim

# Technology
Python, chatGPT-OSS, Elevenlabs API

# TODO
Upload created code
Describe thoroughly project
Add Cost-Effectiveness analysis

## Screening

This repository contains a Python script for filtering screening data from the study.The script prepares screening datasets for recruitment and study management. It reads exported Excel files from the screening questionnaire, applies inclusion and exclusion criteria, assigns anonymous participant codes, and creates separate files for research data and contact data.

The main workflow is:

1. Load screening responses from an Excel file.
2. Convert questionnaire responses to numeric values.
3. Compute screening indicators, including:
   - summed GAD-7 score,
   - mean PTSD screening score,
   - TAPS-based substance-use indicators.
4. Apply eligibility filters.
5. Split participants by GAD-7 threshold:
   - `GAD7_sum >= 8` for the main study sample,
   - `GAD7_sum < 8` for a lower-anxiety auxiliary/comparison sample.
6. Assign anonymous participant codes, such as `C001` or `H001`.
7. Export:
   - a full filtered dataset,
   - a contact-only file containing participant code, e-mail, and phone number.
  
  
