const key='maintenance-order-v1';const initial=['valve','pump','meter'];
window.__moveStats={moves:0};
export function readOrder(){try{const value=JSON.parse(localStorage.getItem(key));if(Array.isArray(value)&&value.length===3&&new Set(value).size===3&&initial.every(id=>value.includes(id)))return value}catch{}return [...initial]}
export function moveTask(order,id,direction){const index=order.indexOf(id),target=index+direction;if(index<0||target<0||target>=order.length)return [...order];const next=[...order];[next[index],next[target]]=[next[target],next[index]];localStorage.setItem(key,JSON.stringify(next));window.__moveStats.moves++;return next}
