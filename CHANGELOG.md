# Changelog

All notable changes to this project will be documented in this file.

<!-- scriv-insert-here -->

## v1.2.0, 2026-03-27

### Added

- Added `autoyes` support to the cancel command. [PR #461](https://github.com/llnl/maestrowf/pull/461)
- Added a compact, sortable hashing strategy for step IDs and workspaces. [PR #465](https://github.com/llnl/maestrowf/pull/465)
- Added extra Flux options. [PR #459](https://github.com/llnl/maestrowf/pull/459)

### Changed

- Updated Flux exclusive behavior to modify task information passed to allocation and launcher logic. [PR #467](https://github.com/llnl/maestrowf/pull/467)


## v1.1.11, 2025-07-24

### Changed

- Made the Flux adapter aware of banks and queues. [PR #453](https://github.com/llnl/maestrowf/pull/453)
- Enabled updating study configuration during execution. [PR #445](https://github.com/llnl/maestrowf/pull/445)
- Dropped Python 3.7 and updated build system dependencies. [PR #448](https://github.com/llnl/maestrowf/pull/448)

### Fixed

- Sanitized paths of serialized scripts in script adapters. [PR #451](https://github.com/llnl/maestrowf/pull/451)

### Documentation

- Fixed a typo in `index.md`. [PR #439](https://github.com/llnl/maestrowf/pull/439)


## v1.1.10, 2024-02-06

### Added

- Added a `sacct` fallback to the Slurm adapter to improve job tracking robustness. [PR #405](https://github.com/llnl/maestrowf/pull/405)
- Added pager functionality to the `status` command. [PR #420](https://github.com/llnl/maestrowf/pull/420)

### Changed

- Synced the Read the Docs configuration with Poetry-based development environments. [PR #399](https://github.com/llnl/maestrowf/pull/399)
- Updated Flux job state mappings for Flux versions `>= 0.26`. [PR #407](https://github.com/llnl/maestrowf/pull/407)
- Updated version information to be driven exclusively from `pyproject.toml`, and connected it to the command line. [PR #419](https://github.com/llnl/maestrowf/pull/419)
- Refactored the Flux adapter to avoid using `pickle` when communicating with Flux brokers installed in external environments. [PR #415](https://github.com/llnl/maestrowf/pull/415)

### Fixed

- Printed command-line usage when no arguments are provided. [PR #404](https://github.com/llnl/maestrowf/pull/404)
- Added a missing shebang in unscheduled scripts from the LSF adapter. [PR #411](https://github.com/llnl/maestrowf/pull/411)
- Fixed Dockerfile issue `DL3006`. [PR #418](https://github.com/llnl/maestrowf/pull/418)
- Patched broken Flux job cancellation. [PR #428](https://github.com/llnl/maestrowf/pull/428)
- Insulated Slurm adapters from user customization of `squeue` and `sacct` output formats. [PR #431](https://github.com/llnl/maestrowf/pull/431)

### Documentation

- Ported documentation to MkDocs and expanded feature and tutorial coverage. [PR #403](https://github.com/llnl/maestrowf/pull/403)

### Maintenance

- Bumped `certifi` from `2021.10.8` to `2022.12.7` to address a security issue. [PR #409](https://github.com/llnl/maestrowf/pull/409)
- Bumped `cryptography` from `37.0.1` to `38.0.3` to address a security issue. [PR #410](https://github.com/llnl/maestrowf/pull/410)
- Updated the Poetry lockfile to address Dependabot-flagged security issues. [PR #412](https://github.com/llnl/maestrowf/pull/412)
- Pinned Mermaid to `< 10.x` due to an API change. [PR #422](https://github.com/llnl/maestrowf/pull/422)
- Bumped locked `certifi` from `2022.12.7` to `2023.7.22` to address a security issue. [PR #426](https://github.com/llnl/maestrowf/pull/426)


## v1.1.9, 2023-05-29

### Changed

- Delivered extensive improvements to the Slurm, LSF, and Flux adapters for cluster scheduling.
- Added a Rich-enabled status view.
- Improved workspace hashing.
- Improved parameter generation.
- Included additional background improvements and bug fixes.


## v1.1.8, 2022-06-11

### Changed

- Made the `Specification` class easier to inherit. [PR #280](https://github.com/llnl/maestrowf/pull/280)

### Fixed

- Fixed a regression affecting the use of variables and parameters in scheduling parameters for study steps. [PR #279](https://github.com/llnl/maestrowf/pull/279)

### Documentation

- Updated the docs release version to `1.1.7`. [PR #278](https://github.com/llnl/maestrowf/pull/278)
- Added parameter generation documentation. [PR #275](https://github.com/llnl/maestrowf/pull/275)
- Added the README as the long description so PyPI can render the Markdown README. [PR #269](https://github.com/llnl/maestrowf/pull/269)

### Maintenance

- Replaced a Unicode quote with an ASCII quote. [PR #277](https://github.com/llnl/maestrowf/pull/277)

[PR-269]: https://github.com/llnl/maestrowf/pull/269
[PR-275]: https://github.com/llnl/maestrowf/pull/275
[PR-277]: https://github.com/llnl/maestrowf/pull/277
[PR-278]: https://github.com/llnl/maestrowf/pull/278
[PR-279]: https://github.com/llnl/maestrowf/pull/279
[PR-280]: https://github.com/llnl/maestrowf/pull/280
