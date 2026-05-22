"""Utility script to update all the reference netlists in the examples directory."""

if __name__ == "__main__":
    from pathlib import Path

    for toplevel_item in Path(__file__).parent.iterdir():
        if toplevel_item.is_dir():
            for file in toplevel_item.iterdir():
                if file.is_file() and file.suffix == ".net":
                    reference_file = toplevel_item / (file.name + ".ref")
                    if reference_file.exists():
                        reference_file.unlink()
                    file.rename(reference_file)
                    print(f"Updated {reference_file}")
