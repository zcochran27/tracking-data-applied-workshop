"""Execute independent avenue notebooks, then save standalone HTML exports."""
from pathlib import Path
import json
import nbformat
from nbclient import NotebookClient
from nbconvert import HTMLExporter

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/avenues';OUT.mkdir(exist_ok=True)
report=[]
for path in sorted((ROOT/'notebooks/avenues').glob('*.ipynb')):
    print('Executing',path.name,flush=True)
    book=nbformat.read(path,4)
    client=NotebookClient(book,timeout=300,kernel_name='python3',resources={'metadata':{'path':str(ROOT)}})
    try:client.execute()
    finally:nbformat.write(book,path)
    errors=[o for cell in book.cells if cell.cell_type=='code' for o in cell.outputs if o.output_type=='error']
    assert not errors,path.name
    html,_=HTMLExporter().from_notebook_node(book)
    (OUT/(path.stem+'.html')).write_text('\n'.join(line.rstrip() for line in html.splitlines()).rstrip()+'\n',encoding='utf-8')
    report.append({'notebook':path.name,'code_cells':sum(c.cell_type=='code' for c in book.cells),'errors':len(errors)})
    print('Verified and exported',path.name,flush=True)
(OUT/'execution_report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
