import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';

const read = path => fs.readFileSync(new URL(path, import.meta.url), 'utf8');
const home = read('../web/templates/app.html');
const station = read('../web/templates/station.html');
const stationScript = read('../web/assets/station.js');

test('first-use save guidance uses plain language while keeping research export optional', () => {
  assert.match(home, /Download a copy before closing to keep this moment\./);
  assert.match(station, /id="station-retention-guidance"[^>]*>Your sound and notes stay in this page\. Download a copy before closing if you want to keep them\./);
  assert.match(station, /id="station-soundscape-feedback"[^>]*>No setting categories selected\. Your saved note will say “not recorded,” not that the sounds were absent\./);
  assert.match(station, /id="station-note"[^>]*aria-describedby="station-note-help"/);
  assert.match(station, /id="station-note-help"[^>]*>While recording, tap “Mark an observation” to add this note to your timeline\. If you stop first, it stays in this page and is not included in your download\./);
  assert.match(station, /id="station-draft-warning"[^>]*>This note is still a draft\. It was not added to your saved moment\. Copy it elsewhere if you want to keep it\./);
  assert.match(station, /id="station-export-note"[^>]*>Save this moment downloads one file with your notes and saved sounds\. Check Downloads before leaving\. After you confirm the download, open Compare moments to review it\. The copy stays on your device; it is not sent to Talk2Nature or added to research\./);
  assert.match(station, /<summary>Advanced · research export<\/summary>/);
  assert.match(stationScript, /Starting a new moment will clear this one from the page\. Download a copy first if you want to keep it\./);
  assert.match(stationScript, /This page has reached its temporary sound limit\. Save this moment or discard it before starting again\./);
  assert.doesNotMatch(home, /auto-save|\bexport\b|\bJSON\b/i);
});
