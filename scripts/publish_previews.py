"""Replace generated previews after validating all resolved paths in this repository."""
from pathlib import Path
import shutil,sys,time
root=Path(__file__).resolve().parents[1]
source=Path(sys.argv[1]).resolve();dest=(root/'slides/previews').resolve()
backup=(root/'.build'/('old-previews-'+str(time.time_ns()))).resolve()
for target in [source,dest,backup]:
    target.relative_to(root)
assert source.is_dir() and source.parent==root/'.build'
assert dest==root/'slides/previews'
if dest.exists():dest.rename(backup)
shutil.copytree(source,dest)
print('Published',len(list(dest.glob('*.png'))),'previews')
