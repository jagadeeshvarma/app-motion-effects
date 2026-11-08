import { saveNote, listNotes } from './api.js';
const draft=document.querySelector('#draft');
function render(){const list=document.querySelector('#notes');list.replaceChildren(...listNotes().map(note=>{const item=document.createElement('li');item.textContent=note.text;return item}));}
render();
// Add the note workflow here. The repository deliberately resolves later.
