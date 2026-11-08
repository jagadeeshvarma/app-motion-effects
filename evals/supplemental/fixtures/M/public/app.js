import {readOrder,moveTask} from './model.js';
let order=readOrder();const list=document.querySelector('#rounds');
function placeRows(){
 const active=document.activeElement;
 const selection=active?.matches('input[type=text]')?[active.selectionStart,active.selectionEnd]:null;
 for(const id of order)list.append(document.querySelector(`[data-task="${id}"]`));
 if(active?.isConnected){active.focus({preventScroll:true});if(selection)active.setSelectionRange(...selection)}
 for(const button of document.querySelectorAll('[data-direction]')){const i=order.indexOf(button.dataset.id);button.disabled=Number(button.dataset.direction)<0?i===0:i===order.length-1;}
}
document.querySelectorAll('[data-direction]').forEach(button=>button.addEventListener('click',()=>{order=moveTask(order,button.dataset.id,Number(button.dataset.direction));placeRows();document.querySelector('#feedback').textContent=`Task moved to position ${order.indexOf(button.dataset.id)+1}`;}));
placeRows();
