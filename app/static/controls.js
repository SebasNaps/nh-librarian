

import { socket } from "./socket.js";

// Grab references
const idSourceBtn = document.getElementById('idSourceBtn');
const idSourceMenu = document.getElementById('idSourceMenu');

// When any item is clicked...
idSourceMenu.querySelectorAll('a').forEach(item => {
    item.addEventListener('click', e => {
        e.preventDefault();
        const choice = item.getAttribute('data-value');
        const label = item.textContent.trim();

        // 1) Update the button text
        idSourceBtn.textContent = label + ' ▾';

        // 2) Store the value somewhere (e.g. on the button)
        idSourceBtn.setAttribute('data-selected', choice);

        // 3) Optionally close the menu (if you switch to click‐to‐open behavior)
        idSourceMenu.style.display = 'none';
    });
});

// (Optional) If you want click-to-toggle instead of hover:
idSourceBtn.addEventListener('click', () => {
    const isVisible = idSourceMenu.style.display === 'block';
    idSourceMenu.style.display = isVisible ? 'none' : 'block';
});

// Grab references
const modeBtn = document.getElementById('modeBtn');
const modeMenu = document.getElementById('modeMenu');

// When any item is clicked...
modeMenu.querySelectorAll('a').forEach(item => {
    item.addEventListener('click', e => {
        e.preventDefault();
        const choice = item.getAttribute('data-value');
        const label = item.textContent.trim();

        // 1) Update the button text

        modeBtn.textContent = label + ' ▾';

        const idSourceBtn = document.getElementById('idSourceBtn');
        const runUntilBtn = document.getElementById('runUntilBtn');
        if (choice == 'auto') {

            idSourceBtn.style.display = 'None';
            runUntilBtn.style.display = 'None';
        } else if (choice == 'custom') {
            idSourceBtn.style.display = 'inline-block';
            runUntilBtn.style.display = 'inline-block';
        }

        // 2) Store the value somewhere (e.g. on the button)
        modeBtn.setAttribute('data-selected', choice);

        // 3) Optionally close the menu (if you switch to click‐to‐open behavior)
        modeMenu.style.display = 'none';
    });
});

// (Optional) If you want click-to-toggle instead of hover:
modeBtn.addEventListener('click', () => {
    const isVisible = modeMenu.style.display === 'block';
    modeMenu.style.display = isVisible ? 'none' : 'block';
});

// Grab references
const runUntilBtn = document.getElementById('runUntilBtn');
const runUntilMenu = document.getElementById('runUntilMenu');

// When any item is clicked...
runUntilMenu.querySelectorAll('a').forEach(item => {
    item.addEventListener('click', e => {
        e.preventDefault();
        const choice = item.getAttribute('data-value');
        const label = item.textContent.trim();

        // 1) Update the button text
        if (choice == 'cbz') {
            runUntilBtn.textContent = 'Run all ▾';
        } else {
            runUntilBtn.textContent = 'Until:' + label + ' ▾';

        }
        // 2) Store the value somewhere (e.g. on the button)
        runUntilBtn.setAttribute('data-selected', choice);

        // 3) Optionally close the menu (if you switch to click‐to‐open behavior)
        runUntilMenu.style.display = 'none';
    });
});

// (Optional) If you want click-to-toggle instead of hover:
runUntilBtn.addEventListener('click', () => {
    const isVisible = runUntilMenu.style.display === 'block';
    runUntilMenu.style.display = isVisible ? 'none' : 'block';
});

// startStopBtn = document.getElementById('start-stop-btn');

document.getElementById('start-stop-btn').onclick = () => {
    // socket.emit('send_test');

    if (document.getElementById('start-stop-btn').dataset.state === 'start') {

        const mode = modeBtn.getAttribute('data-selected');

        if (!mode) {
            // socket.emit('log_stuff', 'No mode set.');
        } else {
            const id_source = idSourceBtn.getAttribute('data-selected');
            const run_until = runUntilBtn.getAttribute('data-selected');
            if (mode === 'auto') {
                document.getElementById('start-stop-btn').dataset.state = 'stop';

                document.getElementById('start-stop-btn').classList.add('btn-stop');      // add the red stop style
                document.getElementById('start-stop-btn').textContent = 'Stop';            // change the text

                socket.emit('start_tasks', mode);
            } else if (mode === 'custom') {
                if (!!id_source && !!run_until) {
                    document.getElementById('start-stop-btn').dataset.state = 'stop';

                    document.getElementById('start-stop-btn').classList.add('btn-stop');      // add the red stop style
                    document.getElementById('start-stop-btn').textContent = 'Stop';            // change the text

                    socket.emit('start_tasks', { 'mode': mode, 'id_source': id_source, 'run_until': run_until });

                } else {
                    socket.emit('log_stuff', 'Mode set to custom but other settings not set.');
                }

            }
        }
    } else {
        socket.emit('stop_run', '9xE3XB93eFQq8Tne');
        document.getElementById('start-stop-btn').dataset.state = 'start'
    }

};

socket.on('progress_complete', () => {
    document.getElementById('start-stop-btn').classList.remove('btn-stop');
    document.getElementById('start-stop-btn').dataset.state = 'start'
    document.getElementById('start-stop-btn').textContent = 'Start';
});

socket.on('progress_stopped', () => {
    document.getElementById('start-stop-btn').dataset.state = 'start'
    document.getElementById('start-stop-btn').textContent = 'Stopped';
})

socket.on('run_stopping', () => {
    document.getElementById('start-stop-btn').classList.remove('btn-stop');
    document.getElementById('start-stop-btn').textContent = 'Stopping...';
});



socket.on('update.control', ({ mode, id_source, run_until, start_button }) => {
    socket.emit('frontend_log', `update.control:`)
    socket.emit('frontend_log', `mode: ${mode}`)
    socket.emit('frontend_log', `id_source: ${id_source}`)
    socket.emit('frontend_log', `run_until: ${run_until}`)
    socket.emit('frontend_log', `start_button: ${start_button}`)

    if (start_button == 'start') {
        document.getElementById('start-stop-btn').classList.remove('btn-stop');
        document.getElementById('start-stop-btn').dataset.state = 'start'
        document.getElementById('start-stop-btn').textContent = 'Start';

    } else if (start_button == 'stop') {
        document.getElementById('start-stop-btn').dataset.state = 'stop';
        document.getElementById('start-stop-btn').classList.add('btn-stop');
        document.getElementById('start-stop-btn').textContent = 'Stop';

    } else if (start_button == 'stopping') {
        document.getElementById('start-stop-btn').classList.remove('btn-stop');
        document.getElementById('start-stop-btn').textContent = 'Stopping...';

    } else if (start_button == 'stopped') {
        document.getElementById('start-stop-btn').classList.remove('btn-stop');
        document.getElementById('start-stop-btn').dataset.state = 'start'
        document.getElementById('start-stop-btn').textContent = 'Stopped';
    } else {
        document.getElementById('start-stop-btn').classList.remove('btn-stop');
        document.getElementById('start-stop-btn').dataset.state = 'start'
        document.getElementById('start-stop-btn').textContent = 'Start';
    }

    if (mode == 'auto') {
        modeBtn.textContent = "Automatic Mode ▾"
        modeBtn.setAttribute('data-selected', "auto");
        idSourceBtn.style.display = 'None';
        runUntilBtn.style.display = 'None';
    } else if (mode == 'custom') {
        modeBtn.textContent = "Custom Mode ▾"
        modeBtn.setAttribute('data-selected', "custom");
        idSourceBtn.style.display = 'inline-block';
        runUntilBtn.style.display = 'inline-block';

        switch(id_source){
            case 'favs':
                idSourceBtn.textContent = 'Favorites from Pages ▾';
                idSourceBtn.setAttribute('data-selected', "favs");
                break;
            case 'pre_fetched_favs':
                idSourceBtn.textContent = 'Pre-Fetched Favorites ▾';
                idSourceBtn.setAttribute('data-selected', "pre_fetched_favs");
                break;
            case 'id_list':
                idSourceBtn.textContent = 'Manual ID List ▾';
                idSourceBtn.setAttribute('data-selected', "id_list");
                break;
        }

        switch (run_until) {
            case 'favs':
                runUntilBtn.textContent = 'Fetch Favorites ▾';
                runUntilBtn.setAttribute('data-selected', "favs");
                break;
            case 'meta':
                runUntilBtn.textContent = 'Fetch Metadata ▾';
                runUntilBtn.setAttribute('data-selected', "meta");
                break;
            case 'urls':
                runUntilBtn.textContent = 'Fetch URLs ▾';
                runUntilBtn.setAttribute('data-selected', "urls");
                break;
            case 'down':
                runUntilBtn.textContent = 'Download Images ▾';
                runUntilBtn.setAttribute('data-selected', "down");
                break;
            case 'cbz':
                runUntilBtn.textContent = 'Run all ▾';
                runUntilBtn.setAttribute('data-selected', "cbz");
                break;
        }
    }
})