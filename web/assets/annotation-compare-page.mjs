import {compareAnnotations,parseAnnotationText} from './annotation-compare.mjs';
import {showFileSelection} from './file-picker.mjs';

const $=id=>document.getElementById(id);
const selected={a:null,b:null};
const selectionVersion={a:0,b:0};
let currentReport=null, reportUrl=null;
const node=(tag,text,className)=>{const e=document.createElement(tag);if(text!==undefined)e.textContent=text;if(className)e.className=className;return e;};
const fmt=n=>`${Number(n).toFixed(2)} s`;
function revokeReport(){if(reportUrl)URL.revokeObjectURL(reportUrl);reportUrl=null;}
function resetResults(){currentReport=null;revokeReport();$('annotation-compare-results').hidden=true;$('annotation-report-download').disabled=true;}
function state(){
  $('annotation-compare-clear').disabled=!(selected.a||selected.b);
  if(!selected.a||!selected.b){resetResults();return;}
  try{
    currentReport=compareAnnotations(selected.a,selected.b);
    $('annotation-compare-error').textContent='';
    render(currentReport);
  }catch(error){resetResults();$('annotation-compare-error').textContent=error.message;}
}
function card(value,label){const e=node('div',undefined,'annotation-compare-stat');e.append(node('strong',String(value)),node('span',label));return e;}
function render(report){
  const summary=$('annotation-compare-summary'),tbody=$('annotation-compare-pairs'),mobilePairs=$('annotation-compare-mobile-pairs');
  summary.replaceChildren(card(report.annotation_counts.a,'events in A'),card(report.annotation_counts.b,'events in B'),card(report.positive_overlap_pair_count,'positive-overlap pairs'));
  tbody.replaceChildren();mobilePairs.replaceChildren();
  if(!report.pairwise_overlaps.length){
    const message='No positive interval overlaps. This does not establish that no sound occurred.';
    const row=node('tr'),cell=node('td',message);cell.colSpan=7;row.append(cell);tbody.append(row);
    const empty=node('article',undefined,'annotation-compare-mobile-card');empty.append(node('h3','No positive interval overlaps'),node('p',message));mobilePairs.append(empty);
  }
  for(const pair of report.pairwise_overlaps){
    const row=node('tr'),kindClass=pair.kind_exact_match?'annotation-match':'annotation-difference';
    const kindA=node('td',pair.kind_a,kindClass),kindB=node('td',pair.kind_b,kindClass);
    const context=pair.context_comparison==='same_declared_category'?`Same: ${pair.context_a}`:pair.context_comparison==='different_declared_category'?`${pair.context_a} / ${pair.context_b}`:'Not comparable';
    const eventA=node('th',`#${pair.event_a_id}`);eventA.scope='row';
    row.append(eventA,node('td',`#${pair.event_b_id}`),node('td',`${fmt(pair.overlap_start_seconds)}–${fmt(pair.overlap_end_seconds)} · ${fmt(pair.overlap_seconds)}`),node('td',pair.temporal_iou.toFixed(3)),kindA,kindB,node('td',context));tbody.append(row);
    const mobile=node('article',undefined,'annotation-compare-mobile-card');
    mobile.append(node('h3',`A #${pair.event_a_id}  ↔  B #${pair.event_b_id}`));
    const details=node('dl');
    const detail=(label,value)=>{const item=node('div');item.append(node('dt',label),node('dd',value));return item;};
    const kinds=node('div');kinds.append(node('dt','Sound-kind labels'));
    const kindValues=node('dd');kindValues.append(node('span',`A · ${pair.kind_a}`,kindClass),node('span',`B · ${pair.kind_b}`,kindClass));kinds.append(kindValues);
    details.append(detail('Interval overlap',`${fmt(pair.overlap_start_seconds)}–${fmt(pair.overlap_end_seconds)} · ${fmt(pair.overlap_seconds)}`),detail('Time IoU',pair.temporal_iou.toFixed(3)),kinds,detail('Observed context',context));
    mobile.append(details);mobilePairs.append(mobile);
  }
  const ids=(values)=>values.length?values.map(id=>`#${id}`).join(', '):'None';
  $('annotation-unmatched-a').textContent=ids(report.event_ids_without_positive_overlap.a);
  $('annotation-unmatched-b').textContent=ids(report.event_ids_without_positive_overlap.b);
  $('annotation-compare-results').hidden=false;$('annotation-report-download').disabled=false;
}
async function openFile(key,file){
  if(!file)return;
  showFileSelection($('annotation-file-'+key),file);
  const version=++selectionVersion[key];
  selected[key]=null;resetResults();$('annotation-compare-error').textContent='';$('annotation-status-'+key).textContent='Checking this local file…';
  try{
    if(file.size>2*1024*1024)throw Error('Choose an annotation file smaller than 2 MB.');
    const document=parseAnnotationText(await file.text());
    if(version!==selectionVersion[key])return;
    selected[key]=document;
    $('annotation-status-'+key).textContent=`Ready · ${document.events.length} declared event${document.events.length===1?'':'s'}.`;
    state();
  }catch(error){
    if(version!==selectionVersion[key])return;
    $('annotation-status-'+key).textContent='No valid file selected.';
    $('annotation-compare-error').textContent=error.message;
  }finally{if(version===selectionVersion[key])$('annotation-file-'+key).value='';}
}
for(const key of ['a','b'])$('annotation-file-'+key).addEventListener('change',event=>openFile(key,event.target.files?.[0]));
$('annotation-compare-clear').addEventListener('click',()=>{
  for(const key of ['a','b'])selectionVersion[key]++;
  selected.a=null;selected.b=null;resetResults();$('annotation-compare-error').textContent='';$('annotation-download-status').textContent='';
  for(const key of ['a','b']){showFileSelection($('annotation-file-'+key),null);$('annotation-file-'+key).value='';$('annotation-status-'+key).textContent='Nothing selected.';}
  $('annotation-file-a').focus();
});
$('annotation-report-download').addEventListener('click',()=>{
  if(!currentReport)return;
  revokeReport();reportUrl=URL.createObjectURL(new Blob([JSON.stringify(currentReport,null,2)+'\n'],{type:'application/json'}));
  const anchor=node('a');anchor.href=reportUrl;anchor.download='talk2nature-annotation-comparison.json';anchor.click();
  $('annotation-download-status').textContent='Report downloaded to your device. Inspect it before sharing.';
});
window.addEventListener('pagehide',()=>{selected.a=null;selected.b=null;currentReport=null;revokeReport();});
