import os
from pathlib import Path
from feast import FeatureStore

CURRENT_DIR = Path(__file__).parent
REPO_PATH = (CURRENT_DIR / "../feature_repo").resolve()

store = FeatureStore(repo_path=str(REPO_PATH))

def get_online_traffic_data(camera_id: str):
    try:
        feature_list = [
            "camera_stats_stream:vehicle_count",
            "camera_stats_stream:is_congested",
            "camera_stats_stream:avg_vehicle_count",
            "camera_stats_stream:max_vehicle_count",
            "camera_stats_stream:min_vehicle_count"
        ]

        entity_rows = [{"id_camera": camera_id}]

        # query Online Store (Redis)
        response = store.get_online_features(
            features=feature_list,
            entity_rows=entity_rows,
        ).to_dict(include_event_timestamps=True)

        print(f"\n🚀 [FEAST ONLINE] Data for Camera ID: {camera_id}")
        print("-" * 50)
        
        for key, value in sorted(response.items()):
            print(f"{key:40} | {value}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_id = "5d8cd542766c880017188948" 
    get_online_traffic_data(test_id)