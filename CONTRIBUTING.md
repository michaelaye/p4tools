# Contributing

Contributions are welcome and greatly appreciated! Every little bit helps, and
credit will always be given.

## Types of contributions

### Report bugs

Report bugs at <https://github.com/michaelaye/p4tools/issues>. Please include:

- Your OS name and version.
- Any details about your local setup that might help troubleshooting.
- Detailed steps to reproduce the bug.

### Fix bugs / implement features

Look through the GitHub issues. Anything tagged `bug` or `enhancement` and
`help wanted` is open to whoever wants to implement it.

### Write documentation

p4tools could always use more documentation — in the docstrings/notebooks, the
rendered docs, or out on the web in blog posts and articles.

### Submit feedback

File an issue at <https://github.com/michaelaye/p4tools/issues>. If you're
proposing a feature, explain how it would work and keep the scope narrow.

## Get started

p4tools is an [nbdev](https://nbdev.fast.ai/) project: **the notebooks in
`notebooks/` are the source of truth**, and the `.py` files under `p4tools/` are
generated from them. Never edit the `.py` files directly.

1. Fork the repo on GitHub and clone your fork:

   ```bash
   git clone git@github.com:your_name_here/p4tools.git
   cd p4tools
   ```

2. Create an environment and install in editable mode with the dev extra
   (conda recommended):

   ```bash
   conda create -n p4tools python=3.12
   conda activate p4tools
   pip install -e ".[dev]"          # add ".[dev,pipeline]" for the catalog pipeline
   nbdev_install_hooks              # clean notebook outputs in git
   ```

3. Create a branch:

   ```bash
   git checkout -b name-of-your-bugfix-or-feature
   ```

4. Make your changes **in the notebooks**, then sync and check:

   ```bash
   nbdev_export        # notebooks -> p4tools/*.py
   nbdev_test          # run the notebooks as tests
   ruff check .        # lint
   ```

5. Commit and push:

   ```bash
   git add .
   git commit -m "Detailed description of your changes."
   git push origin name-of-your-bugfix-or-feature
   ```

6. Open a pull request on GitHub.

## Pull request guidelines

1. Add tests for new behavior (as notebook cells/asserts).
2. If the PR adds functionality, document it: a docstring on the new function and
   an entry in `README.md` / `CHANGELOG.md`.
3. p4tools targets Python ≥ 3.10.

## Tips

Run a single test notebook:

```bash
nbdev_test --file_glob "01_markings.ipynb"
```
