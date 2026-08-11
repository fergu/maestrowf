# Release Process

This document describes the release process for `maestrowf`.

The project uses a release-oriented branching model:

- `develop` is the integration branch for normal development.
- `main` contains released code.
- release branches are cut from `develop` and merged back through the release flow.
- versioned release tags are created on `main`.

## Branch and Merge Policy

Use two merge policies:

- ordinary feature, bugfix, documentation, and maintenance pull requests into `develop` may be squash merged
- release promotion and release mergeback pull requests should use merge commits

Squash merging ordinary pull requests keeps `develop` readable, avoids requiring contributors to polish every intermediate review commit, and usually makes reverts simpler. The pull request, squash commit message, changelog fragment, and GitHub review history provide enough traceability for normal development.  This may be revisited in the future with larger features/refactors.

Release branches are promotion branches, so they should preserve ancestry. The release branch commit that was built, uploaded to TestPyPI, and manually validated should remain an ancestor of the official release. Use merge commits for:

- `release/X.Y.Z` into `develop`
- `develop` into `main`
- `chore/mergeback_vX.Y.Z` into `develop`

The next-development version bump branch, such as `chore/start-vNEXTdev0`, may be squash merged because it is a small mechanical change. We will keep it as a pull request rather than a direct push to develop so it remains visible, reviewable, and CI-gated.

The release mergeback and next-development version bump are kept intentionally separate. The mergeback records release ancestry reconciliation. The version bump reopens development. Keeping them separate makes the history easier to audit.

Avoid `dev` version tags unless a need arises for pre-release versions on pypi in the future to keep the git tag space less cluttered. Tags should normally identify final releases on `main`.  Development version provenance is currently 1:1 with develop commits with the current squash merge approach; may revisit this if squash merges are abandoned in the future.

## Release Goals

A release should provide:

- a clean version in `pyproject.toml`
- collected Scriv changelog fragments in `CHANGELOG.md`
- source distribution and wheel artifacts built from the release commit
- a TestPyPI upload suitable for manual installation and scheduler validation
- a final PyPI upload from the same reviewed release content
- a GitHub tag and release whose notes match the collected changelog entry
- release documentation built from the release commit

Manual validation against real schedulers may remain outside GitHub Actions. This project does not have GitHub-hosted runners that can exercise site-specific Slurm, Flux, LSF, and machine policy behaviors and features.

## Required Tools

The repository currently pins Poetry for local development:

```bash
pip install "poetry==1.8.4"
poetry install --with dev,docs
```

Scriv is available through the development dependencies on Python versions that support it.

## Preparing a Release Branch

Start from an up-to-date `develop` branch:

```bash
git checkout develop
git pull --ff-only origin develop
git checkout -b release/X.Y.Z
```

Set the final release version:

```bash
poetry version X.Y.Z
```

Collect the Scriv fragments into `CHANGELOG.md`:

```bash
poetry run scriv collect
```

Check that:

- `pyproject.toml` contains the final release version, not a `dev` version.
- `CHANGELOG.md` has a new `vX.Y.Z, YYYY-MM-DD` section.
- `changelog.d/` no longer contains the fragments that were collected for the release.
- the release notes are understandable without reading the merged pull requests.

Run the local verification that is practical for the machine:

```bash
poetry run pytest
poetry run python scripts/docs_prepare.py --mode release
poetry run mkdocs build
poetry build
```

Commit the release preparation:

```bash
git add pyproject.toml CHANGELOG.md changelog.d
git commit -s -m "Finalize X.Y.Z release"
git push origin release/X.Y.Z
```

Do not merge the release branch yet. First publish this release branch commit to TestPyPI and validate it.

## TestPyPI Publishing

Publish to TestPyPI from the reviewed release branch or from the exact commit that will be merged for release.

Clean any old local build artifacts first:

```bash
rm -rf dist
poetry build
```

Configure Poetry to know about TestPyPI:

```bash
poetry config repositories.testpypi https://test.pypi.org/legacy/
```

Use an API token from TestPyPI. For local publishing, prefer an environment variable instead of storing the token in shell history:

```bash
export TEST_PYPI_API_TOKEN="pypi-..."
poetry publish -r testpypi --username __token__ --password "$TEST_PYPI_API_TOKEN"
```

After the upload, test installation from TestPyPI in a clean environment:

```bash
python -m venv /tmp/maestrowf-testpypi
. /tmp/maestrowf-testpypi/bin/activate
python -m pip install --upgrade pip
python -m pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ maestrowf==X.Y.Z
maestro --version
```

The `--extra-index-url` is normally needed because TestPyPI does not mirror all runtime dependencies.

Run the manual validation matrix that matters for the release. At minimum, record:

- package version and wheel filename tested
- Python version
- operating system or cluster
- scheduler target tested, such as local, Slurm, Flux, or LSF
- representative study names or paths
- pass/fail result and any deviations

If validation finds a release blocker, `develop`, update or add Scriv fragments as needed, and rebuild the release branch. Do not publish a different artifact with the same version number.

### Validation records?

Here's some ideas for potentially tracking release validation; these are currently only documented here, and not yet implemented.

Record validation details in the release pull request or in a dedicated release validation issue:

- release branch name
- release branch commit SHA
- workflow run URL or local build command
- artifact filenames and hashes
- TestPyPI project/version URL
- Python versions and platforms tested
- scheduler targets tested, such as local, Slurm, Flux, or LSF
- representative studies tested
- pass/fail result and any deviations

GitHub Actions artifacts are useful during the release window, but they expire according to repository retention policy.  We can not rely on them as the only long-term record. The durable long-term records should be the final Git tag, PyPI files, GitHub release assets and notes, and the release pull request or validation issue.

## Merging to Main

After TestPyPI validation passes:

1. Open a pull request from `release/X.Y.Z` into `develop`.
2. Merge that pull request with a merge commit.
3. Open the release pull request from `develop` into `main`.
4. Verify CI on the `main` release pull request.
5. Merge the release pull request into `main` with a merge commit.
6. Tag the resulting `main` release commit:

```bash
git checkout main
git pull --ff-only origin main
git tag -a vX.Y.Z -m "maestrowf vX.Y.Z"
git push origin vX.Y.Z
```

7. Publish the final package to PyPI from the tag.
8. Create `chore/mergeback_vX.Y.Z` from current `develop`, then merge `origin/main` into it:

```bash
git checkout develop
git pull --ff-only origin develop
git checkout -b chore/mergeback_vX.Y.Z
git merge --no-ff origin/main -m "Mergeback of main into develop for vX.Y.Z"
git push origin chore/mergeback_vX.Y.Z
```

9. Open a pull request from `chore/mergeback_vX.Y.Z` into `develop`.
10. Merge that pull request with a merge commit.
11. Create `chore/start-vNEXTdev0` from updated `develop`:

```bash
git checkout develop
git pull --ff-only origin develop
git checkout -b chore/start-vNEXTdev0
poetry version NEXT_VERSIONdev0
git add pyproject.toml
git commit -s -m "Start NEXT_VERSIONdev0 development"
git push origin chore/start-vNEXTdev0
```

12. Open a pull request from `chore/start-vNEXTdev0` into `develop`.
13. Merge that pull request. Squash merge is acceptable for this version bump branch.

Use the next appropriate version number for the development bump, for example `1.2.1dev0` after `1.2.0`.

The `v1.2.0` release used this ancestry-preserving shape. Its mergeback was not a squash merge:

- `68c1936` was the `main` release merge commit tagged `v1.2.0`
- `20f0daf` merged `main` into `chore/mergeback_v1.2.0`
- `78ffbe0` merged `chore/mergeback_v1.2.0` back into `develop`

## Release Pull Request Checklist

Use this checklist for the release pull request into `develop`:

- final version set in `pyproject.toml`
- Scriv fragments collected into `CHANGELOG.md`
- release branch commit SHA recorded
- source distribution and wheel built
- TestPyPI upload completed
- clean install from TestPyPI verified
- manual scheduler validation recorded
- release notes reviewed
- CI passing

Use this checklist for the release pull request into `main`:

- source branch includes the validated release commit
- no unrelated changes entered `develop` after validation, or they were intentionally included and validated
- CI passing
- final PyPI publish will happen from the tag after merge

Use this checklist for the mergeback pull request:

- branch starts from current `develop`
- branch merges current `origin/main`
- no release-version or next-dev-version edit is combined into the mergeback
- pull request is merged with a merge commit

Use this checklist for the next-development version bump pull request:

- branch starts from `develop` after mergeback
- only the version bump is included
- squash merge is acceptable

## PyPI Publishing

Publish the final package from the tagged release commit.

```bash
git checkout vX.Y.Z
rm -rf dist
poetry build
```

Use a PyPI API token:

```bash
export PYPI_API_TOKEN="pypi-..."
poetry publish --username __token__ --password "$PYPI_API_TOKEN"
```

Once a version is published to PyPI, treat it as immutable. If a bad package is uploaded, release a new version.

## GitHub Release Notes from Scriv

`CHANGELOG.md` is the source of truth for release notes. Build the GitHub release notes from the Scriv-collected section for the tag.

After `poetry run scriv collect`, inspect the generated section:

```bash
sed -n '/^## vX.Y.Z, /,/^## v/p' CHANGELOG.md
```

For the GitHub release body, use the content under the `## vX.Y.Z, YYYY-MM-DD` heading and stop before the next `##` heading. Keep category headings such as `Added`, `Changed`, and `Fixed`.

If using the GitHub CLI:

```bash
awk '/^## vX.Y.Z, /{capture=1; next} capture && /^## v/{exit} capture{print}' CHANGELOG.md > /tmp/maestrowf-vX.Y.Z-notes.md
gh release create vX.Y.Z --title "maestrowf vX.Y.Z" --notes-file /tmp/maestrowf-vX.Y.Z-notes.md dist/*
```

This keeps the GitHub release, changelog, and documentation aligned.  

**NOTE:** May want/need to start with github's automatic draft release notes to get the text for linking the contributors; scriv doesn't currently record those in the changelog.
