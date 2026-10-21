"""Add source/notebook hyperlinks and native, self-contained MP4 movie objects."""
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
P14='http://schemas.microsoft.com/office/powerpoint/2010/main'
E.register_namespace('a',A);E.register_namespace('p',P);E.register_namespace('r',R)
E.register_namespace('p14',P14)
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
    if s.get('video'):
        video=(root/s['video']).resolve();video.relative_to(root)
        assert video.is_file() and video.suffix=='.mp4',video
        media_name='workshop_'+video.name
        files['ppt/media/'+media_name]=video.read_bytes()
        pic=tree.find(f'.//{{{P}}}pic')
        assert pic is not None, 'Movie needs a poster image'
        props=pic.find(f'{{{P}}}nvPicPr/{{{P}}}cNvPr')
        props.set('name','Video: '+s['title'])
        props.set('descr','Embedded MP4. Click to play. '+s.get('videoDescription',s['title']))
        # CT_NonVisualDrawingProps requires click actions BEFORE extLst.
        # Appending after artifact-tool's creationId extension breaks native playback.
        click=E.Element(f'{{{A}}}hlinkClick',{'action':'ppaction://media'})
        props.insert(0,click)
        nv=pic.find(f'{{{P}}}nvPicPr/{{{P}}}nvPr')
        video_id='rIdWorkshopVideo';media_id='rIdWorkshopMedia'
        E.SubElement(rels,f'{{{REL}}}Relationship',{'Id':video_id,'Type':R+'/video','Target':'../media/'+media_name})
        E.SubElement(rels,f'{{{REL}}}Relationship',{'Id':media_id,'Type':'http://schemas.microsoft.com/office/2007/relationships/media','Target':'../media/'+media_name})
        E.SubElement(nv,f'{{{A}}}videoFile',{f'{{{R}}}link':video_id})
        extlist=E.SubElement(nv,f'{{{P}}}extLst')
        # This is PowerPoint's registered embedded-media extension identifier.
        ext=E.SubElement(extlist,f'{{{P}}}ext',{'uri':'{DAA4B4D4-6D71-4841-9C94-3DE7FCFB9230}'})
        E.SubElement(ext,f'{{{P14}}}media',{f'{{{R}}}embed':media_id})
        timing=E.SubElement(tree,f'{{{P}}}timing');tnlist=E.SubElement(timing,f'{{{P}}}tnLst')
        par=E.SubElement(tnlist,f'{{{P}}}par');ctn=E.SubElement(par,f'{{{P}}}cTn',{'id':'1','dur':'indefinite','restart':'never','nodeType':'tmRoot'})
        children=E.SubElement(ctn,f'{{{P}}}childTnLst');vid=E.SubElement(children,f'{{{P}}}video')
        node=E.SubElement(vid,f'{{{P}}}cMediaNode',{'vol':'80000'})
        ct=E.SubElement(node,f'{{{P}}}cTn',{'id':'2','fill':'hold','display':'0'})
        conds=E.SubElement(ct,f'{{{P}}}stCondLst');E.SubElement(conds,f'{{{P}}}cond',{'delay':'indefinite'})
        target=E.SubElement(node,f'{{{P}}}tgtEl');E.SubElement(target,f'{{{P}}}spTgt',{'spid':props.get('id')})
    files[name]=E.tostring(tree,encoding='utf-8',xml_declaration=True)
    files[relname]=E.tostring(rels,encoding='utf-8',xml_declaration=True)
CT='http://schemas.openxmlformats.org/package/2006/content-types'
E.register_namespace('',CT)
types=E.fromstring(files['[Content_Types].xml'])
if any(s.get('video') for s in content) and not any(x.get('Extension')=='mp4' for x in types):
    E.SubElement(types,f'{{{CT}}}Default',{'Extension':'mp4','ContentType':'video/mp4'})
files['[Content_Types].xml']=E.tostring(types,encoding='utf-8',xml_declaration=True)
with zipfile.ZipFile(deck,'w',zipfile.ZIP_DEFLATED) as z:
    for n,b in files.items():z.writestr(n,b)
