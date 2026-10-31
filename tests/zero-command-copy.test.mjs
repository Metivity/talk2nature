import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';

const read = path => fs.readFileSync(new URL(path, import.meta.url), 'utf8');
const home = read('../web/templates/app.html');
const station = read('../web/templates/station.html');
const stationScript = read('../web/assets/station.js');

test('first-use save guidance uses plain language while keeping research export optional', () => {
  assert.match(home, /Start with an invented example: no microphone or account needed\. We don't call, imitate or prompt animals\. Real observation is optional\./);
  assert.match(station, /id="station-demo"[^>]*>Try invented example · no microphone<\/button>/);
  assert.match(home, /No microphone is used unless you choose Start\. Download a copy before closing to keep a real moment\./);
  assert.match(station, /id="station-retention-guidance"[^>]*>Your sound and notes stay in this page\. Download a copy before closing if you want to keep them\./);
  assert.match(station, /id="station-zero-command"[^>]*><strong>Listen-only by design\.<\/strong> We do not call, imitate or prompt animals\. You choose when recording starts and can stop it at any time\. In the browser, recording ends if you leave this page\./);
  assert.match(station, /id="station-start"[^>]*aria-describedby="station-zero-command station-retention-guidance"/);
  assert.match(station, /id="station-soundscape-feedback"[^>]*>No setting categories selected\. Your saved note will say “not recorded,” not that the sounds were absent\./);
  assert.match(station, /id="station-note"[^>]*aria-describedby="station-note-help"/);
  assert.match(station, /id="station-note-help"[^>]*>While recording, tap “Mark an observation” to add this note to your timeline\. If you stop first, it stays in this page and is not included in your download\./);
  assert.match(station, /id="station-draft-warning"[^>]*>This note is still a draft\. It was not added to your saved moment\. Copy it elsewhere if you want to keep it\./);
  assert.match(station, /id="station-export-note"[^>]*>Save this moment prepares one file with your notes and saved sounds\. Check Downloads before leaving\. If it opens as a preview, use Share → Save to Files \(or your device’s save option\), then return here\. After saving, open Compare moments to review it\. The file stays on your device; it is not sent to Talk2Nature or added to research\./);
  assert.match(stationScript, /Your file is ready\. Check Downloads\. If it opens as a preview, use Share → Save to Files/);
  assert.match(stationScript, /\$\('station-save-ack'\)\.textContent = 'I saved the file'/);
  assert.match(station, /<summary>Advanced · research export<\/summary>/);
  assert.match(stationScript, /Starting a new moment will clear this one from the page\. Download a copy first if you want to keep it\./);
  assert.match(stationScript, /This page has reached its temporary sound limit\. Save this moment or discard it before starting again\./);
  assert.doesNotMatch(home, /auto-save|\bexport\b|\bJSON\b/i);
});

test('the animal-facing zero-command rule appears before the first action', () => {
  const boundary = home.indexOf("We don't call, imitate or prompt animals.");
  const firstAction = home.indexOf('class="app-actions"');
  assert.ok(boundary >= 0, 'the home page states the animal-facing boundary');
  assert.ok(firstAction >= 0, 'the home page has its first-action group');
  assert.ok(boundary < firstAction, 'the boundary appears before the first action');
});
