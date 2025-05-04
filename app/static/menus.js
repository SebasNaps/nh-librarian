
import { socket } from "./socket.js";

const cookieOverlay = document.getElementById('cookieOverlay');
const cookieModal = document.getElementById('cookieModal');
const idsOverlay = document.getElementById('idsOverlay');
const idsModal = document.getElementById('idsModal');
const idListInput = document.getElementById('id_list');

// Cookie Overlay controls
document.getElementById('cookie-btn').onclick = () => { cookieOverlay.classList.add('active'); cookieModal.classList.add('active'); };
const close_cookie = () => { cookieOverlay.classList.remove('active'); cookieModal.classList.remove('active'); };
document.getElementById('cookie-close-btn').onclick = close_cookie;
cookieOverlay.onclick = close_cookie;
document.getElementById('cookie-save-btn').onclick = () => {
  const cookie_id = document.getElementById('cookie_id').value.trim();
  const cookie_cf = document.getElementById('cookie_cf').value.trim();
  if (!cookie_id || !cookie_cf) { alert('Both fields required'); return; }
  socket.emit('cookie_input', { cookie_id: cookie_id, cookie_cf: cookie_cf });
  close_cookie();
};

// IDs Overlay controls
document.getElementById('ids-btn').onclick = () => { idsOverlay.classList.add('active'); idsModal.classList.add('active'); };
const close_ids = () => { idsOverlay.classList.remove('active'); idsModal.classList.remove('active'); };
document.getElementById('ids-close-btn').onclick = close_ids;
idsOverlay.onclick = close_ids;
document.getElementById('ids-save-btn').onclick = () => {
  const id_list = idListInput.value.trim();
  if (!id_list) { alert('No IDs were input'); return; }
  socket.emit('ids_input', { id_list: id_list });
  close_ids();
};



