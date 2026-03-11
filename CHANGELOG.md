# Changelog

All notable changes to p4tools are documented here.

## [0.16.1] — 2026-03-11

### Fixed
- **Savedir path mismatch**: `produce` CLI wrote clustering output to `v3.1/` but
  `ReleaseManager` reads from `P4_catalog_v3.1/`. Now uses `rm.catalog` as savedir
  for all three phases (clustering, fnotching, post-processing).
- `cluster-tile` and `cluster-obsid` standalone commands default to `clustering/`
  savedir (unchanged); only the `produce` pipeline was affected.

## [0.16.0] — 2026-03-11

### Fixed
- **Cluster validation**: Multi-stage sub-clustering (XY → radii → angles) could
  fragment clusters below `min_samples` members. The filter that was supposed to
  catch this was broken (iterated over DataFrame columns instead of rows, and only
  saw the last tile's data). Moved the `n_votes >= min_samples` filter into
  `DBScanner.cluster_image_id` where it correctly applies per-tile after concat.
- Removed broken `save_results=False` interception from `cluster_obsid`; validation
  now happens at the source inside DBScanner.
- Removed stale `min_cluster_size` parameter from `_cluster_single` CLI wrapper.

## [0.15.1] — 2026-03-11

### Fixed
- Added missing `get_L1A_paths()` function to `production.catalog`, required by
  `ReleaseManager` and the `produce` CLI command.

## [0.15.0] — 2026-03-11

### Changed
- **L1A schema**: Clustering output now writes `tile_id` instead of `image_id` for
  consistency with the published catalog and the `Fan`/`Blotch` marking classes.
- **Parallel execution**: `execute_in_parallel`, `cluster_obsid_parallel`, and
  `fnotch_obsid_parallel` now use `submit`/`as_completed` with per-item error
  handling. Individual obsid failures are logged and skipped instead of aborting
  the entire batch.

### Fixed
- `TileID.subframe` was importing `get_subframe` from `p4tools.production.io`
  (wrong module); now correctly imports from `p4tools.io`.
- Missing `import seaborn as sns` in `production.markings` caused `NameError`
  when plotting clustered markings via `cluster-tile`.

## [0.14.1] — 2026-03-11

### Fixed
- `cluster-tile`, `cluster-obsid`, and `produce` CLI commands now read the
  database path from `~/.p4tools.ini` when `--db` is not given, matching
  the behavior of `db-stats` and `random-tile`.

## [0.14.0] — 2026-03-11

### Added
- `p4 db-stats` CLI command: database summary with top tiles/obsids by marking
  count, averages, and type breakdown.
- `p4 random-tile` CLI command: pick a random tile with near-average marking count.
- Reusable helper functions in `production.io`: `resolve_dbname()`,
  `get_db_stats()`, `get_random_tile()`.

### Changed
- All CLI commands now fall back to config-based database path resolution.

### Fixed
- Removed duplicate `IMG_X_SIZE`, `IMG_Y_SIZE`, `set_subframe_size`,
  `calc_fig_size` from `05b_production.markings` (now imported from
  `p4tools.markings`).
- Removed duplicate `mars_years` dict and `define_martian_year()` from
  `03_stats` (now imported from `p4tools.io`).
- Unified `marking_id_generator` in `05_production.catalog` to eliminate
  duplicated fan/blotch ID generator logic.
- Extracted duplicated try/except/else block in `05f_production.fnotching`
  into `_apply_cut_to_tile()`.
