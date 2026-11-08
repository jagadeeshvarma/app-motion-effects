const records={one:{title:'Lamp 12',draft:'Check the cable',priority:false},two:{title:'Chair 4',draft:'Inspect the joint',priority:true}};
let selected='one';const input=document.querySelector('#draft'),priority=document.querySelector('#priority');
function show(id){selected=id;document.querySelector('#record-title').textContent=records[id].title;input.value=records[id].draft;priority.checked=records[id].priority;document.querySelectorAll('[data-record]').forEach(button=>button.setAttribute('aria-pressed',String(button.dataset.record===id)));}
input.addEventListener('input',()=>records[selected].draft=input.value);priority.addEventListener('change',()=>records[selected].priority=priority.checked);
document.querySelectorAll('[data-record]').forEach(button=>button.addEventListener('click',()=>show(button.dataset.record)));show(selected);
