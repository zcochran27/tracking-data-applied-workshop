"""Add native hyperlinks to source footers and the opening resource entries."""
import json,sys,zipfile
from pathlib import Path
from xml.etree import ElementTree as E

root=Path(__file__).resolve().parents[1]
deck=Path(sys.argv[1])
content=json.loads((root/'slides/content.json').read_text(encoding='utf-8'))
sources=json.loads((root/'resources/sources.json').read_text(encoding='utf-8'))
A='http://schemas.openxmlformats.org/drawingml/2006/main'
P='http://schemas.openxmlformats.org/presentationml/2006/main'
R='http://schemas.openxmlformats.org/officeDocument/2006/relationships'
REL='http://schemas.openxmlformats.org/package/2006/relationships'
E.register_namespace('a',A);E.register_namespace('p',P);E.register_namespace('r',R)
with zipfile.ZipFile(deck) as z: files={n:z.read(n) for n in z.namelist()}
for i,s in enumerate(content,1):
    name=f'ppt/slides/slide{i}.xml';relname=f'ppt/slides/_rels/slide{i}.xml.rels'
    tree=E.fromstring(files[name]);rels=E.fromstring(files[relname])
    for shape in tree.findall(f'.//{{{P}}}sp'):
        runs=shape.findall(f'.//{{{A}}}r')
        for run in runs:
            t=run.find(f'{{{A}}}t')
            if t is None or not t.text:continue
            key=None
            for k in s['sources']:
                if sources[k][0] in t.text:key=k;break
            if i==2:
                for prefix,k in [('SkillCorner/opendata','skillcorner'),('kloppy:','kloppy'),('DataBallPy:','distance')]:
                    if t.text.startswith(prefix):key=k
            target=sources[key][1] if key else None
            if s.get("notebook") and t.text == s.get("cue"):
                target="https://github.com/zcochran27/tracking-data-applied-workshop/blob/main/"+s["notebook"]
            if not target:continue
            rid='rIdWorkshop'+str(len(rels)+1)
            E.SubElement(rels,f'{{{REL}}}Relationship',{'Id':rid,'Type':R+'/hyperlink','Target':target,'TargetMode':'External'})
            props=run.find(f'{{{A}}}rPr')
            if props is None:props=E.Element(f'{{{A}}}rPr');run.insert(0,props)
            E.SubElement(props,f'{{{A}}}hlinkClick',{f'{{{R}}}id':rid})
    files[name]=E.tostring(tree,encoding='utf-8',xml_declaration=True)
    files[relname]=E.tostring(rels,encoding='utf-8',xml_declaration=True)
with zipfile.ZipFile(deck,'w',zipfile.ZIP_DEFLATED) as z:
    for n,b in files.items():z.writestr(n,b)
