import sys
from pathlib import Path

STUDY = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(STUDY / "harness"))
sys.path.insert(0, str(STUDY / "witness"))
