import test from 'node:test';
import assert from 'node:assert/strict';
import {readdir, readFile} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import path from 'node:path';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const assets = path.join(root, 'web', 'assets');
const templates = path.join(root, 'web', 'templates');

test('observation assets cannot trigger animal-facing browser output', async () => {
  const files = (await readdir(assets)).filter(file => /\.(?:m?js)$/.test(file));
  const forbidden = [
    ['speech synthesis', /\bspeechSynthesis\s*\.\s*(?:speak|cancel)\s*\(/i],
    ['device vibration', /\bnavigator\s*\.\s*vibrate\s*\(/i],
    ['notification permission prompt', /\bNotification\s*\.\s*requestPermission\s*\(/i],
    ['constructed notification', /\bnew\s+Notification\s*\(/i],
    ['enabled camera torch', /\btorch\s*:\s*true\b/i],
    ['autoplay-enabled embed', /[?&]autoplay\s*=\s*1(?:&|\b)/i],
  ];
  const supportedHumanPlayback = new Set(['station.js', 'review-audio.mjs']);

  for (const file of files) {
    const source = await readFile(path.join(assets, file), 'utf8');
    for (const [label, pattern] of forbidden) {
      assert.doesNotMatch(source, pattern, `${file} contains ${label}`);
    }
    if (!supportedHumanPlayback.has(file)) {
      assert.doesNotMatch(source, /\.play\s*\(/i, `${file} must not start media playback`);
    }
  }

  const station = await readFile(path.join(assets, 'station.js'), 'utf8');
  const stationControl = station.indexOf("$('station-play-review').addEventListener('click'");
  const stationConfirm = station.indexOf('window.confirm(', stationControl);
  const stationPlay = station.indexOf('await player.play()', stationConfirm);
  assert.ok(stationControl >= 0 && stationConfirm > stationControl && stationPlay > stationConfirm,
    'Station playback must follow a deliberate review-button click and a fresh confirmation');
  assert.equal((station.match(/\.play\s*\(/g) || []).length, 1,
    'Station must have no playback path beyond its confirmed review button');

  const review = await readFile(path.join(assets, 'review-audio.mjs'), 'utf8');
  const reviewControl = review.indexOf("button.addEventListener('click'");
  const reviewConfirm = review.indexOf('if (!confirm(START_PROMPT))', reviewControl);
  const reviewPlay = review.indexOf('await audio.play()', reviewConfirm);
  assert.ok(reviewControl >= 0 && reviewConfirm > reviewControl && reviewPlay > reviewConfirm,
    'Listen and Compare playback must follow a deliberate button click and a fresh confirmation');
  assert.equal((review.match(/\.play\s*\(/g) || []).length, 1,
    'Listen and Compare must have no playback path beyond their confirmed review button');
});

test('animal-facing boundary is visible in the Station and playback cannot autoplay', async () => {
  const station = await readFile(path.join(templates, 'station.html'), 'utf8');
  const appIntro = await readFile(path.join(templates, 'app-station-intro.html'), 'utf8');
  assert.match(station, /Observe what happens naturally/i);
  assert.match(station, /no animal calls or prompts/i);
  assert.match(station, /do not call or imitate to elicit a response/i);
  assert.match(station, /not automatically a reply/i);
  assert.match(station, /You do not need to call, imitate or prompt an animal/i);
  assert.match(station, /Do not provoke calls, approach wildlife or change an animal’s behavior/i);
  assert.match(station, /id="station-play-review"[^>]*>Play for human review</i);
  assert.match(appIntro, /Observe without prompting/i);
  assert.match(appIntro, /You do not need to call or imitate an animal/i);
  assert.match(appIntro, /no animal-directed sounds or prompts/i);
  assert.match(appIntro, /capture stops if you leave this page/i);
  assert.match(appIntro, /Playback is for human review only—never play it to animals/i);

  for (const file of ['station.html', 'listen.html', 'compare.html']) {
    const source = await readFile(path.join(templates, file), 'utf8');
    const players = source.match(/<audio\b[^>]*>/gi) || [];
    assert.ok(players.length > 0, `${file} should expose its documented review player`);
    for (const player of players) assert.doesNotMatch(player, /\bautoplay\b/i, `${file} player must not autoplay`);
  }

  const listen = await readFile(path.join(templates, 'listen.html'), 'utf8');
  const compare = await readFile(path.join(templates, 'compare.html'), 'utf8');
  assert.match(listen, /id="listen-playback-toggle"[^>]*>Play for human review</i);
  assert.match(compare, /id="compare-playback-toggle"[^>]*>Play for human review</i);
});

test('browser Station stops capture when the page leaves the foreground', async () => {
  const station = await readFile(path.join(assets, 'station.js'), 'utf8');
  const hiddenStart = station.indexOf("document.addEventListener('visibilitychange'");
  const pagehideStart = station.indexOf("window.addEventListener('pagehide'");
  const unloadStart = station.indexOf("window.addEventListener('beforeunload'");
  assert.ok(hiddenStart >= 0 && pagehideStart > hiddenStart && unloadStart > pagehideStart);
  const hiddenHandler = station.slice(hiddenStart, pagehideStart);
  const pagehideHandler = station.slice(pagehideStart, unloadStart);
  assert.match(hiddenHandler, /if \(!document\.hidden\) return;/);
  assert.match(hiddenHandler, /if \(active \|\| pending\) stop\('backgrounded'\)/);
  assert.match(pagehideHandler, /if \(active \|\| pending\) stop\('page_closed'\)/);
});
