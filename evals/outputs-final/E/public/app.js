const editor = document.querySelector('#editor');
const opener = document.querySelector('#open');
const count = document.querySelector('#count');
const confirm = document.querySelector('#confirm');
const cancel = document.querySelector('#cancel');
const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
let motion;
let closing = false;

function stopMotion() {
  if (!motion) return;
  motion.onfinish = null;
  motion.cancel();
  motion = undefined;
}

function animateEditor(frames, durationToken) {
  const styles = getComputedStyle(editor);
  motion = editor.animate(frames, {
    duration: parseFloat(styles.getPropertyValue(durationToken)),
    easing: styles.getPropertyValue('--ease').trim()
  });
}

function finishClose() {
  stopMotion();
  closing = false;
  editor.close();
  editor.hidden = true;
  delete editor.dataset.state;
  editor.style.removeProperty('--backdrop-exit-opacity');
  opener.focus({ preventScroll: true });
}

function closeEditor() {
  if (!editor.open || closing) return;
  const appearance = getComputedStyle(editor);
  const exitStart = { opacity: appearance.opacity, transform: appearance.transform };
  const backdropOpacity = getComputedStyle(editor, '::backdrop').opacity;
  closing = true;
  stopMotion();
  editor.style.setProperty('--backdrop-exit-opacity', backdropOpacity);
  editor.dataset.state = 'closing';
  if (reducedMotion.matches || !editor.animate) {
    finishClose();
    return;
  }
  // Keep the modal boundary during exit so a second action cannot click through.
  animateEditor([
    exitStart,
    { opacity: 0, transform: 'translateY(4px)' }
  ], '--motion-fast');
  motion.onfinish = finishClose;
}

opener.onclick = () => {
  if (editor.open) return;
  stopMotion();
  editor.hidden = false;
  editor.dataset.state = 'open';
  editor.showModal();
  count.focus({ preventScroll: true });
  count.select();
  if (!reducedMotion.matches && editor.animate) {
    animateEditor([
      { opacity: 0, transform: 'translateY(8px)' },
      { opacity: 1, transform: 'translateY(0)' }
    ], '--motion-normal');
  }
};

cancel.onclick = closeEditor;
confirm.onclick = () => {
  if (!editor.open || closing) return;
  document.querySelector('#feedback').textContent = `Count saved: ${count.value}`;
  closeEditor();
};

editor.addEventListener('cancel', event => {
  event.preventDefault();
  closeEditor();
});

editor.addEventListener('keydown', event => {
  if (event.key !== 'Tab') return;
  // Explicit wrapping also keeps Tab out of browser chrome at either boundary.
  if (event.shiftKey && document.activeElement === count) {
    event.preventDefault();
    cancel.focus();
  } else if (!event.shiftKey && document.activeElement === cancel) {
    event.preventDefault();
    count.focus();
  }
});

editor.addEventListener('close', () => {
  // Also clean up if a caller uses the platform close() method directly.
  if (editor.open) return;
  stopMotion();
  closing = false;
  editor.hidden = true;
  delete editor.dataset.state;
  editor.style.removeProperty('--backdrop-exit-opacity');
  opener.focus({ preventScroll: true });
});

reducedMotion.addEventListener('change', () => {
  if (!reducedMotion.matches) return;
  if (closing) finishClose();
  else stopMotion();
});
