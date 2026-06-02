"""
Automatic evaluation of AI-generated criticism and Imagery Rescripting scenarios
using the OpenAI API.

The script:
1. Defines diverse test cases with childhood criticism memories.
2. Generates two types of scripts:
   - criticism scenario,
   - imagery rescripting intervention.
3. Evaluates whether the generated scripts meet predefined structural criteria.
4. Saves the results to CSV and Excel.

Requirements:
    pip install openai pandas openpyxl

Before running:
    Set your OpenAI API key as an environment variable:

    Linux / macOS:
        export OPENAI_API_KEY="your_api_key_here"

    Windows PowerShell:
        setx OPENAI_API_KEY "your_api_key_here"

    Google Colab:
        import os
        os.environ["OPENAI_API_KEY"] = "your_api_key_here"
"""

import json
import time
from datetime import datetime
from pathlib import Path

import pandas as pd
from openai import OpenAI


# =========================
# Configuration
# =========================

client = OpenAI()

GENERATION_MODEL = "gpt-4.1-mini"
EVALUATION_MODEL = "gpt-4.1-mini"

OUTPUT_DIR = Path("evaluation_results")
OUTPUT_DIR.mkdir(exist_ok=True)

TODAY = datetime.today().strftime("%Y-%m-%d")


# =========================
# Prompts for generation
# =========================

CRITICISM_SYSTEM_PROMPT = """
You are a tool for generating short personalized therapeutic scenarios based on
autobiographical memories of childhood criticism.

Your task is to transform the user's memory description into a coherent scenario.
The scenario must be written in the present tense, as if the event is happening now.

The scenario should include four parts:

1. Description of the imagining person:
   - age and gender of the child,
   - appearance, clothes, and relevant accessories,
   - where the child is located.

2. Description of the environment:
   - room or place,
   - visual details,
   - sounds, smells, atmosphere,
   - other people if mentioned.

3. Description of the criticizing person:
   - who the person is,
   - appearance,
   - clothing,
   - behavior,
   - emotional expression if provided.

4. Hotspot of criticism:
   - the critical moment,
   - what the criticizing person says or does,
   - tone of voice if provided,
   - emotional reaction of the child.

Use only information provided in the input. Do not invent traumatic details.
Write in Polish.
"""
