export function appNavOverlapsControls(nav, controls, activeElement) {
  if (!nav || nav.contains?.(activeElement)) return false;
  const dock = nav.getBoundingClientRect();
  if (!dock.width || !dock.height) return false;
  return Array.from(controls).some(control => {
    if (nav.contains?.(control) || control.hidden || control.disabled || control.closest?.('[hidden], [inert], [aria-hidden="true"]')) return false;
    const style = control.ownerDocument?.defaultView?.getComputedStyle?.(control);
    if (style && (style.display === 'none' || style.visibility === 'hidden')) return false;
    const box = control.getBoundingClientRect();
    return box.width > 0 && box.height > 0 && box.left < dock.right && box.right > dock.left && box.top < dock.bottom && box.bottom > dock.top;
  });
}
