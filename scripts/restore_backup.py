"""Verify a backup, optionally restore to a NEW directory, never over live data."""
import argparse
from pathlib import Path
import sys
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from activity_core.improvements import verify_backup


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('backup', type=Path)
    parser.add_argument('--restore-to', type=Path, help='New directory only; must not exist')
    args = parser.parse_args()
    count = verify_backup(args.backup)
    print(f'Verified {count} files and database integrity.')
    if not args.restore_to:
        return
    destination = args.restore_to.resolve()
    if destination.exists():
        parser.error('Destination already exists; refusing to overwrite any data')
    with zipfile.ZipFile(args.backup) as archive:
        members = []
        for name in archive.namelist():
            if name == 'manifest.json':
                continue
            target = (destination / name).resolve()
            if destination not in target.parents:
                parser.error('Unsafe archive path')
            members.append((name, target))
        destination.mkdir(parents=False, exist_ok=False)
        for name, target in members:
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open('xb') as output:
                output.write(archive.read(name))
    print(f'Restored to {destination}. Live application was not changed.')


if __name__ == '__main__':
    main()
