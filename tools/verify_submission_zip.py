"""Check ZIP CRCs and exact staged file contents, including every runtime file."""
from pathlib import Path
import hashlib
import sys
import zipfile


def main(package: Path, archive: Path) -> None:
    expected = {p.relative_to(package.parent).as_posix(): p
                for p in package.rglob("*") if p.is_file()}
    with zipfile.ZipFile(archive) as zipped:
        assert zipped.testzip() is None, "ZIP CRC failure"
        files = [entry.filename for entry in zipped.infolist() if not entry.is_dir()]
        assert len(files) == len(set(files)), "Duplicate ZIP entries"
        assert set(files) == set(expected), "ZIP inventory differs from staging folder"
        for name, path in expected.items():
            assert hashlib.sha256(zipped.read(name)).digest() == hashlib.sha256(path.read_bytes()).digest(), name
    print(f"PASS: ZIP CRC, inventory and SHA-256 content match for all {len(expected)} staged files.")


if __name__ == "__main__":
    main(Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve())
