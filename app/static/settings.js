
import { socket } from "./socket.js";


const advanced = document.getElementById('advanced-settings');

// Advanced Options
document.getElementById('toggle-advanced').onclick = () => { advanced.classList.toggle('active'); };
document.getElementById('apply-adv').onclick = () => {
  const convert = document.getElementById('convert-checkbox').checked;
  const autodelete = document.getElementById('autodelete-checkbox').checked;
  const live_progress = document.getElementById('live-progress-checkbox').checked;
  const webp = document.getElementById('webp-quality').value;
  const cbz = document.getElementById('cbz-quality').value;
  const retry = document.getElementById('error-retry').value;
  socket.emit('apply_settings', { convert, autodelete, live_progress, webp, cbz, retry});
};
document.getElementById('reset-adv').onclick = () => {
  socket.emit('reset_settings')

  ['convert-checkbox', 'autodelete-checkbox'].forEach(id => document.getElementById(id).value = '1');
  ['live-progress-checkbox'].forEach(id => document.getElementById(id).value = '0');
  ['webp-quality', 'cbz-quality', 'error-retry'].forEach(id => document.getElementById(id).value = '');
};