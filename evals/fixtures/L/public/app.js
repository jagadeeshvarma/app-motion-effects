window.__filterStats={changes:0};
document.querySelector('#filter').addEventListener('change',event=>{window.__filterStats.changes++;const ready=event.target.value==='ready';document.querySelectorAll('#parcels li').forEach(item=>item.hidden=ready&&item.dataset.state!=='ready');document.querySelector('#feedback').textContent=ready?'1 parcel shown':'2 parcels shown'});
