import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {spawnSync} from 'node:child_process';

const root=path.resolve(import.meta.dirname,'..');
const runtime=process.env.WORKSHOP_NODE_MODULES || 'C:/Users/zcoch/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules';
process.env.RUNTIME_NODE_MODULES=runtime;
const skill=process.env.WORKSHOP_SLIDES_SKILL || 'C:/Users/zcoch/.codex/plugins/cache/openai-primary-runtime/presentations/26.1015.12040/skills/presentations';
const python=process.env.WORKSHOP_RUNTIME_PYTHON || 'C:/Users/zcoch/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe';
const {Presentation,PresentationFile}=await import(pathToFileURL(path.join(runtime,'@oai/artifact-tool/dist/artifact_tool.mjs')).href);
const content=JSON.parse(await fs.readFile(path.join(root,'slides/content.json'),'utf8'));
const sources=JSON.parse(await fs.readFile(path.join(root,'resources/sources.json'),'utf8'));
const p=Presentation.create({slideSize:{width:1280,height:720}});
const ink='#183a35',accent='#147d68',orange='#e87524';
function text(s,body,x,y,w,h,size=28,color=ink,bold=false){
 const t=s.shapes.add({geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});
 t.text=body;t.text.style={typeface:'Arial',fontSize:size,color,bold};return t;
}
function rect(s,x,y,w,h,fill){return s.shapes.add({geometry:'rect',position:{left:x,top:y,width:w,height:h},fill,line:{fill:'none',width:0}});}
function node(s,label,x,y,w=250){rect(s,x,y,w,76,'#e0eee8');text(s,label,x+15,y+8,w-30,65,22,ink,true);}
for(let i=0;i<content.length;i++){
 const c=content[i],s=p.slides.add();s.background.fill='#fbfcf8';
 rect(s,0,0,1280,12,accent);
 text(s,c.title,60,42,1160,85,i===0?50:40,ink,true);
 c.body.forEach((b,j)=>{
   text(s,String(j+1).padStart(2,'0'),55,151+j*140,40,28,16,accent,true);
   text(s,b,55,185+j*140,340,109,25);
 });
 if(!c.image)throw new Error(`Missing method visual: ${c.title}`);
 const bytes=await fs.readFile(path.join(root,'assets',c.image));
 s.images.add({blob:bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.byteLength),contentType:'image/png',alt:c.title,fit:'contain',position:{left:430,top:c.video?145:140,width:800,height:c.video?420:455}});
 if(c.cue){rect(s,60,600,1160,43,'#e0eee8');text(s,c.cue,78,608,1120,34,22,accent,true);}
 if(c.video)text(s,'▶ Click the video to play · embedded MP4',450,574,760,24,15,accent,true);
 c.sources.forEach((k,j)=>text(s,sources[k][0],60+j*(1080/c.sources.length),657,1060/c.sources.length,40,12,'#51645c'));
 text(s,`${i+1} / ${content.length}`,1165,657,90,30,14,'#51645c');
 s.speakerNotes.text=c.notes+'\n\n'+(c.cue||'')+(c.notebook?'\nhttps://github.com/zcochran27/tracking-data-applied-workshop/blob/main/'+c.notebook:'')+(c.video?'\nEmbedded video (click to play): '+c.video+'\n'+(c.videoDescription||''):'')+'\n\nSources:\n'+c.sources.map(k=>sources[k].join('\n')).join('\n\n');
}
await fs.mkdir(path.join(root,'.build'),{recursive:true});
await fs.mkdir(path.join(root,'slides/previews'),{recursive:true});
const candidate=path.join(root,'.build/candidate.pptx');
await (await PresentationFile.exportPptx(p)).save(candidate);
const links=spawnSync(python,[path.join(root,'scripts/add_source_links.py'),candidate],{encoding:'utf8'});
if(links.status!==0)throw new Error(links.stderr);
console.log('Exported draft');
const renderDir=path.join(root,`.build/previews-${Date.now()}`);
await fs.mkdir(renderDir,{recursive:true});
for(let i=0;i<p.slides.items.length;i++){
 const blob=await p.export({slide:p.slides.items[i],format:'png',scale:1});
 const name=`${String(i+1).padStart(2,'0')}.png`;
 await fs.writeFile(path.join(renderDir,name),new Uint8Array(await blob.arrayBuffer()));
 console.log('Rendered',i+1);
}
const {finalizePresentation}=await import(pathToFileURL(path.join(skill,'container_tools/artifact_tool_utils.mjs')).href);
const validated=path.join(root,`.build/export-${Date.now()}/tracking-data-applied.pptx`);
await fs.mkdir(path.dirname(validated),{recursive:true});
await finalizePresentation({workspaceDir:root,candidatePath:candidate,finalPath:validated,
 pythonExecutable:python,integrityValidatorPath:path.join(skill,'container_tools/inspect_presentation_package_integrity.py'),
 layoutValidatorPath:path.join(skill,'container_tools/inspect_presentation_layout_geometry.py'),
 layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-bullet-geometry','--validate-heading-fit'],
 fontPolicy:{basis:'design',families:['Arial']},verifyArtifactToolImport:true,
 receiptPath:path.join(root,`.build/presentation-validation-${Date.now()}.json`)});
await fs.copyFile(validated,path.join(root,'slides/tracking-data-applied.pptx'));
const previews=spawnSync('python',[path.join(root,'scripts/publish_previews.py'),renderDir],{encoding:'utf8'});
if(previews.status!==0)throw new Error(previews.stderr);
console.log('Final PPTX validated');
