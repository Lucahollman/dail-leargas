'''
Script that populates sql database - WARNING: delete database + debates.csv before running for now 
'''

#Packages
import sys 
import subprocess
import os
from tqdm import tqdm  
from pathlib import Path

script_dir = Path(__file__).parent
scripts = [
    "api-query.py",
    "td-metadata.py",
    "debate-analysis.py",
    "debate-language-detector.py",
    "sentiment-analysis.py",
    "td-overall-data.py",
    "party-data.py",
    "word-analysis.py"
]
if os.path.exists("dail-debates.db"):
    print("Delete Database before you run script !!")
    1/0


for script in tqdm(scripts, desc = "populating database"):
    result = subprocess.run(
        [sys.executable, script_dir / script],
        cwd=script_dir.parent,
        capture_output=True,
        text=True
    )
    print(f"\n---Beginning {script} ---")
    print(result.stdout)
    if result.returncode != 0:
        print("ERROR:")
        print(result.stderr)
        break
    else:
        print(f"Finished {script}")