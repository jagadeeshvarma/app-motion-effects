import { saveNote, listNotes } from './api.js';

const draft = document.querySelector('#draft');
const save = document.querySelector('#save');
const failNext = document.querySelector('#fail-next');
const feedback = document.querySelector('#feedback');
const notes = document.querySelector('#notes');
const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
const tokens = getComputedStyle(document.documentElement);
let saving = false;
let feedbackMotion;

function showFeedback(state, message) {
  feedbackMotion?.cancel();
  feedback.dataset.state = state;
  feedback.textContent = message;
  if (message && !reducedMotion.matches) {
    feedbackMotion = feedback.animate(
      [{ opacity: 0.55 }, { opacity: 1 }],
      {
        duration: parseFloat(tokens.getPropertyValue('--motion-fast')),
        easing: tokens.getPropertyValue('--ease').trim(),
      },
    );
  }
}

reducedMotion.addEventListener('change', () => {
  if (reducedMotion.matches) feedbackMotion?.cancel();
});

function noteItem(note) {
  const item = document.createElement('li');
  item.dataset.noteId = note.id;
  item.textContent = note.text;
  return item;
}

notes.replaceChildren(...listNotes().map(noteItem));
draft.setAttribute('aria-describedby', 'feedback');

draft.addEventListener('input', () => {
  if (!saving) {
    save.textContent = 'Save note';
    showFeedback('idle', '');
  }
});

save.addEventListener('click', async () => {
  if (saving) return;

  const submittedText = draft.value;
  if (!submittedText.trim()) {
    showFeedback('error', 'Enter a note.');
    draft.focus();
    return;
  }

  saving = true;
  save.disabled = true;
  failNext.disabled = true;
  save.textContent = 'Saving…';
  save.setAttribute('aria-busy', 'true');
  showFeedback('saving', 'Saving note…');

  try {
    const note = await saveNote(submittedText, { fail: failNext.checked });
    const item = noteItem(note);
    if (!reducedMotion.matches) {
      const clearArrival = () => {
        item.classList.remove('note-arriving');
        item.removeEventListener('animationend', clearArrival);
        item.removeEventListener('animationcancel', clearArrival);
      };
      item.addEventListener('animationend', clearArrival);
      item.addEventListener('animationcancel', clearArrival);
      item.classList.add('note-arriving');
    }
    notes.append(item);

    // A draft edited during the request belongs to the next save.
    const unchanged = draft.value === submittedText;
    if (unchanged) draft.value = '';
    save.textContent = 'Save note';
    showFeedback('success', unchanged ? 'Note saved.' : 'Note saved. Your new draft is still here.');
  } catch {
    save.textContent = 'Retry save';
    showFeedback('error', 'Save failed. Your note is still here. Try again.');
  } finally {
    saving = false;
    save.disabled = false;
    failNext.disabled = false;
    save.removeAttribute('aria-busy');
  }
});
