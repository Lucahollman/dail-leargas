'''
Script that populates sql database - WARNING: delete database + debates.csv before running for now 
'''

#Packages
import sys 
import subprocess
from tqdm import tqdm  
from pathlib import Path

script_dir = Path(__file__).parent
scripts = [
    "scraper.py",
    "debate-analysis.py",
    "debate-language-detector.py",
    "td-metadata.py",
    "debate-get-contributions.py",
    "td-overall-data.py",
    "party-data.py"
]

for script in tqdm(scripts, desc = "populating database"):
    result = subprocess.run(
        [sys.executable, script_dir / script],
        cwd=script_dir.parent,
        capture_output=True,
        text=True
    )
    print(f"\n--- {script} ---")
    print(result.stdout)
    if result.returncode != 0:
        print("ERROR:")
        print(result.stderr)
        break
    else:
        print(f"Finished {script}")