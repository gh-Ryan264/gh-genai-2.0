import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))
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
    print("\n--- upsert data only ---")
    
    print(type(test_data))
    upsert_data(test_data)
    print("\n--- test Data upsertion complete ---")
