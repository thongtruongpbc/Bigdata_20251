import pandas as pd
import numpy as np
from datetime import datetime, timedelta, timezone

# cấu hình
N_CAMERAS = 5
ROWS_PER_CAMERA = 50

now = datetime.now(timezone.utc)

records = []

for camera_id in range(1, N_CAMERAS + 1):
    for i in range(ROWS_PER_CAMERA):
        ts = now - timedelta(minutes=5 * i)

        vehicle_count = np.random.randint(0, 100)
        is_congested = 1 if vehicle_count >= 60 else 0

        records.append(
            {
                "id_camera": camera_id,
                "timestamp": ts,
                "vehicle_count": vehicle_count,
                "is_congested": is_congested,
            }
        )

df = pd.DataFrame(records)

# đảm bảo đúng dtype cho Feast
df["id_camera"] = df["id_camera"].astype("int64")
df["vehicle_count"] = df["vehicle_count"].astype("int32")
df["is_congested"] = df["is_congested"].astype("int32")
df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)

# ghi parquet
output_path = "feature_repo/data/camera_stats.parquet"
df.to_parquet(output_path, index=False)

print(f"✅ Wrote {len(df)} rows to {output_path}")
print(df.head())
