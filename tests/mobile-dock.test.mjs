import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { runInNewContext } from 'node:vm';
import test from 'node:test';

const script = readFileSync(new URL('../web/assets/site.js', import.meta.url), 'utf8');

function createPage(width = 320, initialY = 0, contentOverlaps = false) {
  const windowListeners = new Map();
  const documentListeners = new Map();
  const dockListeners = new Map();
  const classes = new Set();
  const keyboardLink = {};
  const dock = {
    style: {},
    getBoundingClientRect() { return {left: 12, right: 308, top: 770, bottom: 832, width: 296, height: 62}; },
    addEventListener(type, listener) { dockListeners.set(type, listener); },
    contains(target) { return target === keyboardLink; },
  };
  const paragraph = {
    hidden: false,
    disabled: false,
    closest() { return null; },
    getBoundingClientRect() { return contentOverlaps ? {left: 20, right: 300, top: 780, bottom: 820, width: 280, height: 40} : {left: 20, right: 300, top: 710, bottom: 750, width: 280, height: 40}; },
    ownerDocument: {defaultView: {getComputedStyle() { return {display: 'block', visibility: 'visible'}; }}},
  };
  const window = {
    innerWidth: width,
    scrollY: initialY,
    matchMedia() {
      const viewport = this;
      return { get matches() { return viewport.innerWidth <= 800; } };
    },
    addEventListener(type, listener) { windowListeners.set(type, listener); },
  };
  const document = {
    activeElement: null,
    visibilityState: 'visible',
    body: { classList: {
      add(name) { classes.add(name); },
      remove(name) { classes.delete(name); },
      contains(name) { return classes.has(name); },
    } },
    querySelector(selector) { return selector === '.field-dock' ? dock : null; },
    querySelectorAll() { return [paragraph]; },
    addEventListener(type, listener) { documentListeners.set(type, listener); },
  };
  runInNewContext(script, { document, window });
  return {
    classes, dock, dockListeners, document, documentListeners, keyboardLink, window, windowListeners,
    scrollTo(y) { window.scrollY = y; windowListeners.get('scroll')(); },
    resize(width) { window.innerWidth = width; windowListeners.get('resize')(); },
  };
}

test('mobile dock hides over readable content and returns when it no longer covers the page', () => {
  const page = createPage(320, 0, true);
  assert.equal(page.classes.has('field-dock-away'), true);
  page.document.querySelectorAll = () => [];
  page.resize(321);
  assert.equal(page.classes.has('field-dock-away'), false);
});

test('mobile dock hides while scrolling down and returns on upward scroll or keyboard focus', () => {
  const page = createPage();
  assert.equal(page.classes.has('field-dock-away'), false);
  page.scrollTo(140);
  assert.equal(page.classes.has('field-dock-away'), true);
  page.scrollTo(105);
  assert.equal(page.classes.has('field-dock-away'), false);
  page.scrollTo(155);
  assert.equal(page.classes.has('field-dock-away'), true);
  page.dockListeners.get('focusin')();
  assert.equal(page.classes.has('field-dock-away'), false);

  page.document.activeElement = page.keyboardLink;
  page.scrollTo(190);
  assert.equal(page.classes.has('field-dock-away'), false);
});

test('desktop keeps its dock unchanged and viewport rotation synchronizes visibility', () => {
  const page = createPage(900);
  page.scrollTo(140);
  assert.equal(page.classes.has('field-dock-away'), false);
  page.resize(390);
  assert.equal(page.classes.has('field-dock-away'), true);
  page.resize(900);
  assert.equal(page.classes.has('field-dock-away'), false);
});

test('returning near the top or restoring a visible page reveals the dock', () => {
  const page = createPage(320, 180);
  assert.equal(page.classes.has('field-dock-away'), true);
  page.scrollTo(40);
  assert.equal(page.classes.has('field-dock-away'), false);
  page.scrollTo(150);
  assert.equal(page.classes.has('field-dock-away'), true);
  page.window.scrollY = 0;
  page.document.visibilityState = 'visible';
  page.documentListeners.get('visibilitychange')();
  assert.equal(page.classes.has('field-dock-away'), false);
});
