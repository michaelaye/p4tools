# CLAUDE.md — p4tools

Guidance for Claude Code when working in the **p4tools** repository (published
catalog-access library for the Planet Four Zooniverse project).

## Project shape

- **nbdev project: the notebooks in `notebooks/` are the source of truth.** The
  `.py` files under `p4tools/` are generated — never edit them by hand. Edit the
  notebook, then `nbdev_export`. (Exception per saved convention: for an *existing*
  function you may edit the `.py` and run `nbdev_update` to sync back.)
- Config lives entirely in `pyproject.toml`: setuptools build backend, dynamic
  version from `p4tools.__version__`, `[tool.nbdev]`, `[tool.ruff]` (line length
  100), `[tool.pytest.ini_options]`. There is no `settings.ini` or `setup.cfg`.
- Lint with **ruff** (`ruff check .`). Tests run via **`nbdev_test`** (the test
  notebooks under `tests/` are `.ipynb`).
- CLI entry point: `p = p4tools.clis:app` (Typer).
- Catalog data is fetched with `pooch` from Zenodo/refubium and cached.

## Semver bump type

Any commit adding **API surface** — a new exported function, a new keyword on an
existing function, a new CLI verb, a new config key — is **MINOR**. PATCH is for
pure bug fixes that add no surface. MAJOR is for breaking changes. Don't default
everything to PATCH; look at the diff and ask "did I add a name a user can reach?"

## Don't auto-commit

Wait for explicit approval before committing. Exception: a release cycle (when the
user has explicitly invoked it) follows the Release Process below and makes several
commits as part of that workflow.

## Release Process

Triggered by **"do a full release cycle"**. Four publishing surfaces — **git tag,
PyPI, anaconda.org, GitHub Release** — are ONE indivisible release; none is "done"
until all four are. If interrupted, finish the missing steps before considering the
cycle closed. Notebooks are the source of truth, so always `nbdev_export` before
building.

1. **CHANGELOG.md** entry: `## [X.Y.Z] — YYYY-MM-DD`, Keep-a-Changelog sections
   (`### Added/Changed/Fixed`, and `### Known issues` when relevant), prose bullets
   matching prior style. Choose the bump type per the semver rule above.
2. `nbdev_export` (notebooks → `p4tools/*.py`).
3. **Gate: `nbdev_test` must pass.** (Demo cells that fetch `www.planetfour.org`
   subject images are marked `#| eval: false` — that host is down; see CHANGELOG
   "Known issues". If a real failure appears, fix it before continuing.)
4. Stage + commit the feature work + CHANGELOG with a descriptive message.
5. **Bump the version** (nbdev-native — never edit `__init__.py` by hand), then
   commit and tag:
   ```bash
   nbdev_bump_version --part {2|1|0}        # 2=patch, 1=minor, 0=major
   V=$(python -c "import p4tools; print(p4tools.__version__)")
   git commit -am "Bump version to $V"
   git tag "v$V"
   ```
6. `git push && git push --tags`
7. **Build + PyPI** (manual upload — there is no GH Actions publisher):
   ```bash
   rm -rf dist/ && python -m build && python -m twine check dist/* && python -m twine upload dist/*
   ```
   Needs the `build` package once: `pip install build`.
8. **GitHub Release** (keeps the Releases tab in sync with PyPI + conda):
   ```bash
   V=$(python -c "import p4tools; print(p4tools.__version__)")
   awk -v ver="$V" '$0 ~ "^## \\[" ver "\\]" {f=1; next} /^## \[/{if(f)exit} f' CHANGELOG.md > /tmp/release_notes.md
   gh release create "v$V" --repo michaelaye/p4tools \
     --title "v$V — <short subject from the CHANGELOG opening>" \
     --notes-file /tmp/release_notes.md
   ```
9. **conda recipe** `conda/meta.yaml`:
   - Bump `{% set version = "X.Y.Z" %}`.
   - Replace `sha256:` with the PyPI sdist hash:
     ```bash
     curl -s https://pypi.org/pypi/p4tools/X.Y.Z/json \
       | jq -r '.urls[] | select(.packagetype=="sdist") | .digests.sha256'
     ```
10. `conda-build conda/ --output-folder /tmp/conda-output --no-anaconda-upload`
11. `anaconda --site anaconda upload /tmp/conda-output/noarch/p4tools-X.Y.Z-*.conda`
    (glob the build string — the hash suffix varies).

**Notes:**
- `--site anaconda` required (bypasses an interactive prompt that fails non-TTY).
- `conda-build`, `anaconda-client`, `grayskull`, `build`, `twine`, `gh` live in the
  `py314` conda env.
- `noarch: python` — one build for all platforms; uploads to the **michaelaye**
  anaconda.org channel (same as planetarypy).
- conda run-deps mirror the pyproject **core** deps (`matplotlib` → `matplotlib-base`,
  others 1:1). The optional `[pipeline]` extras are intentionally not in the recipe.
- If `nbdev_test` is red for a real reason: fix on `main`, delete the tag, re-bump.
