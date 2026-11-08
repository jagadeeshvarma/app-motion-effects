window.__filterStats={changes:0};

function animateResultChange(...elements) {
  elements.forEach(element => element.classList.remove('results-changed'));
  // Flush once so repeated changes restart the same shared CSS animation.
  void document.documentElement.offsetWidth;
  elements.forEach(element => element.classList.add('results-changed'));
}

document.querySelector('#filter').addEventListener('change', event => {
  window.__filterStats.changes++;
  const ready = event.target.value === 'ready';
  document.querySelectorAll('#parcels li').forEach(item => {
    item.hidden = ready && item.dataset.state !== 'ready';
  });
  const feedback = document.querySelector('#feedback');
  feedback.textContent = ready ? '1 parcel shown' : '2 parcels shown';
  animateResultChange(document.querySelector('#parcels'), feedback);
});
