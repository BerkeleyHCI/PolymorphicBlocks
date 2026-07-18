# Contribution Guidelines

We take pull requests!

All pull requests are thoroughly reviewed for code quality.


## Parts Contributions

This repository maintains a curated parts library since:
- parts represent a continuing maintenance commitment
- we want libraries to produce working boards with reasonably high confidence
- we want to avoid choice overload for users

There will be many useful parts that are not a good fit for inclusion on this repository, but we encourage an ecosystem of community libraries.
Consider creating a separate repository and publishing it on pip with a dependency on this project.
We may maintain a list of high quality third-party parts libraries.

Good candidates for inclusion in this repository are:
- parts with good support among the maker and open-source community, such as support in ESPHome or high quality Arduino or Rust libraries
- parts with breakout boards available, such as by Sparkfun or Adafruit
- parts available from many distributors, including JLC assembly (particularly basic parts), Mouser, and Digi-Key 
- parts with wide applicability
- parts using footprints in the standard KiCad libraries, or in PCM libraries
- parts that have been tested functional in a real PCB, consider opening PRs after you've brought up your device

Parts that are poor candidates for inclusion are:
- parts that cannot be sourced by individuals
- parts with no public documentation (community-provided documentation and libraries count)
- parts that cannot be hand-soldered (including with hot air), primarily BGA
- extremely integrated parts which do not have a clean block boundary or interface
- niche parts

Borderline case? Feel free to open an issue or PR for discussion.


## Compiler / Infrastructure Contributions

If you're thinking of implementing a significant feature or refactor, please discuss the plan with us first such as through an issue.
We'd prefer to figure out and nail down an architecture and plan before any detailed coding.


## Third Party Tools

If you build a tool that integrates with / makes use of this HDL, feel free to open an issue to request we add it to a list of such tools.
We may review such tools for quality and readiness before listing.

We are also open to collaborating and discussing on how we can better support third party tooling, particularly community-driven open-source projects.


## Example Boards

Third party designs should go in their own repositories, unless you feel it makes sense as an integration test here.

We may link high quality example / built-with designs.
Feel free to open an issue or PR.
