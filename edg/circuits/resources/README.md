This folder contains parts tables used by some components.

## JLC Parts Library
The full table (274MB) was downloaded on April 24, 2022, and is [available on the Internet Archive here](https://web.archive.org/web/20220424072635/https://jlcpcb.com/componentSearch/uploadComponentInfo).

Only a pruned version is included in this repository, to reduce cloning and compilation time.
See jlcprune.py for the script used to produce the pruned file.

## DigiKey Parts Library (deprecated)
Some older example designs used parts tables from DigiKey using their CSV export.
A strict reading of their terms of service implies that we cannot redistribute those, so those were never made public.

In any case, the export format has also changed, and newly downloaded tables will not work with the existing component parsers. 

For context, these tables were downloaded between Fall 2019 and Spring 2020.
