const key='packing-notes-v1';
window.__repoStats={attempts:0,successes:0};
export function listNotes(){return JSON.parse(localStorage.getItem(key)||'[]')}
export async function saveNote(text,{fail=false}={}){window.__repoStats.attempts++;await new Promise(resolve=>setTimeout(resolve,320));if(fail)throw Error('Save failed. Try again.');if(!text.trim())throw Error('Enter a note.');const note={id:Date.now(),text:text.trim()};localStorage.setItem(key,JSON.stringify([...listNotes(),note]));window.__repoStats.successes++;return note}
