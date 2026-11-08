const shelves = document.querySelector('#shelves');
const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
const tokens = getComputedStyle(shelves);
const timing = {
  duration: parseFloat(tokens.getPropertyValue('--motion-fast')),
  easing: tokens.getPropertyValue('--ease').trim()
};
const animations = new Set();
const cancelAnimations = () => {
  animations.forEach(animation => animation.cancel());
  animations.clear();
};
reducedMotion.addEventListener('change', cancelAnimations);

document.querySelector('#search').addEventListener('input', event => {
  const items = [...shelves.querySelectorAll('li')];
  const animate = !reducedMotion.matches && typeof shelves.animate === 'function';
  // Read the current presentation before cancelling, so rapid edits retarget it.
  const previous = new Map();
  if (animate) items.filter(item => !item.hidden).forEach(item => {
    previous.set(item, {
      top: item.getBoundingClientRect().top,
      opacity: Number(getComputedStyle(item).opacity)
    });
  });
  cancelAnimations();

  let count = 0;
  items.forEach(item => {
    item.hidden = !item.textContent.toLowerCase().includes(event.target.value.toLowerCase());
    if (!item.hidden) count++;
  });
  document.querySelector('#feedback').textContent = `${count} shelves shown`;

  if (!animate) return;
  const visible = items.filter(item => !item.hidden);
  // Batch layout reads; animate only current matches, never departing rows.
  const tops = visible.map(item => item.getBoundingClientRect().top);
  visible.forEach((item, index) => {
    const from = previous.get(item);
    const offset = from ? from.top - tops[index] : 0;
    const opacity = from ? from.opacity : 0.65;
    if (!offset && opacity === 1) return;
    const animation = item.animate([
      { transform: `translateY(${offset}px)`, opacity },
      { transform: 'translateY(0)', opacity: 1 }
    ], timing);
    animations.add(animation);
    animation.onfinish = () => animations.delete(animation);
  });
});
