from pathlib import Path
from datetime import datetime, timezone
import requests
import pandas as pd

BASE_URL = "https://roszdravnadzor.gov.ru/opendata/7710537160-drugs_qualitycontrol"
RAW_DIR = Path("data/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)

FILES = {
    "quality_control_meta.csv": f"{BASE_URL}/meta.csv",
    "quality_control_structure.csv": f"{BASE_URL}/structure-20171120.csv",
    "quality_control_data.csv": f"{BASE_URL}/data-20261011-structure-20171120.csv",
}

def download_file(name: str, url: str) -> Path:
    print(f"Downloading: {name}")
    response = requests.get(url, timeout=120)
    response.raise_for_status()

    path = RAW_DIR / name
    path.write_bytes(response.content)
    print(f"Saved: {path} ({len(response.content) / 1024 / 1024:.2f} MB)")
    return path

def build_manifest() -> None:
    rows = []
    for name, url in FILES.items():
        path = RAW_DIR / name
        rows.append({
            "dataset_id": "7710537160-drugs_qualitycontrol",
            "file": name,
            "source_url": url,
            "downloaded_at_utc": datetime.now(timezone.utc).isoformat(),
            "file_size_mb": round(path.stat().st_size / 1024 / 1024, 3),
        })

    manifest = pd.DataFrame(rows)
    manifest.to_csv(RAW_DIR / "source_manifest.csv", index=False)
    print("\nSource manifest:")
    print(manifest.to_string(index=False))

if __name__ == "__main__":
    for name, url in FILES.items():
        download_file(name, url)

    build_manifest()