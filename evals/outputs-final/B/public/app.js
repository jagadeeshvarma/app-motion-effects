const records={one:{title:'Lamp 12',draft:'Check the cable',priority:false},two:{title:'Chair 4',draft:'Inspect the joint',priority:true}};
let selected;
const input=document.querySelector('#draft'),priority=document.querySelector('#priority');
const title=document.querySelector('#record-title');
const reducedMotion=window.matchMedia('(prefers-reduced-motion: reduce)');
let selectionCue;

function cancelSelectionCue(){
  selectionCue?.cancel();
  selectionCue=undefined;
}

function cueSelection(){
  // Retarget immediately: never queue record changes or animate the editable form.
  cancelSelectionCue();
  if(reducedMotion.matches || typeof title.animate!=='function') return;
  const tokens=getComputedStyle(document.documentElement);
  selectionCue=title.animate([{opacity:.65},{opacity:1}],{
    // CONVENTIONS.md's motion tokens use milliseconds.
    duration:parseFloat(tokens.getPropertyValue('--motion-fast')),
    easing:tokens.getPropertyValue('--ease').trim()
  });
}

reducedMotion.addEventListener('change',()=>{
  if(reducedMotion.matches) cancelSelectionCue();
});

function show(id){
  // Reselecting the current record must not reset the textarea's caret.
  if(id===selected) return;
  const switching=selected!==undefined;
  selected=id;
  title.textContent=records[id].title;
  input.value=records[id].draft;
  priority.checked=records[id].priority;
  document.querySelectorAll('[data-record]').forEach(button=>button.setAttribute('aria-pressed',String(button.dataset.record===id)));
  if(switching) cueSelection();
}
input.addEventListener('input',()=>records[selected].draft=input.value);priority.addEventListener('change',()=>records[selected].priority=priority.checked);
document.querySelectorAll('[data-record]').forEach(button=>button.addEventListener('click',()=>show(button.dataset.record)));show('one');
