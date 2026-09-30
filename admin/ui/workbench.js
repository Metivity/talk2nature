let csrf = '';
let records = [];
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
  const [observations, releases, audit] = await Promise.all([api('/api/observations'),api('/api/releases'),api('/api/audit')]);
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
function setTime() {const now=new Date();document.querySelector('[name="recorded_at"]').value=new Date(now.getTime()-now.getTimezoneOffset()*60000).toISOString().slice(0,16);}
document.querySelector('#refresh').addEventListener('click',()=>refresh().catch(e=>report(e.message)));
document.querySelector('#release').addEventListener('click',async event=>{event.target.disabled=true;try{await api('/api/releases',{ids:records.filter(r=>r.state==='accepted' && r.consent_training).map(r=>r.id)});await refresh();report('A private synthetic metadata release was created. No model training was run.');}catch(e){report(e.message);event.target.disabled=false;}});
document.querySelector('#logout').addEventListener('click',async()=>{try{await api('/auth/logout',{});location.assign('/');}catch(e){report(e.message);}});
(async()=>{try{csrf=(await api('/api/me')).csrf;setTime();await refresh();}catch(e){report(e.message);}})();
