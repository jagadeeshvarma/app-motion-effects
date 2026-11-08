import {updateAddress} from './api.js';
document.querySelector('#save').onclick=async()=>{const feedback=document.querySelector('#feedback');feedback.textContent='Saved';try{await updateAddress(document.querySelector('#address').value,document.querySelector('#permission').value)}catch(error){console.info(error.code)}};
