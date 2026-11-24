'use strict';
const projectUrl=new URL('../mobile/',document.currentScript.src).href;
const buildToken=value=>/^[a-f0-9]{16}$/i.test(value||'')?value:'Not supplied';
const feedbackBuild=buildToken(new URL(document.currentScript.src).searchParams.get('v'));
const linkedAppBuild=buildToken(new URL(location.href).searchParams.get('app_build'));
const status=document.getElementById('share-status');
document.getElementById('copy-project')?.addEventListener('click',async()=>{
  try { await navigator.clipboard.writeText(projectUrl); status.textContent='Project link copied. No recordings or notes were included.'; }
  catch { status.textContent=`Copy this public project link: ${projectUrl}`; }
});
document.getElementById('share-project')?.addEventListener('click',async()=>{
  if(!navigator.share){status.textContent='Use Copy link to share the public project page.';return;}
  try {await navigator.share({title:'Talk2Nature — a field companion',text:'Explore sounds and observations with this local-first, open-source app. Try the synthetic rehearsal.',url:projectUrl});status.textContent='Share dialog completed. No recordings or notes were included.';}
  catch(error){status.textContent=error.name==='AbortError'?'Sharing cancelled.':'Sharing is unavailable here. Use Copy link.';}
});

const feedbackForm=document.getElementById('mobile-feedback-form');
const feedbackPreview=document.getElementById('feedback-preview');
const feedbackReport=document.getElementById('feedback-report');
const feedbackStatus=document.getElementById('feedback-status');
const emailFeedback=document.getElementById('email-feedback');
feedbackForm?.addEventListener('submit',event=>{
  event.preventDefault();
  const workflow=document.getElementById('feedback-workflow')?.value.trim();
  const outcome=document.getElementById('feedback-outcome')?.value.trim();
  if(!workflow||!outcome){feedbackForm.reportValidity();return;}
  const device=document.getElementById('feedback-device')?.value.trim()||'Not provided';
  const note=document.getElementById('feedback-note')?.value.trim()||'No additional note';
  const report=['Talk2Nature mobile workflow feedback',`Workflow: ${workflow}`,`Outcome: ${outcome}`,`App build referenced by link: ${linkedAppBuild}`,`Feedback page build: ${feedbackBuild}`,`Device/browser: ${device}`,`What was unclear or useful: ${note}`].join('\n');
  feedbackReport.value=report;
  const subject=encodeURIComponent('Talk2Nature mobile workflow feedback');
  const encodedBody=encodeURIComponent(report);
  const emailTooLong=encodedBody.length>1800;
  emailFeedback.hidden=emailTooLong;
  emailFeedback.href=`mailto:raviv@metivity.com?subject=${subject}&body=${encodedBody}`;
  feedbackPreview.hidden=false;
  feedbackStatus.textContent=emailTooLong?'Report prepared here. It is too long for a reliable email link; use Copy report. Nothing has been saved or sent.':'Report prepared on this page. Nothing has been saved or sent; choose Copy report or open an email draft.';
  feedbackStatus.focus();
});

document.getElementById('copy-feedback')?.addEventListener('click',async()=>{
  try {await navigator.clipboard.writeText(feedbackReport.value);feedbackStatus.textContent='Report copied. Nothing was sent; review it before sharing.';}
  catch {feedbackReport.focus();feedbackReport.select();feedbackStatus.textContent='Clipboard access is unavailable; the report text is selected so you can copy it manually.';}
});
