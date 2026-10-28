import test from 'node:test';
import assert from 'node:assert/strict';
import {appNavOverlapsContent, appNavShouldHideOnLoad} from '../web/assets/app-nav-visibility.mjs';

function node(box, options = {}) {
  const value = {
    ...options,
    getBoundingClientRect: () => box,
    closest: selector => options.ancestorHidden && selector.includes('hidden') ? {} : null,
    ownerDocument: {defaultView: {getComputedStyle: () => ({display: options.display || 'block', visibility: options.visibility || 'visible'})}}
  };
  return value;
}

function nav(box, children = []) {
  return {getBoundingClientRect: () => box, contains: element => children.includes(element)};
}

const dock = {left: 12, right: 308, top: 770, bottom: 832, width: 296, height: 62};

test('mobile deep links and restored positions start with the dock hidden', () => {
  assert.equal(appNavShouldHideOnLoad({compact: true, fixed: true, hasHash: true, scrollY: 0}), true);
  assert.equal(appNavShouldHideOnLoad({compact: true, fixed: true, hasHash: false, scrollY: 240}), true);
});

test('ordinary top loads and non-fixed desktop navigation stay visible', () => {
  assert.equal(appNavShouldHideOnLoad({compact: true, fixed: true, hasHash: false, scrollY: 0}), false);
  assert.equal(appNavShouldHideOnLoad({compact: false, fixed: false, hasHash: true, scrollY: 240}), false);
  assert.equal(appNavShouldHideOnLoad({compact: true, fixed: false, hasHash: true, scrollY: 0}), false);
});

test('mobile dock yields when it covers a visible control', () => {
  const control = node({left: 24, right: 296, top: 748, bottom: 784, width: 272, height: 36});
  assert.equal(appNavOverlapsContent(nav(dock), [control], null), true);
});

test('mobile dock yields when it covers readable text', () => {
  const paragraph = node({left: 18, right: 302, top: 780, bottom: 820, width: 284, height: 40});
  assert.equal(appNavOverlapsContent(nav(dock), [paragraph], null), true);
});

test('mobile dock can show when controls are clear and ignores hidden or dock-owned controls', () => {
  const hidden = node({left: 20, right: 300, top: 780, bottom: 820, width: 280, height: 40}, {hidden: true});
  const outside = node({left: 20, right: 300, top: 710, bottom: 750, width: 280, height: 40});
  const dockLink = node(dock, {});
  assert.equal(appNavOverlapsContent(nav(dock, [dockLink]), [hidden, outside, dockLink], null), false);
});

test('focused navigation remains available even when a page control lies below it', () => {
  const dockLink = node(dock, {});
  const control = node({left: 20, right: 300, top: 780, bottom: 820, width: 280, height: 40});
  const menu = nav(dock, [dockLink]);
  assert.equal(appNavOverlapsContent(menu, [control, dockLink], dockLink), false);
});
