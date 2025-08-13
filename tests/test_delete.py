import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))
from database.upsert import upsert_data
from database.delete_data import bulk_delete_intents
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
    items = []
    for item in test_data[:2]:
        items.append(item["intent"])
    print(f"deleting intents: {items}")
    bulk_delete_intents(items)
    print("\n--- test Data deletion complete ---")
