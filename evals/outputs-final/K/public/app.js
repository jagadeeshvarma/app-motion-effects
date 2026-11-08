const show = document.querySelector('#show');
const hide = document.querySelector('#hide');
const panel = document.querySelector('#handover-panel');
const content = document.querySelector('#handover-content');
const note = document.querySelector('#handover');
const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
const tokens = getComputedStyle(document.documentElement);
const revealDuration = parseFloat(tokens.getPropertyValue('--motion-normal'));
const dismissDuration = parseFloat(tokens.getPropertyValue('--motion-fast'));
let open = false;
let transition = null;

show.setAttribute('aria-controls', panel.id);
show.setAttribute('aria-expanded', 'false');
panel.inert = true;

function settle() {
  panel.hidden = !open;
  const previous = transition;
  transition = null;
  previous?.cancel();
}

function setOpen(nextOpen) {
  if (open === nextOpen) return;
  open = nextOpen;
  show.setAttribute('aria-expanded', String(open));
  if (!open && panel.contains(document.activeElement)) {
    show.focus({ preventScroll: true });
  }
  panel.inert = !open;
  panel.setAttribute('aria-hidden', String(!open));

  // Immediate fallback also prevents hidden controls in older browsers.
  if (reducedMotion.matches || !panel.animate || !('inert' in HTMLElement.prototype)) {
    settle();
    return;
  }

  panel.hidden = false;
  if (!transition) {
    const animation = panel.animate([
      { opacity: 0, transform: 'translateY(-6px)' },
      { opacity: 1, transform: 'translateY(0)' }
    ], {
      duration: revealDuration,
      easing: tokens.getPropertyValue('--ease').trim(),
      fill: 'both'
    });
    animation.pause();
    animation.currentTime = open ? 0 : revealDuration;
    animation.onfinish = () => {
      if (transition === animation) settle();
    };
    transition = animation;
  }

  // Reverse the existing timeline without jumping back to an endpoint.
  // At an endpoint, settle directly to avoid play() auto-rewinding it.
  if ((open && transition.currentTime >= revealDuration) ||
      (!open && transition.currentTime <= 0)) {
    settle();
    return;
  }
  transition.playbackRate = open ? 1 : -revealDuration / dismissDuration;
  transition.play();
}

show.onclick = () => {
  content.textContent = note.value;
  setOpen(true);
};
hide.onclick = () => setOpen(false);
reducedMotion.addEventListener('change', () => {
  if (reducedMotion.matches) settle();
});
