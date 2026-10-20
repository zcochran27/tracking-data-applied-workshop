"""Cache a bounded real SkillCorner sample; never fabricate missing data."""
import json
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'data' / '1925299'
REVISION = '4340d274572876239c154c90bc507a9b3250a656'
BASE = f'https://raw.githubusercontent.com/SkillCorner/opendata/{REVISION}/data/matches/1925299/'

def main():
    DEST.mkdir(parents=True, exist_ok=True)
    for suffix in ['match.json', 'dynamic_events.csv', 'phases_of_play.csv']:
        name = f'1925299_{suffix}'
        with urllib.request.urlopen(BASE + name, timeout=90) as response:
            (DEST / name).write_bytes(response.read())
        print(name)
    name = '1925299_tracking_extrapolated.jsonl'
    # First 15 minutes at native 10 Hz. Closing the stream avoids a full-match download.
    tracking_url = BASE.replace('raw.githubusercontent.com/', 'media.githubusercontent.com/media/') + name
    with urllib.request.urlopen(tracking_url, timeout=90) as response, (DEST / name).open('wb') as out:
        count = 0
        for line in response:
            if line.strip():
                json.loads(line)
                out.write(line)
                count += 1
            if count >= 9000:
                break
    (DEST / 'sample_info.json').write_text(json.dumps({'match_id':1925299,'frames':count,'source':BASE,'scope':'First 9000 records, not a full match'}, indent=2))
    print('tracking records:', count)

if __name__ == '__main__':
    main()
