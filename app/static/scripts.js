


import { socket } from "./socket.js";     // <-- pulls in `socket`
import "./menus.js";                      // <-- registers menu handlers
import "./progress.js";                   // <-- registers progress handlers
import "./settings.js"
import "./controls.js"
// import "./explorer.js";                   // <-- (if you eventually add file-explorer code)
// import "./logs.js";                       // <-- (if you eventually add log code)

document.addEventListener('DOMContentLoaded', () => {
  // Parse combined JSON containing state + mode
  
  socket.emit('log_stuff', "Page (re)loaded. Fetching current state.")
  socket.emit('first_loaded')

});

document.getElementById('test-btn').onclick = () => {
  socket.emit('send_test');
  socket.emit('set_settings', {'k': 2});
  // socket.emit('testy');
  document.getElementById('test-btn').disabled = true;
};

socket.on('progress_complete', () => {
  document.getElementById('test-btn').disabled = false;
});

