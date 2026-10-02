let csrf = '';
let records = [];
let studies = [], studySessions = [], evidence = [];
const status = document.querySelector('#status');
function report(message) { status.textContent = message; }
function element(tag, text, className) {
  const item = document.createElement(tag);
  if (text !== undefined) item.textContent = text;
  if (className) item.className = className;
  return item;
}
async function api(path, body) {
  const response = await fetch(path, {method: body === undefined ? 'GET' : 'POST', credentials:'same-origin', cache:'no-store', headers:body === undefined ? {} : {'Content-Type':'application/json','X-CSRF-Token':csrf}, body:body === undefined ? undefined : JSON.stringify(body)});
  if (response.status === 401) { location.assign('/'); throw new Error('Your session has ended.'); }
  const result = await response.json();
  if (!response.ok) throw new Error(result.detail || 'The request could not be completed.');
  return result;
}
function action(label, fn, className) {
  const button = element('button', label, className);
  button.type = 'button';
  button.addEventListener('click', async () => {
    button.disabled = true;
    try { await fn(); } catch(error) { report(error.message); }
    finally { if (button.isConnected) button.disabled = false; }
  });
  return button;
}
function card(record) {
  const item = element('article', undefined, 'observation');
  const top = element('div', undefined, 'card-heading');
  top.append(element('h3', record.species || 'Withdrawn observation'), element('span', record.state, 'badge ' + record.state));
  item.append(top);
  if (record.state === 'withdrawn') { item.append(element('p','Active metadata removed. Dependent releases are revoked.','small')); return item; }
  item.append(element('p', `${record.individual_id} · ${record.session_id}`, 'small'));
  item.append(element('p', `${record.context} · ${record.label_source.replaceAll('_', ' ')} · ${new Date(record.recorded_at).toLocaleString()}`));
  if(record.note) item.append(element('p', record.note, 'field-note'));
  item.append(element('p', `Rights: ${record.rights} · ${record.rights_evidence || 'Evidence missing'}`, 'small'));
  item.append(element('p', `Training: ${record.consent_training ? 'permitted' : 'not permitted'} · Publication consideration: ${record.consent_publication ? 'permitted' : 'not permitted'}`, 'small'));
  if(record.review) item.append(element('p', `Owner review recorded ${new Date(record.review.reviewed_at*1000).toLocaleString()} · observation version ${record.review.source_version}`, 'small'));
  item.append(element('p', record.study ? `Study: ${record.study.title} · protocol v${record.study.protocol_version}` : 'Standalone observation from the earlier rehearsal workflow', 'small'));
  const controls = element('div', undefined, 'card-actions');
  if(record.state === 'quarantined') {
    const fieldset = element('fieldset'); fieldset.append(element('legend','Review checklist'));
    const checks = {};
    for (const [key, text] of [['rights_checked','Rights evidence checked'],['consent_checked','Permissions checked'],['privacy_checked','Privacy checked'],['label_checked','Context independently observed']]) {
      const label = element('label',undefined,'check'); const input = element('input'); input.type='checkbox'; checks[key] = input; label.append(input,document.createTextNode(text)); fieldset.append(label);
    }
    item.append(fieldset);
    controls.append(action('Accept for research review', async () => {
      await api(`/api/observations/${record.id}/review`, {version:record.version, decision:'accept',...Object.fromEntries(Object.entries(checks).map(([k,v])=>[k,v.checked]))});
      await refresh(); report('Observation accepted. A training release still requires explicit training permission.');
    }));
    controls.append(action('Reject', async()=>{ await api(`/api/observations/${record.id}/review`, {version:record.version, decision:'reject'}); await refresh(); report('Observation rejected.');},'quiet'));
  }
  controls.append(action('Withdraw metadata',async()=>{
    // A second local action makes loss of active metadata explicit.
    const confirm = action('Confirm withdrawal',async()=>{const result=await api(`/api/observations/${record.id}/withdraw`,{version:record.version});await refresh();report(result.notice);},'danger');
    controls.replaceChildren(element('span','Remove this metadata and revoke dependent releases?'), confirm, action('Cancel',refresh,'quiet'));
  },'quiet'));
  item.append(controls); return item;
}
async function refresh() {
  const [observations, releases, audit, studyRows, sessionRows, evidenceRows] = await Promise.all([api('/api/observations'),api('/api/releases'),api('/api/audit'),api('/api/studies'),api('/api/study-sessions'),api('/api/evidence')]);
  studies=studyRows;studySessions=sessionRows;evidence=evidenceRows;renderStudies();
  records = observations;
  document.querySelector('#waiting').textContent=records.filter(r=>r.state==='quarantined').length;
  document.querySelector('#accepted').textContent=records.filter(r=>['accepted','released'].includes(r.state)).length;
  document.querySelector('#releases-count').textContent=releases.filter(r=>!r.revoked).length;
  const queue=document.querySelector('#queue'); queue.replaceChildren(...records.map(card));
  if(!records.length) queue.append(element('p','Your queue is empty. Rehearse an observation to try the review workflow.','empty'));
  document.querySelector('#release').disabled=!records.some(r=>r.state==='accepted' && r.consent_training);
  const list=document.querySelector('#release-list'); list.replaceChildren();
  for(const r of releases) {
    const row=element('div',undefined,'release-row');row.append(element('span',`${r.count} observation${r.count===1?'':'s'} · ${r.revoked?'Revoked':'Active'}`));
    if(!r.revoked) {const a=element('a','View private metadata');a.href=`/api/releases/${r.id}`;a.target='_blank';a.rel='noopener';row.append(a);}
    list.append(row);
  }
  document.querySelector('#audit-list').replaceChildren(...audit.map(a=>element('li',`${new Date(a.created*1000).toLocaleString()} · ${a.action.replaceAll('_',' ')}`)));
}
document.querySelector('#observation-form').addEventListener('submit',async event=>{
  event.preventDefault(); const form=event.target; const button=form.querySelector('button'); button.disabled=true;
  try {
    const data=Object.fromEntries(new FormData(form));
    for(const key of ['consent_review','consent_training','consent_publication','synthetic'])data[key]=form.elements[key].checked;
    data.recorded_at=new Date(data.recorded_at).toISOString();
    await api('/api/observations',data);form.reset();setTime();await refresh();report('Observation received and quarantined for review.');status.focus();
  } catch(error) {report(error.message);} finally {button.disabled=false;}
});
function localTime() {const now=new Date();return new Date(now.getTime()-now.getTimezoneOffset()*60000).toISOString().slice(0,16);}
function setTime() {document.querySelector('[name="recorded_at"]').value=localTime();}
document.querySelector('#refresh').addEventListener('click',()=>refresh().catch(e=>report(e.message)));
document.querySelector('#release').addEventListener('click',async event=>{event.target.disabled=true;try{await api('/api/releases',{ids:records.filter(r=>r.state==='accepted' && r.consent_training).map(r=>r.id)});await refresh();report('A private synthetic metadata release was created. No model training was run.');}catch(e){report(e.message);event.target.disabled=false;}});
document.querySelector('#logout').addEventListener('click',async()=>{try{await api('/auth/logout',{});location.assign('/');}catch(e){report(e.message);}});
function fillSelect(select, choices, empty, defaultFirst=false) {
  const previous=select.value;
  const placeholder=element('option',empty);placeholder.value='';
  select.replaceChildren(placeholder,...choices.map(([value,title])=>{const option=element('option',title);option.value=value;return option;}));
  select.value=choices.some(([value])=>value===previous)?previous:(defaultFirst&&choices.length?choices[0][0]:'');
}
function sessionGuidance() {
  const form=document.querySelector('#observation-form');
  const session=studySessions.find(s=>s.id===form.elements.study_session_id.value);
  const study=studies.find(s=>s.id===session?.study_id);
  form.elements.species.value=study?.payload.species||'';
  form.elements.individual_id.value=session?.payload.individual_id||'';
  form.elements.session_id.value=session?.id||'';
  document.querySelector('#session-guidance').textContent=study?`${study.payload.protocol} Stop: ${study.payload.stop_rule}`:'Start a session above to connect your observation to a protocol.';
  const previous=form.elements.context.value;
  const unknown=element('option','Unknown / unclear');unknown.value='unknown';
  form.elements.context.replaceChildren(unknown,...Object.entries(study?.payload.codebook||{}).map(([key,definition])=>{const option=element('option',`${key}: ${definition}`);option.value=key;return option;}));
  form.elements.context.value=study?.payload.codebook[previous]?previous:'unknown';
}
function renderStudies() {
  document.querySelector('#evidence-count').textContent=`${evidence.length} catalog records in database`;
  fillSelect(document.querySelector('#study-evidence'), evidence.filter(e=>e.kind!=='source').map(e=>[e.key,e.title]),'Choose a reviewed resource or note');
  fillSelect(document.querySelector('#session-study'),studies.filter(s=>s.state==='active').map(s=>[s.id,s.payload.title]),'Choose an active study');
  fillSelect(document.querySelector('#observation-session'),studySessions.filter(s=>s.state==='open').map(s=>[s.id,`${studies.find(t=>t.id===s.study_id)?.payload.title||'Study'} · ${s.payload.individual_id}`]),'Choose an open session',true);
  sessionGuidance();
  const list=document.querySelector('#study-list');list.replaceChildren();
  if(!studies.length)list.append(element('p','Create a study draft, check its protocol, then activate the synthetic rehearsal.','empty'));
  for(const study of studies) {
    const article=element('article',undefined,'observation');
    article.append(element('h3',study.payload.title),element('p',`${study.payload.species} · ${study.state}`,'small'),element('p',study.payload.question));
    const details=element('details');details.append(element('summary','Protocol and evidence'),element('p',study.payload.protocol),element('p',`Stop rule: ${study.payload.stop_rule}`));
    for(const [key,value] of Object.entries(study.payload.codebook))details.append(element('p',`${key}: ${value}`,'small'));
    for(const ref of study.evidence) {
      const link=element('a',`Read saved evidence: ${evidence.find(e=>e.key===ref.evidence_key)?.title||ref.evidence_key}`);
      link.href=`/api/evidence/${encodeURIComponent(ref.evidence_key)}/versions/${ref.fingerprint}`;link.target='_blank';link.rel='noopener';
      details.append(link,element('br'));
    }
    article.append(details);
    if(study.state==='draft')article.append(action('Activate synthetic study',async()=>{await api(`/api/studies/${study.id}/activate`,{version:study.version});await refresh();report('Synthetic study activated. The protocol is frozen; real participants remain disabled.');}));
    list.append(article);
  }
  const sessions=document.querySelector('#session-list');sessions.replaceChildren();
  for(const session of studySessions) {
    const row=element('div',undefined,'release-row');row.append(element('span',`${session.payload.individual_id} · ${session.state} · ${new Date(session.payload.started_at).toLocaleString()}`));
    if(session.state==='open')row.append(action('Close session',async()=>{await api(`/api/study-sessions/${session.id}/close`,{version:session.version});await refresh();report('Session closed. Existing observations remain available for review.');},'quiet'));
    sessions.append(row);
  }
}
document.querySelector('#observation-session').addEventListener('change',sessionGuidance);
document.querySelector('#study-form').addEventListener('submit',async event=>{
  event.preventDefault();const form=event.target, button=form.querySelector('button');button.disabled=true;
  try {
    const fields=Object.fromEntries(new FormData(form));
    const codebook=Object.fromEntries(['resting','moving','feeding','social'].filter(k=>fields[k].trim()).map(k=>[k,fields[k].trim()]));
    if(!Object.keys(codebook).length)throw new Error('Define at least one observable behavior.');
    await api('/api/studies',{title:fields.title,species:fields.species,question:fields.question,protocol:fields.protocol,stop_rule:fields.stop_rule,codebook,evidence_keys:[fields.evidence],method:'passive_observation',synthetic:form.elements.synthetic.checked});
    form.reset();form.closest('details').open=false;await refresh();report('Study draft saved with its evidence versions. Check the protocol before activating.');
  }catch(error){report(error.message);}finally{button.disabled=false;}
});
document.querySelector('#session-form').addEventListener('submit',async event=>{
  event.preventDefault();const form=event.target, button=form.querySelector('button');button.disabled=true;
  try {
    const fields=Object.fromEntries(new FormData(form));
    await api('/api/study-sessions',{study_id:fields.study_id,individual_id:fields.individual_id,started_at:new Date(fields.started_at).toISOString(),synthetic:form.elements.synthetic.checked});
    form.reset();form.elements.started_at.value=localTime();await refresh();report('Session opened. Add invented observations in Field Notes below.');
  }catch(error){report(error.message);}finally{button.disabled=false;}
});
(async()=>{try{csrf=(await api('/api/me')).csrf;setTime();document.querySelector('#session-form [name="started_at"]').value=localTime();await refresh();}catch(e){report(e.message);}})();

document.getElementById('show-graph').addEventListener('click', async () => {
  const button = document.getElementById('show-graph'); button.disabled = true;
  try {
    const graph = await api('/api/knowledge-graph');
    document.getElementById('graph-summary').textContent = `${graph.nodes.length} records · ${graph.edges.length} connections · owner only`;
    const container = document.getElementById('graph-connections'); container.replaceChildren();
    const names = new Map(graph.nodes.map(n => [n.id,n.title]));
    const relations = {cites:'cites',uses_frozen_evidence:'uses a frozen reference',follows_protocol:'follows protocol',observed_in:'observed in',contains:'contains',documents:'documents',captured_in:'captured in',aligns:'aligns',uses_release:'uses reviewed release',uses_media:'uses frozen media metadata',uses_alignment:'uses frozen alignment',produces:'has invented output',predicts_on:'refers to input'};
    for (const node of graph.nodes) {
      const edges = graph.edges.filter(e => e.from === node.id);
      if (!edges.length) continue;
      const detail = element('details'); detail.append(element('summary',node.title));
      const list = element('ul');
      for (const edge of edges) list.append(element('li',`${relations[edge.relation]} → ${names.get(edge.to)}`));
      detail.append(list); container.append(detail);
    }
  } catch(error) { report(error.message); }
  finally { button.disabled = false; }
});
