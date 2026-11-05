export function showFileSelection(input, file) {
  const output = input?.closest?.('.file-picker')?.querySelector?.('[data-selected-file]');
  if (!output) return false;
  if (!file) {
    output.textContent = '';
    output.title = '';
    output.hidden = true;
    return false;
  }
  const bytes = Number(file.size);
  const size = Number.isFinite(bytes) && bytes >= 0
    ? bytes < 1024 ? `${bytes} B`
      : bytes < 1024 ** 2 ? `${(bytes / 1024).toFixed(1)} KB`
        : bytes < 1024 ** 3 ? `${(bytes / 1024 ** 2).toFixed(1)} MB`
          : `${(bytes / 1024 ** 3).toFixed(1)} GB`
    : '';
  output.textContent = `Ready on this device: ${file.name}${size ? ` · ${size}` : ''}. Tap to change.`;
  output.title = file.name;
  output.hidden = false;
  return true;
}

function acceptedByInput(input, file) {
  const accept = (input?.accept || '').split(',').map(value => value.trim().toLowerCase()).filter(Boolean);
  if (!accept.length) return true;
  const name = (file?.name || '').toLowerCase();
  const type = (file?.type || '').toLowerCase();
  return accept.some(rule => rule.startsWith('.')
    ? name.endsWith(rule)
    : rule.endsWith('/*')
      ? type.startsWith(rule.slice(0, -1))
      : rule === type);
}

export function bindFilePicker(input, {DataTransferClass = globalThis.DataTransfer, EventClass = globalThis.Event} = {}) {
  const picker = input?.closest?.('.file-picker');
  if (!picker || typeof picker.addEventListener !== 'function' || picker.dataset?.dropReady) return false;
  if (picker.dataset) picker.dataset.dropReady = 'true';
  const selection = picker.querySelector?.('[data-selected-file]');
  const announce = message => {
    if (!selection) return;
    selection.textContent = message;
    selection.hidden = false;
  };
  const setHover = value => picker.classList?.toggle('file-picker-over', value);
  for (const name of ['dragenter', 'dragover']) picker.addEventListener(name, event => {
    event.preventDefault();
    setHover(true);
  });
  picker.addEventListener('dragleave', event => {
    if (event.relatedTarget && picker.contains?.(event.relatedTarget)) return;
    setHover(false);
  });
  picker.addEventListener('drop', event => {
    event.preventDefault();
    setHover(false);
    const files = Array.from(event.dataTransfer?.files || []);
    if (files.length !== 1) {
      announce(files.length ? 'Open one file at a time.' : 'No file was dropped. Choose a file from this device.');
      return;
    }
    const [file] = files;
    if (!acceptedByInput(input, file)) {
      announce('That file type does not match this tool. Choose a supported file from this device.');
      return;
    }
    if (typeof DataTransferClass !== 'function' || typeof EventClass !== 'function') {
      announce('File drop is unavailable here. Choose a file from this device.');
      return;
    }
    try {
      const transfer = new DataTransferClass();
      transfer.items.add(file);
      input.files = transfer.files;
      input.dispatchEvent(new EventClass('change', {bubbles: true}));
    } catch {
      announce('This browser could not open the dropped file. Choose a file from this device.');
    }
  });
  return true;
}
