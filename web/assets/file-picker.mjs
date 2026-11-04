export function showFileSelection(input, file) {
  const output = input?.closest?.('.file-picker')?.querySelector?.('[data-selected-file]');
  if (!output) return false;
  if (!file) {
    output.textContent = '';
    output.title = '';
    output.hidden = true;
    return false;
  }
  output.textContent = `Selected: ${file.name}`;
  output.title = file.name;
  output.hidden = false;
  return true;
}
