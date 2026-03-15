#!/usr/bin/env python3
"""Place .done sentinels in all completed pipeline stage directories.

This script walks the v3.1 pipeline products directory and writes a .done
sentinel file into every L1A/, L1B/, and L1C_cut_*/ directory that represents
a completed processing stage. This allows the per-tile skip guards in
cluster_image_id, fnotch_image_ids, and _apply_cut_to_tile to correctly
skip already-processed tiles on re-runs.

A tile's pipeline stage is considered "completed" if:
  - L1A: the directory exists (clustering_settings.json confirms the clustering
    loop iterated over this tile; absence of CSV means no surviving clusters,
    which is a valid outcome)
  - L1B: the directory exists (fnotching iterated over this tile)
  - L1C_cut_*: the directory exists (cut was applied to this tile)

Tiles that were never processed (no directory at all) are NOT affected —
they will be picked up on the next production run.

Usage:
    python place_done_sentinels.py /path/to/P4_catalog_v3.1_pipeline_products

A report of all sentinels placed is written to:
    /path/to/P4_catalog_v3.1_pipeline_products/../sentinel_placement_report.txt
"""

import sys
from pathlib import Path
from datetime import datetime


def place_sentinels(products_dir: Path):
    """Walk all tile directories and place .done sentinels."""
    products_dir = Path(products_dir)
    if not products_dir.is_dir():
        print(f"ERROR: {products_dir} is not a directory")
        sys.exit(1)

    report_path = products_dir.parent / "sentinel_placement_report.txt"
    timestamp = datetime.now().isoformat()

    stages = ["L1A", "L1B"]
    # L1C directories have the cut value in the name
    l1c_pattern = "L1C_cut_*"

    placed = {"L1A": [], "L1B": [], "L1C": []}
    skipped = {"L1A": 0, "L1B": 0, "L1C": 0}

    obsid_dirs = sorted(
        d for d in products_dir.iterdir()
        if d.is_dir() and not d.name.startswith(".")
    )
    # Filter to only obsid directories (exclude campt files etc.)
    obsid_dirs = [d for d in obsid_dirs if not d.name.endswith(".csv")
                  and not d.name.endswith(".tocampt")]

    for obsid_dir in obsid_dirs:
        tile_dirs = sorted(
            d for d in obsid_dir.iterdir()
            if d.is_dir() and d.name.startswith("APF")
        )
        for tile_dir in tile_dirs:
            # L1A
            l1a = tile_dir / "L1A"
            if l1a.is_dir():
                sentinel = l1a / ".done"
                if not sentinel.exists():
                    sentinel.touch()
                    placed["L1A"].append(
                        f"{obsid_dir.name}/{tile_dir.name}/L1A"
                    )
                else:
                    skipped["L1A"] += 1

            # L1B
            l1b = tile_dir / "L1B"
            if l1b.is_dir():
                sentinel = l1b / ".done"
                if not sentinel.exists():
                    sentinel.touch()
                    placed["L1B"].append(
                        f"{obsid_dir.name}/{tile_dir.name}/L1B"
                    )
                else:
                    skipped["L1B"] += 1

            # L1C (any L1C_cut_* directory)
            for l1c in tile_dir.glob(l1c_pattern):
                if l1c.is_dir():
                    sentinel = l1c / ".done"
                    if not sentinel.exists():
                        sentinel.touch()
                        placed["L1C"].append(
                            f"{obsid_dir.name}/{tile_dir.name}/{l1c.name}"
                        )
                    else:
                        skipped["L1C"] += 1

    # Print summary
    print(f"Sentinels placed:")
    for stage in ["L1A", "L1B", "L1C"]:
        print(f"  {stage}: {len(placed[stage])} placed, {skipped[stage]} already existed")
    print(f"Report: {report_path}")

    # Write report
    with open(report_path, "w") as f:
        f.write(f"Sentinel placement report\n")
        f.write(f"Generated: {timestamp}\n")
        f.write(f"Products dir: {products_dir}\n")
        f.write(f"\n")
        for stage in ["L1A", "L1B", "L1C"]:
            f.write(f"--- {stage}: {len(placed[stage])} sentinels placed, "
                    f"{skipped[stage]} already existed ---\n")
            for path in placed[stage]:
                f.write(f"  {path}\n")
            f.write(f"\n")

    return placed


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)
    place_sentinels(sys.argv[1])
