import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent / 'src'
sys.path.append(str(project_root))

from database.ingest import ingest_data_bulk
from database.upsert import upsert_data
import json


def load_test_data():
    file_path = "data/navigation_intents.json"
    with open(file_path, "r") as f:
        return json.load(f)

if __name__ == "__main__":
    test_data = load_test_data()
    print(f"Loaded {len(test_data)} intents from test data.")
    # Ingest bulk
    print("\n--- Ingesting data ---")
    ingest_data_bulk(test_data)
    print("\n--- test Data ingestion complete ---")