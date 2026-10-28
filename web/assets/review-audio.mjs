const START_PROMPT = 'Right before playback: confirm an animal cannot hear this recording. Use headphones or review away from animals. Cancel leaves it unplayed.';

function clock(seconds) {
  const value = Number.isFinite(seconds) && seconds > 0 ? Math.floor(seconds) : 0;
  return `${Math.floor(value / 60)}:${String(value % 60).padStart(2, '0')}`;
}

export function createReviewAudioControls({audio, button, seek, time, status, confirm}) {
  let duration = 0, pending = false, sequence = 0;
  const update = () => {
    const total = Number.isFinite(audio.duration) && audio.duration > 0 ? audio.duration : duration;
    seek.max = String(total);
    seek.value = String(Math.min(total, Number.isFinite(audio.currentTime) ? audio.currentTime : 0));
    time.textContent = `${clock(audio.currentTime)} / ${clock(total)}`;
    const playing = !audio.paused && !audio.ended;
    button.textContent = playing ? 'Pause review' : 'Play for human review';
    button.setAttribute('aria-label', playing ? 'Pause review audio' : 'Play audio for human review');
  };

  button.addEventListener('click', async () => {
    if (!audio.paused && !audio.ended) {
      audio.pause();
      status.textContent = 'Playback paused.';
      return;
    }
    if (pending) return;
    if (!confirm(START_PROMPT)) {
      status.textContent = 'Cancelled. The recording was not played.';
      return;
    }
    if (audio.ended) audio.currentTime = 0;
    pending = true;
    const attempt = ++sequence;
    button.disabled = true;
    try {
      await audio.play();
      if (attempt === sequence) status.textContent = 'Playing for human review. Use headphones or review away from animals.';
    } catch {
      if (attempt === sequence) status.textContent = 'Playback could not start in this browser. The file stayed on this device.';
    } finally {
      if (attempt === sequence) {
        pending = false;
        button.disabled = false;
        update();
      }
    }
  });

  seek.addEventListener('input', () => {
    const position = Number(seek.value);
    if (Number.isFinite(position) && (Number.isFinite(audio.duration) || duration > 0)) audio.currentTime = position;
    update();
  });
  for (const event of ['loadedmetadata', 'durationchange', 'timeupdate', 'play', 'pause', 'ended']) audio.addEventListener(event, update);

  return {
    pause(message = 'Playback paused.') {
      sequence++;
      pending = false;
      button.disabled = false;
      audio.pause();
      status.textContent = message;
      update();
    },
    reset(seconds = 0) {
      sequence++;
      pending = false;
      button.disabled = false;
      duration = Number.isFinite(seconds) && seconds > 0 ? seconds : 0;
      seek.value = '0';
      seek.max = String(duration);
      time.textContent = `${clock(0)} / ${clock(duration)}`;
      status.textContent = '';
      update();
    }
  };
}
