# Changelog

All notable changes to p4tools are documented here.

## [0.23.0] — 2026-08-13

### Added — per-tile quality (uncertainty) API
- **`stats.add_uncertainty_columns(df, *, min_votes=5, circular_ratio_limit=0.8)`**
  enriches a fan or blotch catalog (kind inferred from its columns) with four
  per-marking columns derived from the cluster standard deviations: `pos_std`
  (`hypot(x_std, y_std)`), `size_cv` (a mean relative std — `distance`/`spread`
  for fans, `radius_1`/`radius_2` for blotches), `angle_usable` (False for
  near-circular blotches, where orientation is ill-defined) and `scatter_ok`
  (the `n_votes >= min_votes` gate).
- **`stats.tile_quality(kind="both", version=None, *, min_votes=5, agg="median",
  ranks=True)`** aggregates to one row per `tile_id` with the **support** and
  **scatter** column groups kept strictly separate: scatter (`angle_scatter`,
  `pos_scatter`, `size_scatter`) is computed only from markings that pass the
  vote gate, so weak support can never masquerade as disagreement, and vote
  counts never divide the scatter numbers (no SEM). Optional cap-wide
  percentile `support_rank`/`scatter_rank` make the incommensurate units
  combinable.
- **`stats.classify_tile_quality(tq, *, support_thresh=50, scatter_thresh=50)`**
  labels tiles `consistent` / `contested` / `sparse` / `noisy` from the two rank
  axes; tiles with no gated marking (hence no scatter estimate) are left `<NA>`
  rather than guessed.
- New tutorial **`03a_tile_quality`** introduces the API with live v3.1
  examples; tests in `tests/test_stats.ipynb`.

### Added — coverage & plotting helpers
- **`coverage.pct_summary(coverage, pcts=...)`** returns a percent-scaled
  percentile+mean summary; **`coverage.attach_tile_metadata(per_tile, *,
  version="v3.1")`** adds `roi_name`/`Ls`/`MY` per obsid.
- **`plotting.plot_random_tiles_with_min_fans`** and
  **`plot_random_tiles_with_min_blotches`** sample and plot random tiles meeting
  a minimum marking count.

### Changed — v3.1 catalog re-published with per-marking cluster std columns
- The v3.1 fan/blotch catalogs are re-published as Zenodo **v3.1.1**
  (`doi:10.5281/zenodo.21917907`), adding the seven per-marking cluster standard
  deviations (`x_std`, `y_std`, `angle_std`, plus `distance_std`/`spread_std`
  for fans and `radius1_std`/`radius2_std` for blotches) that feed the new
  uncertainty API. The change is **strictly additive** — every pre-existing
  column and value is byte-identical — so `get_fan_catalog("v3.1")` /
  `get_blotch_catalog("v3.1")` transparently gain the columns with no break to
  existing code. The `io` v3.1 registry is repointed and all v3.1 files unified
  onto the single new DOI.
- **`ReleaseManager.FAN_COLUMNS_AS_PUBLISHED` / `BLOTCH_COLUMNS_AS_PUBLISHED`**
  now retain the std columns, so future catalog production carries them through
  `merge_all` rather than dropping them at publish.

## [0.22.0] — 2026-07-01

### Added — offline subframe cache access
- **`get_cached_tile_ids()`** returns the sorted list of tile IDs whose subframe
  image is already present in the local pooch cache, by reverse-mapping each
  cached `<md5(url)>-<subject>.jpg` file back to its tile ID via `get_tile_urls`.
- **`is_tile_cached(tile_id)`** reports whether a tile's subframe is cached.
- **`get_subframe(..., download=False)`** and
  **`get_subframe_by_tile_id(..., download=False)`** raise `FileNotFoundError`
  when the image is not cached instead of attempting a network fetch — useful now
  that the original `www.planetfour.org` subject host is offline.

### Changed
- **`get_url_for_tile_id` is memoized.** It previously re-read the 114k-row
  `tile_urls` table and rebuilt its index on every call (~10 ms); it now uses a
  process-cached `tile_id → url` Series (microseconds per lookup), a large speedup
  on any loop over tiles. Call `io._tile_url_series.cache_clear()` to refresh after
  the table changes.

### Deprecated
- **`get_url_for_tile`** and **`get_subframe_for_tile`** now emit a
  `DeprecationWarning`; use `get_url_for_tile_id` and `get_subframe_by_tile_id`.

### Fixed
- **`markings.Fan` now accepts `with_center` instead of leaking it into matplotlib.**
  `Fan` forwarded unknown constructor kwargs to `matplotlib.lines.Line2D`, so
  `Fan(data, with_center=...)` raised `AttributeError: Fan.set() got an unexpected
  keyword argument 'with_center'`. 0.21.0 and 0.21.2 worked around this by stripping
  `with_center` at specific call sites; this release fixes the root cause — `Fan`
  absorbs `with_center` as a no-op (fans have no center) — and
  `plotting.plot_fans_for_tile` now threads it through like `plot_blotches_for_tile`.

### Removed
- Deleted the orphaned, empty `p4tools/data_extract.py` stub (its notebook was
  parked as `notebooks/_data_extract.ipynb`, excluded from export). No public API
  change — the module exported nothing — and this unblocks `nbdev_update`.

## [0.21.2] — 2026-06-29

### Fixed
- **`with_center` no longer leaks into `Fan` in the production plotting path.**
  `TileID.plot_markings` (used by `plot_raw_fans`/`plot_raw_blotches` via the
  production `TileID`) passed `with_center` to whichever marking class it built.
  `Blotch` accepts that keyword, but `Fan` forwards unknown kwargs to
  `matplotlib.lines.Line2D`, so `plot_raw_fans(...)` raised
  `AttributeError: Fan.set() got an unexpected keyword argument 'with_center'`.
  `with_center` is now only passed when building blotches. The earlier 0.21.0
  fix only covered the analogous case in `plotting.plot_fans_for_tile`; this
  closes the same bug in the production `markings` module.

## [0.21.1] — 2026-06-16

### Fixed
- **Packaging now ships the `p4tools.production` subpackage.**
  `[tool.setuptools.packages.find]` used `include = ["p4tools"]`, which matches
  only the top-level package — so `p4tools.production.*` (and therefore the `p`
  CLI, which imports it) was missing from the installed wheel/conda package in
  0.21.0 and every earlier release. Changed to `include = ["p4tools*"]`.

## [0.21.0] — 2026-06-16

### Added — map-projected marking overlays
Plot fan/blotch markings on map-projected imagery/axes. Only marking *centroids*
are ground-projected in the catalog (`Longitude`/`PlanetocentricLatitude` via ISIS
`campt`); the shape (`angle`, `distance`, `spread`, `radius_1/2`) stays in image
pixels. These helpers rebuild the full outline in ground coordinates using the
calibrated `north_azimuth`/`map_scale` transform plus `planetarypy.crs` geodesy.

- **`Fan.to_shapely_ground(crs=None)` / `Blotch.to_shapely_ground(...)`** (on
  `MarkingMixin`) — exact outline (reuses `to_shapely()`) reprojected into any
  pyproj/rasterio/cartopy CRS, or lon/lat if `crs` is None. Raises `KeyError`
  if the data lacks the projection columns.
- **`markings.markings_to_geoseries(df, kind, crs=None, ...)`** — fast vectorized
  approximate outlines (sector for fans, ellipse for blotches) as a `GeoSeries`.
- **`plotting.add_fans` / `plotting.add_blotches`** — overlay on a cartopy axis
  (`src_crs=`) or in a projected raster's own CRS (`target_crs=`).
- **`plotting.overlay_obsid(obsid, image_path)`** — show a map-projected raster
  and overlay that obsid's fans + blotches, aligned in the image CRS.

`planetarypy` and `rasterio` are imported lazily (optional `[pipeline]` extras).

### Fixed
- **`plot_fans_for_tile`** no longer passes `with_center` to `Fan` (only `Blotch`
  accepts it), which raised `AttributeError: Fan.set() got an unexpected keyword
  argument 'with_center'`.

### Known issues
- ⚠️ **Tile image download is currently not working.** The stored tile subject
  URLs point to `http://www.planetfour.org/subjects/standard/<id>.jpg`, and that
  host is no longer reachable. Any function that fetches the tile PNG —
  `io.get_subframe`, `io.get_subframe_by_tile_id`/`get_subframe_for_tile`, and
  anything that draws on the tile image (e.g. `plot_raw_fans`,
  `TileID.show_subframe`) — will time out. Catalog/data access and the new
  map-projected overlays (which take a local `image_path`) are unaffected.

## [0.20.1] — 2026-05-06

### Fixed
- **`region_names` MY 33 mapping completed**: the 0.20.0 release shipped a
  CSV with only 11 of the 13 MY 33 observations (the v1 baseline + the
  fan-catalog-derived obsid list). Two MY 33 observations
  (`ESP_048431_0950`, `ESP_048576_0950`) have only blotches, no fans, so
  they were silently absent from the fan catalog and missed when I built
  the obsid list. New file ships all 13 (5 Manhattan_Classic + 8 Ithaca),
  derived from `metafull` directly. New Zenodo DOI:
  [10.5281/zenodo.20054858](https://doi.org/10.5281/zenodo.20054858)
  (MD5 `9090f80faeb215819215362d2800bec6`).

## [0.20.0] — 2026-05-06

### Fixed — `region_names` now covers MY 33

The v1 region_names dataset shipped with p4tools was missing 11 MY 33
observations (5 Manhattan_Classic + 6 Ithaca), so any code calling
`get_region_names()` or `attach_roi()` silently dropped MY 33 from
ROI-matched analyses. The fix ships an updated CSV alongside the v3.1
catalog and re-points the loader.

- New file `P4_catalog_v3.1_region_names.csv` (465 rows; MD5
  `b51e41b86afe2d53be5a2ee6d2504369`) released on Zenodo
  [DOI 10.5281/zenodo.20054589](https://doi.org/10.5281/zenodo.20054589).
  The 11 MY 33 entries' lat/lon come from `metafull.IMAGE_CENTER_*`
  and timestamps from the `planetarypy.instruments.mro.hirise` RDR
  index; ROI assignments verified by lat/lon proximity to existing
  ROI centroids (Manhattan_Classic at -86.39°/99.0°, Ithaca at
  -85.13°/180.7°).

### Changed — `get_region_names` and `attach_roi` now version-aware

- **`get_region_names(version=None)`** — defaults to ``"v3.1"``
  (was implicitly v1). v1 still reachable via ``version="v1"`` for
  historical reproduction.
- **`attach_roi(df, *, obsid_col="obsid", version="v3.1")`** —
  forwards the version through to the loader.

## [0.19.1] — 2026-05-06

### Changed
- **`apply_talk_context` is now a thin wrapper over `seaborn.set_context("talk", ...)`** —
  no more hand-maintained rcParams dict. Element proportions (titles vs axis labels
  vs ticks vs legend) are now whatever seaborn's `talk` context provides; we only
  choose the `font_scale` so the smallest baseline element (tick labels at ~16.5 pt)
  meets `min_pt` (default 24). Visual output is essentially unchanged but maintenance
  burden is gone.

## [0.19.0] — 2026-05-06

### Added — `p4tools.activity`
- **New top-level analysis module** for ground-area-aware activity metrics:
  - `tile_ground_area_m2(obsids=None, version="v3.1")` — per-obsid tile
    ground area in m² (840×648 × `map_scale`²; values land at 34 020 / 136 080
    / 544 320 m² for the three v3.1 pixel scales 0.25 / 0.5 / 1.0 m/px).
  - `per_tile_marking_density(version="v3.1", kind="all"|"fan"|"blotch")`
    → `[obsid, tile_id, n_fans, n_blotches, n_markings, map_scale,
    tile_ground_area_m2, density_per_m2]`. Combined fans + blotches by
    default — both are markers of jet activity at the eruption-event
    level; separating dilutes the signal.
  - `per_marking_ground_area(version="v3.1", kind="both"|"fan"|"blotch")`
    → per-marking polygon area in m² (caches as parquet next to the
    coverage cache; ~135 s fresh compute on v3.1).

### Changed — module relocation (deprecation, not breakage)
- **`p4tools.coverage` is now the canonical location** for the coverage
  module (was `p4tools.production.coverage`). Coverage is *analysis* of
  the catalog, not part of producing the catalog, so it doesn't belong
  under `production/`.
- **`p4tools.production.coverage` kept as a deprecation shim** that
  re-exports from the new location and emits a `DeprecationWarning`.
  The shim will be removed in **v0.20**.
- `p4tools.egu26` updated to import from the new path.

## [0.18.2] — 2026-05-06

### Fixed
- **Docs build (round 2)**: 4 interactive exploration cells in
  `07_panoptes_extract` referenced a local Dropbox path
  (`/Users/maye/.../planet-four-classifications.csv`) and were running
  during Quarto render, causing the GH Pages workflow to fail with
  `FileNotFoundError`. Added `# | eval: false` to all four.

## [0.18.1] — 2026-05-06

### Fixed
- **GitHub Pages docs build**: the `if __name__ == "__main__":` cells in
  `04_classify_by_activity`, `05g_production.coverage`, and `08_egu26`
  notebooks were being executed during Quarto rendering (because
  `__name__ == "__main__"` is True in a Jupyter kernel), each triggering
  a multi-minute `compute_per_tile_coverage()` Shapely union pass with
  no cache on CI. The runner timed out at 56 min. Added `# | eval: false`
  directives so the cells still export to the `.py` (preserving the
  module-as-script entry points) but are skipped during notebook render.

## [0.18.0] — 2026-05-05

### Added — v4.0 raw-source ingest pipeline

- **`p4tools.panoptes_extract`**: ingest `planet-four-classifications.csv` from
  the Panoptes platform (workflow 12978) into a flat per-marking parquet,
  enriched with metadata, tile coords, and image URLs.
- **`p4tools.production.cleaning`**: pre-clustering canonicalisation extracted
  from the legacy `planet4.reduction` CLI. Public API:
  `filter_nan_required`, `filter_default_markings`, `filter_out_of_frame`,
  `canonicalize_blotch_geometry`, `canonicalize_fan_angles`,
  `compute_angle_components`, and a per-source `clean_classifications`
  orchestrator (`source="panoptes" | "zooniverse_v1"`).
- **Pipeline sequence (v4.0+)**: raw classifications now flow
  `panoptes_extract → production.cleaning → production.{dbscan,fnotching,catalog}`.
  See the *Raw classification → catalog pipeline* section in `index.ipynb`.

### Added — analysis modules

- **`p4tools.classify_by_activity`**: per-HiRISE-observation classification of
  tile marking-count distributions into bimodal / unimodal-busy / unimodal-quiet
  patterns, with per-tile `busy=True/False` labels.
- **`p4tools.production.coverage`**: per-tile and per-obsid fractional dark-deposit
  coverage from the union of fan + blotch polygons. Verbatim port of Tom Ihro's
  legacy `Calculate_Coverage_v2.ipynb` (byte-equivalent on v3.1).
- **`p4tools.egu26`**: reproducible plot functions for slides 5/6/7 of the
  EGU26 oral talk.
- **`p4tools.plotting`**: `apply_talk_context` (24 pt-minimum slide-deck rcParams),
  `histogram_kde`, `kde_per_group`, `smallmult_highlight_grid`.
- **`p4tools.io`**: `attach_my`, `attach_roi` for left-joining obsid-keyed
  dataframes with metafull (MY, L_s) and region_names.

### Changed

- **Markings refactor**: `Blotch`, `Fan`, `Blotches`, `Fans` now share new
  `MarkingMixin` and `MarkingCollection` base classes (deduplicates `tile_id`,
  `n_members`, `is_equal`, `__init__`, `__repr__`). `TileBlotches` and
  `TileFans` subclasses removed; replaced by `Blotches.from_tile_id` /
  `Fans.from_tile_id` classmethods. Net 950-line reduction in `markings.py`.

## [0.17.2] — 2026-03-16

### Added
- **`plot_raw_fans` / `plot_raw_blotches`**: Plot raw citizen science markings
  from the classifications database. Auto-resolves DB path from config.

### Fixed
- **`Blotch.tile_id` / `Fan.tile_id`**: Fall back to `image_id` when
  `tile_id` column is absent (raw classifications DB compatibility).

## [0.17.0] — 2026-03-16

### Fixed
- **v3.1 catalog — user dedup re-clustering**: Re-clustered 10 obsids where
  single-user duplicate fan markings created false clusters (12 fan entries
  removed). Final Zenodo upload: `zenodo.org/records/19057090`.

## [0.16.21] — 2026-03-16

### Fixed
- **v3.1 catalog Zenodo DOI**: Updated to corrected upload
  (`zenodo.org/records/19052818`) with complete catalog files.
  Updated MD5 checksums for fans, blotches, and tile_coords.

## [0.16.17] — 2026-03-16

### Added
- **Catalog v3.1 via Zenodo**: `v3_1` pooch registry now fetches from
  `doi:10.5281/zenodo.19026723` with MD5 checksums and CSV→parquet
  postprocessing, identical to the v1 Zenodo setup.
- **`set_catalog_version(version)`**: Persistent session-wide default version
  setter. `from p4tools import set_catalog_version; set_catalog_version('v3.1')`.
- **`catalog_version(version)` context manager**: Scoped temporary version
  override — restores the previous default on exit, even on exception.
  `from p4tools import catalog_version`.
- Both `set_catalog_version` and `catalog_version` re-exported from `p4tools`
  top-level (`__init__.py`).
- **Per-tile `.done` sentinel** in `cluster_image_id`, `fnotch_image_ids`,
  and `_apply_cut_to_tile`: written after successful completion of each
  pipeline stage. Checked at the start of each stage to skip already-done
  tiles. Replaces the faulty obsid-level skip guards.

### Changed
- **Default catalog version is now `v3.1`** (was `v3`). All `io` functions
  (`get_fan_catalog`, `get_blotch_catalog`, `get_tile_coords`, etc.) default
  to v3.1 when no `version` argument is given.
- Version string `"v3.1"` replaces the internal Python-identifier-style key
  `v3_1` throughout — `fetchers` dict now uses `{"v3.1": v3_1.fetch}`.
- All public `io` functions accept `version=None` (resolved via
  `_resolve_version`) instead of a hardcoded `version="v3"` default.
- **`check_for_todo`** no longer skips obsids — always includes all obsids
  in `self.todo`. Per-tile `.done` sentinels handle skip logic.
- **Fnotching skip guard removed** from `produce` CLI — was checking for
  L1B directory existence at obsid level, now handled by per-tile sentinels.

### Fixed
- **Per-cluster user deduplication** in `get_average_objects`: each user now
  contributes at most once per cluster (`drop_duplicates(subset=["user_name"])`).
  Restores safeguard from the original `planet4/clustering.py` that was lost
  during the port to p4tools. Without this, a single user marking the same
  spot 3+ times could create a spurious cluster passing `min_samples`.
- **Obsid-level skip guard caused permanently skipped tiles**: `check_for_todo`
  checked for L1A directory existence (created before clustering runs by
  `write_settings_file`). An interrupted run left empty L1A dirs that caused
  the entire obsid (hundreds of tiles) to be skipped on re-runs. In v3.1,
  this caused 892 tiles across 5 obsids to be permanently skipped.

## [0.16.5] — 2026-03-12


### Fixed
- **`'TypeError' object has no attribute 'stdout'` crash**: When kalasiris
  import fails (e.g. no `ISISROOT`), `ProcessError` falls back to `Exception`,
  catching all errors including `TypeError` from `None`-valued ISIS functions.
  Added early guard in `nocal_hi` to raise a clear `RuntimeError` when ISIS is
  unavailable, and switched all `except ProcessError` blocks to use
  `getattr(e, 'stdout', '')` for safety.

## [0.16.4] — 2026-03-12

### Added
- **`p4 create-mosaic` CLI command**: Test RED45 mosaic creation for a single
  obsid. Accepts `--overwrite` flag to force re-download and recreation.

## [0.16.3] — 2026-03-12

### Fixed
- **Missing RED45 mosaic creation in `produce` CLI**: The `produce` command skipped
  `create_RED45_mosaic()` between fnotching and post-processing, causing Phase 3 to
  crash when cube files didn't exist. Added parallel mosaic creation as Phase 2.5.

## [0.16.2] — 2026-03-12

### Fixed
- **Missing directory in Phase 3 post-processing**: `TileCalculator.calc_tile_coords()`
  wrote a temp CSV to `cubepath.parent` without ensuring the directory exists. Added
  `mkdir(parents=True, exist_ok=True)` before the `to_csv()` call. This fixes the
  `OSError: Cannot save file into a non-existent directory` crash during `p4 produce`.

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

## [0.13.0] — 2026-02-24

### Changed
- Replaced `pyaml` with stdlib `json` for clustering settings output.

### Fixed
- Fixed `nbdev_preview` crashes caused by uncaught `kalasiris` `KeyError`;
  added `# | eval: false` guard to CLI entry point cell.
- Removed unnecessary `__main__` guard from CLI notebook.
- Fixed outdated `settings.ini` reference in CLI docs (now `pyproject.toml`).
- Cleaned up docs sidebar with consistent titles and section grouping.

## [0.12.0] — 2026-02-23

### Added
- Production pipeline merged from Tom Ihro's fork (`p4tools_tihro`): full
  L0→L1A→L1B→L1C pipeline via `p4 produce`, DBSCAN clustering, fnotching,
  RED45 mosaic creation, coordinate projection.
- Cluster size validation in `cluster_obsid()`.
- `geopandas` added as dependency for stamp visualisation.

### Changed
- **nbdev 3.0 migration**: `settings.ini` → `pyproject.toml`; regenerated
  cell IDs for all notebooks.
- Replaced `dask` with stdlib `concurrent.futures` for parallel execution.
- Moved `planetarypy` to optional `[pipeline]` extras; all ISIS/SPICE imports
  are now conditional to allow lightweight installs.
- `get_config()` returns `None` instead of raising when config file is missing.
- Removed interactive `input()` prompts; replaced with logged warnings for
  non-TTY environments.
- All production notebooks (`05*.ipynb`) marked `skip_exec: true` to prevent
  accidental execution during `nbdev_test` / docs build.
- Fixed CI deploy workflow to use `nbdev 3.0` `quarto-ghp3` action.

### Fixed
- Fixed typo in `Blotch.is_equal`: was comparing `image_x` to `image_y`.
- Removed accidentally committed ISIS `print.prt` artifact.

## [0.11.0] — 2025-11-09

### Added
- `Fans` and `Blotches` container classes for working with collections of
  fan/blotch markings.
- Fixed v3 `tile_coords` hash in pooch registry.

### Fixed
- Various dependency and deploy workflow fixes.

## [0.10.3] — 2025-03-25

### Added
- `get_url_for_tile_id()` and `get_subframe_by_tile_id()` for tile image access.
- `normalize_tile_id()` for robust tile ID normalisation (handles short forms,
  missing `APF` prefix, variable-length zero-padding).
- `version` parameter added to `get_hirise_id_for_tile()`.

### Changed
- Plotting functions now warn (instead of silently returning) when no
  blotches are found for a tile.
- README converted to Markdown; updated with data sources and reference paper.
- Minimum Python version set to 3.10; license updated to MIT.
