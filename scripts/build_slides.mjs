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
const optionsMode=process.argv.includes('--formation-options');
const deckStem=optionsMode?'formation-options':'tracking-data-applied';
const contentPath=path.join(root,optionsMode?'slides/formation-options.json':'slides/content.json');
const content=JSON.parse(await fs.readFile(contentPath,'utf8'));
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
 if(c.layout==='section'){
   text(s,c.section||'ANALYTICAL AVENUE',50,44,1150,30,14,accent,true);
   text(s,c.title,50,112,1160,85,52,ink,true);
   text(s,c.problem,50,218,1130,92,30,ink);
   text(s,c.ideasLabel||'Questions to explore',50,352,400,36,20,accent,true);
   c.ideas.forEach((idea,j)=>text(s,'• '+idea,50+(j%2)*590,409+Math.floor(j/2)*65,550,60,24,ink));
   text(s,c.result||'',50,612,1160,45,21,accent,true);
 }else if(c.layout==='overview'){
   text(s,c.title,50,55,1150,85,46,ink,true);
   text(s,c.problem,50,153,1160,62,25);
   c.avenues.forEach((a,j)=>{
     const y=240+j*74;
     text(s,a.name,50,y,460,45,25,accent,true);
     text(s,a.question,530,y,680,54,23,ink);
   });
 }else if(c.layout==='cover'){
   text(s,'SOCCER ANALYTICS · SKILLCORNER OPEN DATA',50,52,1180,30,15,accent,true);
   text(s,c.title,50,112,1180,100,62,ink,true);
   text(s,c.problem,50,240,520,150,34);
   const bytes=await fs.readFile(path.join(root,'assets',c.image));
   s.images.add({blob:bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.byteLength),contentType:'image/png',alt:c.title,fit:'contain',position:{left:595,top:230,width:640,height:360}});
   text(s,c.result,50,538,470,85,25,accent,true);
 }else{
   text(s,c.section||'TRACKING DATA APPLIED',48,29,1160,26,13,accent,true);
   text(s,c.title,48,62,1184,75,38,ink,true);
   text(s,'Problem',48,158,232,28,15,accent,true);
   text(s,c.problem,48,190,232,136,22);
   text(s,'Methods',48,348,232,28,15,accent,true);
   text(s,c.methods,48,380,232,150,20);
   if(c.status)text(s,c.status,48,547,232,65,13,'#65756d');
   if(!c.image)throw new Error(`Missing result visual: ${c.title}`);
   const bytes=await fs.readFile(path.join(root,'assets',c.image));
   s.images.add({blob:bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.byteLength),contentType:'image/png',alt:c.title,fit:'contain',position:{left:310,top:150,width:930,height:c.video?432:455}});
   if(c.video)text(s,'▶ Click video to play',330,587,870,24,14,accent,true);
   text(s,c.result||'',48,623,1184,40,22,accent,true);
 }
 if(c.cue)text(s,c.cue,730,675,460,27,13,accent,true);
 c.sources.forEach((k,j)=>text(s,sources[k][0],48+j*(650/Math.max(1,c.sources.length)),675,630/Math.max(1,c.sources.length),30,10,'#51645c'));
 text(s,`${i+1}`,1212,675,40,27,13,'#51645c');
 s.speakerNotes.text=c.notes+'\n\n'+(c.cue||'')+(c.notebook?'\nhttps://github.com/zcochran27/tracking-data-applied-workshop/blob/main/'+c.notebook:'')+(c.video?'\nEmbedded video (click to play): '+c.video+'\n'+(c.videoDescription||''):'')+'\n\nSources:\n'+c.sources.map(k=>sources[k].join('\n')).join('\n\n');
}
await fs.mkdir(path.join(root,'.build'),{recursive:true});
await fs.mkdir(path.join(root,'slides/previews'),{recursive:true});
const candidate=path.join(root,`.build/${deckStem}-candidate.pptx`);
await (await PresentationFile.exportPptx(p)).save(candidate);
const links=spawnSync(python,[path.join(root,'scripts/add_source_links.py'),candidate,contentPath],{encoding:'utf8'});
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
const validated=path.join(root,`.build/export-${Date.now()}/${deckStem}.pptx`);
await fs.mkdir(path.dirname(validated),{recursive:true});
await finalizePresentation({workspaceDir:root,candidatePath:candidate,finalPath:validated,
 pythonExecutable:python,integrityValidatorPath:path.join(skill,'container_tools/inspect_presentation_package_integrity.py'),
 layoutValidatorPath:path.join(skill,'container_tools/inspect_presentation_layout_geometry.py'),
 layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-bullet-geometry','--validate-heading-fit'],
 fontPolicy:{basis:'design',families:['Arial']},verifyArtifactToolImport:true,
 receiptPath:path.join(root,`.build/${optionsMode?'formation-options':'presentation'}-validation-${Date.now()}.json`)});
try {
 await fs.copyFile(validated,path.join(root,`slides/${deckStem}.pptx`));
} catch(error) {
 if(!['EBUSY','EPERM'].includes(error.code))throw error;
 const alternate=path.join(root,`slides/${deckStem}-updated.pptx`);
 await fs.copyFile(validated,alternate);
 console.log('Open presentation is locked; saved updated copy:',alternate);
}
if(optionsMode){
 const dest=path.join(root,'slides/formation-options-previews');await fs.mkdir(dest,{recursive:true});
 for(const name of await fs.readdir(renderDir))await fs.copyFile(path.join(renderDir,name),path.join(dest,name));
}else{
 const previews=spawnSync('python',[path.join(root,'scripts/publish_previews.py'),renderDir],{encoding:'utf8'});
 if(previews.status!==0)throw new Error(previews.stderr);
}
console.log('Final PPTX validated');
