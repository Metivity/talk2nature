import test from 'node:test';
import assert from 'node:assert/strict';
import {appNavOverlapsControls} from '../web/assets/app-nav-visibility.mjs';

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

test('mobile dock yields when it covers a visible control', () => {
  const control = node({left: 24, right: 296, top: 748, bottom: 784, width: 272, height: 36});
  assert.equal(appNavOverlapsControls(nav(dock), [control], null), true);
});

test('mobile dock can show when controls are clear and ignores hidden or dock-owned controls', () => {
  const hidden = node({left: 20, right: 300, top: 780, bottom: 820, width: 280, height: 40}, {hidden: true});
  const outside = node({left: 20, right: 300, top: 710, bottom: 750, width: 280, height: 40});
  const dockLink = node(dock, {});
  assert.equal(appNavOverlapsControls(nav(dock, [dockLink]), [hidden, outside, dockLink], null), false);
});

test('focused navigation remains available even when a page control lies below it', () => {
  const dockLink = node(dock, {});
  const control = node({left: 20, right: 300, top: 780, bottom: 820, width: 280, height: 40});
  const menu = nav(dock, [dockLink]);
  assert.equal(appNavOverlapsControls(menu, [control, dockLink], dockLink), false);
});
