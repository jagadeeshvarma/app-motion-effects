import {updateAddress} from './api.js';

const address = document.querySelector('#address');
const permission = document.querySelector('#permission');
const save = document.querySelector('#save');
const feedback = document.querySelector('#feedback');
let pending = false;
let savedAddress;
let feedbackMotion;

function showFeedback(state, message) {
  feedbackMotion?.cancel();
  feedback.dataset.state = state;
  feedback.textContent = message;

  // The result is available immediately; motion never gates feedback or retry.
  if (!window.matchMedia('(prefers-reduced-motion: reduce)').matches && feedback.animate) {
    const styles = getComputedStyle(feedback);
    feedbackMotion = feedback.animate(
      [{opacity: 0.65, transform: 'translateY(3px)'}, {opacity: 1, transform: 'translateY(0)'}],
      {duration: parseFloat(styles.getPropertyValue('--motion-normal')), easing: styles.getPropertyValue('--ease').trim()}
    );
  }
}

// A later draft must never inherit the previous address's success message.
address.addEventListener('input', () => {
  if (!pending && feedback.dataset.state === 'success' && address.value !== savedAddress) {
    showFeedback('draft', 'Unsaved changes.');
  }
});

window.matchMedia('(prefers-reduced-motion: reduce)').addEventListener('change', event => {
  if (event.matches) feedbackMotion?.cancel();
});

save.onclick = async () => {
  if (pending) return;
  pending = true;
  const submittedAddress = address.value;
  const submittedPermission = permission.value;
  save.disabled = true;
  save.setAttribute('aria-busy', 'true');
  save.textContent = 'Saving…';
  showFeedback('pending', 'Saving address…');

  try {
    await updateAddress(submittedAddress, submittedPermission);
    savedAddress = submittedAddress;
    showFeedback('success', address.value === savedAddress
      ? 'Saved'
      : 'Address saved. Your latest changes are not saved.');
  } catch (error) {
    const message = error.code === 401
      ? 'Session expired (401). Your address is kept. In this local demo, choose Editor under Synthetic permission, then select Save address to retry.'
      : error.code === 403
        ? 'Permission denied (403). Your address is kept. Choose Editor under Synthetic permission, then select Save address to retry.'
        : 'Address could not be saved. Your address is kept. Select Save address to retry.';
    showFeedback('error', message);
  } finally {
    pending = false;
    save.disabled = false;
    save.removeAttribute('aria-busy');
    save.textContent = 'Save address';
  }
};
