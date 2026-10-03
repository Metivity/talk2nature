// Filters act on curated literature records, never on private app sessions.
export function filterAtlas(records,{query='',group='all',place='all',period='all',selected=[]}={}) {
  const terms=query.trim().toLowerCase().split(/\s+/).filter(Boolean);
  return records.filter(r=>{
    const places=r.locations.map(l=>l.place_id);
    const location=place==='all'||(place==='mapped'?places.length>0:place==='unmapped'?places.length===0:place==='selection'?places.some(p=>selected.includes(p)):places.includes(place));
    const time=period==='all'||(period==='early'?r.source_year<2000:period==='middle'?r.source_year>=2000&&r.source_year<2020:period==='recent'?r.source_year>=2020:false);
    const haystack=[r.title,r.taxon,r.kind,r.finding,r.location_note,...(r.place_labels||[]),...r.locations.map(l=>l.basis),r.observation_period?.label||''].join(' ').toLowerCase();
    return location&&time&&(group==='all'||r.group===group)&&terms.every(t=>haystack.includes(t));
  });
}
export function mapClusters(records,places,width) {
  if(!Number.isFinite(width)||width<=0)throw Error('A visible map width is required.');
  const scale=width/1000, nodes=[];
  for(const place of places){const ids=records.filter(r=>r.locations.some(l=>l.place_id===place.id)).map(r=>r.id);if(ids.length)nodes.push({x:(place.longitude+180)/360*1000,y:(90-place.latitude)/180*500,places:[place.id],records:[...new Set(ids)]});}
  // Merge the nearest hit targets until mobile controls no longer overlap.
  for(;;){let pair=null,distance=52;
    for(let i=0;i<nodes.length;i++)for(let j=i+1;j<nodes.length;j++){
      const d=Math.hypot(nodes[i].x-nodes[j].x,nodes[i].y-nodes[j].y)*scale;
      if(d<distance){distance=d;pair=[i,j];}
    }
    if(!pair)break;
    const [i,j]=pair,a=nodes[i],b=nodes[j],n=a.places.length+b.places.length;
    nodes[i]={x:(a.x*a.places.length+b.x*b.places.length)/n,y:(a.y*a.places.length+b.y*b.places.length)/n,places:[...a.places,...b.places].sort(),records:[...new Set([...a.records,...b.records])].sort()};nodes.splice(j,1);
  }
  return nodes;
}
