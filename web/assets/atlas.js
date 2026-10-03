import {filterAtlas,mapClusters} from './atlas-model.mjs';
const $=id=>document.getElementById(id);
async function start(){
  try{
    const response=await fetch('./catalog.json',{credentials:'omit'});if(!response.ok)throw Error('Catalog unavailable.');
    const data=await response.json();if(data.schema!=='talk2nature.atlas.v1'||data.visibility!=='public_literature_metadata')throw Error('Unsupported catalog.');
    const fields={query:$('atlas-search'),group:$('atlas-group'),place:$('atlas-place'),period:$('atlas-period')};
    const cards=[...document.querySelectorAll('.atlas-record')], names=new Map(data.places.map(p=>[p.id,p.label]));
    let selected=[],shown=data.records;
    function pins(){
      const focused=document.activeElement?.dataset?.places;
      $('atlas-pins').replaceChildren();
      const clusters=mapClusters(shown,data.places,$('atlas-map').clientWidth||320);
      for(const cluster of clusters){
        const button=document.createElement('button');button.type='button';button.className='atlas-pin';
        button.style.left=`${cluster.x/10}%`;button.style.top=`${cluster.y/5}%`;
        button.textContent=String(cluster.records.length);button.dataset.places=cluster.places.join(',');
        const label=cluster.places.map(p=>names.get(p)).join(' + ');
        button.title=label;button.setAttribute('aria-label',`${label}: ${cluster.records.length} evidence note${cluster.records.length===1?'':'s'}. Filter timeline to this region group.`);
        button.setAttribute('aria-pressed',String(fields.place.value==='selection'&&cluster.places.every(p=>selected.includes(p))));
        button.addEventListener('click',()=>{selected=cluster.places;$('atlas-selection-option').hidden=false;$('atlas-selection-option').textContent=label;fields.place.value='selection';update();$('atlas-place').focus({preventScroll:true});$('atlas-controls').scrollIntoView({behavior:'auto',block:'start'});});
        $('atlas-pins').append(button);
      }
      if(focused){const replacement=[...$('atlas-pins').children].find(p=>p.dataset.places===focused);replacement?.focus({preventScroll:true});}
      const located=shown.filter(r=>r.locations.length).length;
      $('atlas-map-status').textContent=`${located} mapped note${located===1?'':'s'} in this view · ${shown.length-located} without a pin. ${located?'Choose a pin or use the region filter.':'The timeline still includes matching unmapped work.'}`;
    }
    function update(){
      shown=filterAtlas(data.records,{query:fields.query.value,group:fields.group.value,place:fields.place.value,period:fields.period.value,selected});
      const ids=new Set(shown.map(r=>r.id));cards.forEach(card=>card.hidden=!ids.has(card.dataset.id));
      $('atlas-count').textContent=`${shown.length} of ${data.records.length} evidence notes · source years, oldest first`;
      $('atlas-empty').hidden=shown.length!==0;pins();
    }
    fields.query.addEventListener('input',update);
    for(const key of ['group','place','period'])fields[key].addEventListener('change',()=>{if(key==='place'&&fields.place.value!=='selection'){selected=[];$('atlas-selection-option').hidden=true;}update();});
    $('atlas-reset').addEventListener('click',()=>{fields.query.value='';for(const k of ['group','place','period'])fields[k].value='all';selected=[];$('atlas-selection-option').hidden=true;update();fields.query.focus({preventScroll:true});});
    $('atlas-controls').hidden=false;update();
    let previousWidth=$('atlas-map').clientWidth;
    if(typeof ResizeObserver!=='undefined')new ResizeObserver(entries=>{const width=entries[0].contentRect.width;if(width>0&&Math.abs(width-previousWidth)>1){previousWidth=width;pins();}}).observe($('atlas-map'));
    else window.addEventListener('resize',pins);
  }catch{
    $('atlas-map-status').textContent='Interactive map unavailable. All notes, locations and sources remain readable below.';
    $('atlas-controls').hidden=true;$('atlas-pins').replaceChildren();
    document.querySelectorAll('.atlas-record').forEach(r=>r.hidden=false);
  }
}
start();
