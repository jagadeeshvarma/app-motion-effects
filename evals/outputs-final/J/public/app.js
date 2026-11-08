const kits = document.querySelector('#kits');
const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
let resultAnimation;

function cancelResultAnimation() {
  resultAnimation?.cancel();
  resultAnimation = undefined;
}

reducedMotion.addEventListener('change', cancelResultAnimation);

document.querySelector('#filter').onchange = event => {
  cancelResultAnimation();
  const ready = event.target.value === 'ready';
  let changed = false;
  document.querySelectorAll('#kits li').forEach(item => {
    const hidden = ready && item.dataset.ready !== 'true';
    changed ||= item.hidden !== hidden;
    item.hidden = hidden;
  });
  document.querySelector('#feedback').textContent = ready ? '1 kit shown' : '2 kits shown';

  // Commit the filter first; motion only acknowledges the current results.
  if (changed && !reducedMotion.matches && typeof kits.animate === 'function') {
    const tokens = getComputedStyle(kits);
    resultAnimation = kits.animate([{ opacity: 0.65 }, { opacity: 1 }], {
      // The existing --motion-fast token is expressed in milliseconds.
      duration: parseFloat(tokens.getPropertyValue('--motion-fast')),
      easing: tokens.getPropertyValue('--ease').trim()
    });
    resultAnimation.onfinish = () => { resultAnimation = undefined; };
  }
};
