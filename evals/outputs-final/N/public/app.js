import {receipts} from './receipts.js';

const panel = document.querySelector('#panel');
const unpaid = document.querySelector('#unpaid');
const filters = document.querySelector('#filters');
const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)');
let activeUnpaid = false;
let session = null;

function render() {
  document.querySelector('#receipts').replaceChildren(...receipts
    .filter(item => !activeUnpaid || !item.paid)
    .map(item => {
      const li = document.createElement('li');
      li.dataset.paid = String(item.paid);
      li.textContent = `Receipt ${item.id}: ${item.paid ? 'paid' : 'unpaid'}`;
      return li;
    }));
  document.querySelector('#feedback').textContent = activeUnpaid ? 'Unpaid receipts' : 'All receipts';
}

function finishClose(current) {
  // Every completion path owns the same session; stale callbacks cannot close a new one.
  if (session !== current) return;
  session = null;
  cancelAnimationFrame(current.frame);
  current.stopWaiting?.();
  panel.classList.remove('shown', 'closing');
  if (panel.open) panel.close();
  document.body.style.setProperty('overflow', current.overflow, current.overflowPriority);
  const target = current.returnFocus?.isConnected ? current.returnFocus : filters;
  target.focus({preventScroll: true});
  window.scrollTo(current.scrollX, current.scrollY);
}

function open() {
  if (session) {
    if (!session.closing) return;
    finishClose(session);
  }
  if (panel.open) return;
  const current = {
    returnFocus: document.activeElement,
    overflow: document.body.style.overflow,
    overflowPriority: document.body.style.getPropertyPriority('overflow'),
    scrollX: window.scrollX,
    scrollY: window.scrollY,
    closing: false,
    frame: 0
  };
  unpaid.checked = activeUnpaid;
  // Acquire the lock only after showModal succeeds.
  panel.showModal();
  session = current;
  document.body.style.overflow = 'hidden';
  unpaid.focus({preventScroll: true});
  window.scrollTo(current.scrollX, current.scrollY);
  if (reducedMotion.matches) {
    panel.classList.add('shown');
  } else {
    // Establish the existing entry pose before requesting the visible pose.
    getComputedStyle(panel).opacity;
    current.frame = requestAnimationFrame(() => {
      if (session === current && !current.closing) panel.classList.add('shown');
    });
  }
}

function close() {
  const current = session;
  if (!current || current.closing) return;
  current.closing = true;
  cancelAnimationFrame(current.frame);
  if (!panel.open || reducedMotion.matches || !panel.classList.contains('shown')) {
    finishClose(current);
    return;
  }

  const onEnd = event => {
    if (event.target === panel && ['opacity', 'transform'].includes(event.propertyName)) {
      finishClose(current);
    }
  };
  // Never require a transition event: cancellation, missing events and style changes are valid.
  const deadline = setTimeout(() => finishClose(current), 220);
  current.stopWaiting = () => {
    clearTimeout(deadline);
    panel.removeEventListener('transitionend', onEnd);
    panel.removeEventListener('transitioncancel', onEnd);
  };
  panel.addEventListener('transitionend', onEnd);
  panel.addEventListener('transitioncancel', onEnd);
  panel.classList.add('closing');
  panel.classList.remove('shown');
  if (getComputedStyle(panel).transitionDuration.split(',').every(value => parseFloat(value) === 0)) {
    finishClose(current);
  }
}

filters.onclick = open;
document.querySelector('#cancel').onclick = close;
document.querySelector('#apply').onclick = () => {
  if (!session || session.closing) return;
  activeUnpaid = unpaid.checked;
  render();
  close();
};
panel.addEventListener('cancel', event => {
  event.preventDefault();
  close();
});
panel.addEventListener('close', () => {
  // A native close event may be queued until after the next open.
  if (session && !panel.open) finishClose(session);
});
reducedMotion.addEventListener('change', () => {
  if (!session || !reducedMotion.matches) return;
  if (session.closing) {
    finishClose(session);
  } else {
    cancelAnimationFrame(session.frame);
    panel.classList.add('shown');
  }
});
render();
