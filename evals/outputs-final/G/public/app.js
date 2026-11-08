const preview = document.querySelector('#preview');
const panel = document.querySelector('#preview-panel');
const message = document.querySelector('#message');
const content = document.querySelector('#message-content');
const close = document.querySelector('#close');
const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
let isOpen = false;
let animation = null;

function settlePreview() {
  const previous = animation;
  animation = null;
  panel.hidden = !isOpen;
  previous?.cancel();
}

function setPreviewOpen(open) {
  if (open === isOpen && !animation) return;
  isOpen = open;
  preview.setAttribute('aria-expanded', String(open));

  // Restore focus before making the dismissing controls unavailable.
  if (!open && panel.contains(document.activeElement)) preview.focus();
  panel.inert = !open;

  if (reducedMotion.matches || typeof panel.animate !== 'function') {
    settlePreview();
    return;
  }
  if (panel.hidden && !open) return;
  panel.hidden = false;

  if (!animation) {
    const tokens = getComputedStyle(panel);
    const duration = parseFloat(tokens.getPropertyValue('--motion-fast'));
    const next = panel.animate([
      { opacity: 0, transform: 'translateY(-4px)' },
      { opacity: 1, transform: 'translateY(0)' },
    ], {
      duration,
      easing: tokens.getPropertyValue('--ease').trim(),
      fill: 'both',
    });
    animation = next;
    next.currentTime = open ? 0 : duration;
    next.onfinish = () => {
      // Ignore an already queued finish if a newer action reversed playback.
      if (animation === next && next.playState === 'finished') settlePreview();
    };
  }
  // Retain the current position when interrupted; never queue transitions.
  // play() rewinds at an endpoint, so settle an already reached target first.
  const endTime = animation.effect.getComputedTiming().endTime;
  if ((!open && animation.currentTime <= 0) ||
      (open && animation.currentTime >= endTime)) {
    settlePreview();
    return;
  }
  animation.playbackRate = open ? 1 : -1;
  animation.play();
}

preview.onclick = () => {
  // Message data stays literal text throughout reveal, reversal and dismissal.
  content.textContent = message.value;
  setPreviewOpen(true);
};
close.onclick = () => setPreviewOpen(false);
panel.addEventListener('keydown', (event) => {
  if (event.key === 'Escape' && isOpen) {
    event.preventDefault();
    setPreviewOpen(false);
  }
});
reducedMotion.addEventListener('change', () => {
  if (reducedMotion.matches) settlePreview();
});
