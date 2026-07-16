# Contribution Guidelines

We take pull requests!

All pull requests are thoroughly reviewed for code quality.


## Parts Contributions

This repository maintains a curated parts library since:
- parts represent a continuing maintenance commitment
- we want to avoid choice overload for users

As such, good candidates for inclusion in this repository are:
- parts with good support among the maker and open-source community, such as support in ESPHome or high quality Arduino or Rust libraries
- parts with breakout boards available, such as by Sparkfun or Adafruit
- parts available from many distributors, including JLC assembly (particularly basic parts), Mouser, and Digi-Key 
- parts with wide applicability

Parts that are poor candidates for inclusion are:
- parts that cannot be sourced by individuals
- parts with no public documentation (community-provided documentation counts)
- parts that cannot be hand-soldered (including with hot air), primarily BGA 
- extremely integrated parts which do not have a clean block boundary or interface
- niche parts

Borderline case? Feel free to open a PR and we can discuss.

There will be many useful parts that are not a good fit for inclusion here.
Consider creating a separate repository and publishing it on pip with a dependency on this project.


## Compiler / Infrastructure Contributions

If you're thinking of implementing a significant feature or refactor, please discuss the plan with us first.
We'd prefer to figure out and nail down the architecture before any detailed coding.


## Example Boards

Third party designs should go in their own repositories, unless you feel it makes sense as an integration test here.

We may link high quality designs, feel free to open an issue or PR.
