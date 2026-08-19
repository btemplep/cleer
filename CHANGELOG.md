# Changelog

Changelog for `cleer`.
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

<!-- 
## [Unreleased] - YYYY-MM-DD

### Added

### Changed

### Deprecated

### Removed

### Fixed

### Security 
-->

## [0.1.0a13] - 2026-08-18

### Fixed
- Bad `assert` handling for paired punctuation. 


## [0.1.0a12] - 2026-08-16

### Added

- relative paths now work with and without `./`.
- default excludes not include more common python excludes

### Changed

- Switched to pyproject.toml only
- excludes changed to add_excludes to make it more clear that they are added to the defaults.  

### Fixed
- bad __all__ blank lines when empty


## [0.1.0a11] - 2026-08-15

### Fixed
- Missing bad indent formatting
- Violation for empty __all__


## [0.1.0a10] - 2026-08-13

### Added
- many more example tests

### Fixed
- **kwargs format


## [0.1.0a9] - 2026-08-11

### Fixed
- bad indent when formatting with `|`


## [0.1.0a8] - 2026-08-10

### Added
- handle unicode chars
- formatting for math and comparison operators. 

### Fixed
- comment indent being removed
- spaces before comments being removed. 
- fixed glob matching to work on relative paths too.


## [0.1.0a7] - 2026-08-10

### Fixed
- remove `pytokens` dep


## [0.1.0a6] - 2026-08-10

### Fixed
- Bugs with paired punct giving violations when there aren't any.

## [0.1.0a5] - 2026-08-10

### Fixed
- Bugs with paired punct


## [0.1.0a4] - 2026-08-10

### Changed

Everything


## [0.1.0a3] - 2026-07-20

### Fixed
- missing `glob.translate` in python 3.11/12
- bad formatting on functions with "*" as an arg


## [0.1.0a2] - 2026-07-20

Initial Release


## [0.1.0a1] - 2024-02-18

Initial stub 

