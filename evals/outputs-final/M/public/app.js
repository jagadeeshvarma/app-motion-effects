import {readOrder, moveTask} from './model.js';

let order = readOrder();
const list = document.querySelector('#rounds');
const rows = new Map([...list.children].map(row => [row.dataset.task, row]));
const buttons = [...list.querySelectorAll('[data-direction]')];
const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)');
const movements = new Map();

function stopMovements() {
 for (const [row, animation] of movements) {
  animation.cancel();
  row.classList.remove('is-moving');
 }
 movements.clear();
}

function placeRows() {
 const active = document.activeElement;
 const selection = active?.matches('input[type=text]')
  ? [active.selectionStart, active.selectionEnd, active.selectionDirection] : null;

 // Keep existing row/input nodes. moveBefore also preserves browser focus
 // and selection natively; older browsers use the same nodes with restoration.
 order.forEach((id, index) => {
  const row = rows.get(id);
  const atIndex = list.children[index];
  if (row !== atIndex) {
   if (list.moveBefore) list.moveBefore(row, atIndex ?? null);
   else list.insertBefore(row, atIndex ?? null);
  }
 });
 for (const button of buttons) {
  const index = order.indexOf(button.dataset.id);
  button.disabled = Number(button.dataset.direction) < 0
   ? index === 0 : index === order.length - 1;
 }

 // At an edge, keep keyboard users on the same task's usable move control.
 let focus = active;
 if (active?.matches('[data-direction]') && active.disabled) {
  focus = buttons.find(button => button.dataset.id === active.dataset.id && !button.disabled);
 }
 if (focus?.isConnected) {
  if (document.activeElement !== focus) focus.focus({preventScroll: true});
  if (selection) active.setSelectionRange(...selection);
 }
}

function animateRows(before, movedId) {
 if (reducedMotion.matches) return;
 const style = getComputedStyle(list);
 const durationToken = style.getPropertyValue('--motion-normal').trim();
 const duration = parseFloat(durationToken) * (durationToken.endsWith('ms') ? 1 : 1000);
 const easing = style.getPropertyValue('--ease').trim();
 const after = new Map([...rows].map(([id, row]) => [id, row.getBoundingClientRect().top]));

 for (const [id, row] of rows) {
  const offset = before.get(id) - after.get(id);
  if (Math.abs(offset) < .5 || !row.animate) continue;
  const animation = row.animate([
   {transform: `translateY(${offset}px)`},
   {transform: 'translateY(0)'}
  ], {duration, easing});
  movements.set(row, animation);
  if (id === movedId) row.classList.add('is-moving');
  animation.onfinish = () => {
   if (movements.get(row) !== animation) return;
   movements.delete(row);
   row.classList.remove('is-moving');
  };
 }
}

buttons.forEach(button => button.addEventListener('click', () => {
 // Sample displayed positions BEFORE cancellation so rapid/opposite moves
 // continue from there instead of jumping to an earlier target.
 const before = new Map([...rows].map(([id, row]) => [id, row.getBoundingClientRect().top]));
 stopMovements();
 order = moveTask(order, button.dataset.id, Number(button.dataset.direction));
 placeRows();
 animateRows(before, button.dataset.id);
 document.querySelector('#feedback').textContent = `Task moved to position ${order.indexOf(button.dataset.id) + 1}`;
}));

reducedMotion.addEventListener('change', () => {
 if (reducedMotion.matches) stopMovements();
});
// A resize can change row heights; settle into the already-committed layout.
window.addEventListener('resize', stopMovements);
placeRows();
