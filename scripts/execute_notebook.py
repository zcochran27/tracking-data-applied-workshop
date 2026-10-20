from pathlib import Path
import nbformat
from nbclient import NotebookClient

root=Path(__file__).resolve().parents[1]
p=root/'notebooks/tracking_data_applied.ipynb'
nb=nbformat.read(p,4)
client=NotebookClient(nb,timeout=300,kernel_name='python3',resources={'metadata':{'path':str(root)}})
try:
    client.execute()
finally:
    nbformat.write(nb,p)
print('Notebook executed successfully')
