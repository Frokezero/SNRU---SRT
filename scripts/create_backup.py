"""Create an online database + uploads backup without stopping the server."""
import argparse
from pathlib import Path
import sys
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
load_dotenv(ROOT / '.env')
from activity_core.improvements import create_backup


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    if args.output.exists():
        parser.error('Output exists; refusing to overwrite')
    payload = create_backup(ROOT / 'uploads')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('xb') as output:
        output.write(payload.getbuffer())
    print(f'Backup created: {args.output.resolve()}')


if __name__ == '__main__':
    main()
