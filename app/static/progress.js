
import { socket } from "./socket.js";

// Handle Progress Text

socket.on('update.progress', ({ type, current, total }) => {
  socket.emit('frontend_log', `update.status:`)
  socket.emit('frontend_log', `type: ${type}`)
  socket.emit('frontend_log', `current: ${current}`)
  socket.emit('frontend_log', `total: ${total}`)
  switch (type) {
    case 'favorites':
      let txt = document.getElementById('progress-favs')

      if (total) {
        txt.innerText = `Complete. ${current} pages found.`
      } else {
        txt.innerText = `${current} pages`
      }
      break;
    case 'total':
      updateProgress('total', current, total)
      break;
    case 'error':
      let errs = document.getElementById('errors-text');
      if (current != 0) {
        errs.innerText = `${current} error(s)`;
      } else {
        errs.innerText = "";
      }
      updateProgress('error', current, total);
      break;
    case 'doujin':
      // socket.emit('log_stuff', "Updating Step of current doujin.")
      // text element: id="progress-text-<type>"
      let douj = document.getElementById(`progress-doujin-step`);
      if (douj) {
        // show raw current/total instead of percent
        // socket.emit('log_stuff',"Current step")
        // socket.emit('log_stuff',current)
        let doujtext = ""
        switch (current) {
          case 0:
            doujtext = "Fetching Favorites";
            break;
          case 1:
            doujtext = "Fetching Metadata";
            break;
          case 2:
            doujtext = "Fetching URLs";
            break;
          case 3:
            doujtext = "Downloading Images";
            break;
          case 4:
            doujtext = "Converting Images";
            break;
          case 5:
            doujtext = "Creating .cbz Archives";
            break;
          default:
            doujtext = "";
            break;
        }
        // socket.emit('log_stuff', `Current Step ${doujtext}`)
        douj.innerText = `Current Step: ${doujtext}`;
      }

      updateProgress('doujin', current, total);
      break;
    case 'urls':
      updateProgress('urls', current, total);
      break;
    case 'downloads':
      updateProgress('down', current, total);
      break;
    case 'conversion':
      updateProgress('conv', current, total);
      break;
  }
})

socket.on('update.doujin_info', ({title, id, author, tags})=>{
  // const image = 

  let title_txt = document.getElementById('doujin-title')
  let id_txt = document.getElementById('doujin-id')
  let author_txt = document.getElementById('doujin-author')
  let tags_txt = document.getElementById('doujin-tags')

  title_txt.textContent = title;
  id_txt.textContent = id;
  author_txt.textContent = author;
  tags_txt.textContent = tags;

  id_txt.href = `https://nhentai.net/g/${id}/`

})

socket.on('update.cover', ( image ) => {
  socket.emit('frontend_log', `Update cover to: ${image}`)
  if (image) {
    // Encode each path segment so spaces and special chars are safe
    const encodedPath = image
      .split('/')
      .map(encodeURIComponent)
      .join('/');
    const start = image.slice(0, 4)

    // Build URL to your download_file route:
    //  /downloads/download/<path:filename>
    if (start == 'http') {
      let imgUrl = `${encodedPath}`;
      document.getElementById('cover-img').src = imgUrl;
    } else if(image=='logo'){
      document.getElementById('cover-img').src = "{{ logo_cat }}";
    } else{
      let imgUrl = `/covers/download/${encodedPath}`;
      document.getElementById('cover-img').src = imgUrl;
      // socket.emit('log_stuff', encodedPath)
    }
  }
})

socket.on('update.cover_visibility', (data)=>{
  set_cover_visibility(data)
})


socket.on('update.settings', ({convert_to_webp, deleter_after_archiving, save_live_progress, webp_quality, cbz_quality, max_retries}) => {
  socket.emit('frontend_log', `setting_load:`)
  socket.emit('frontend_log', `Convert to webp: ${convert_to_webp}`)
  socket.emit('frontend_log', convert_to_webp)
  // , ${deleter_after_archiving}, ${save_live_progress}, ${webp_quality}, ${cbz_quality}, ${max_retries}
  if (convert_to_webp) { 
      document.getElementById('convert-checkbox').checked = true;
    } else {
      document.getElementById('convert-checkbox').checked = false;
    }
    if (deleter_after_archiving) {
      document.getElementById('autodelete-checkbox').checked = true;
    } else {
      document.getElementById('autodelete-checkbox').checked = false;
    }
    if (save_live_progress) {
      document.getElementById('live-progress-checkbox').checked = true;
    } else {
      document.getElementById('live-progress-checkbox').checked = false;
    }
    if (webp_quality){
      document.getElementById('webp-quality').value = webp_quality;

    }
    if (cbz_quality){
      document.getElementById('cbz-quality').value = cbz_quality;

    }
    if (max_retries){
      document.getElementById('error-retry').value = max_retries;

    }
})


socket.on('setting_load', ({ convert, autodelete, live_progress, webp, cbz, retry }) => {
  // socket.emit('log_stuff', {convert, autodelete, live_progress, webp, cbz, retry})
  
  if (convert) {
    document.getElementById('convert-checkbox').checked = true;
  } else {
    document.getElementById('convert-checkbox').checked = false;
  }
  if (autodelete) {
    document.getElementById('autodelete-checkbox').checked = true;
  } else {
    document.getElementById('autodelete-checkbox').checked = false;
  }
  if (live_progress) {
    document.getElementById('live-progress-checkbox').checked = true;
  } else {
    document.getElementById('live-progress-checkbox').checked = false;
  }
  document.getElementById('webp-quality').value = webp;
  document.getElementById('cbz-quality').value = cbz;
  document.getElementById('error-retry').value = retry;


})

function updateProgress(type, current, total) {
  // socket.emit('frontend_log', `updateProgress Function:`)
  // socket.emit('frontend_log', `type: ${type}`)
  // socket.emit('frontend_log', `current: ${current}`)
  // socket.emit('frontend_log', `total: ${total}`)
  const pct = total > 0
    ? Math.round((current / total) * 100)
    : 0;

  // bar element: id="progress-<type>"
  let bar = document.getElementById(`progress-${type}`);
  // text element: id="progress-text-<type>"
  let txt = document.getElementById(`progress-${type}-text`);

  if (bar) {
    bar.style.width = `${pct}%`;
  }
  if (txt) {
    // show raw current/total instead of percent
    txt.innerText = `${current}/${total}`;
  }
};

const checkbox = document.getElementById('show-cover');
const logo_container = document.getElementById('logo-container');
const cover_container = document.getElementById('cover-container');

checkbox.addEventListener('change', () => {
  set_cover_visibility(checkbox.checked)
  socket.emit('cover_visibility', checkbox.checked)
});


logo_container.addEventListener('click', () => {
  // your JS logic here
  set_cover_visibility(true)
  socket.emit('frontend_log', "Logo clicked");
  socket.emit('cover_visibility', true)
});

cover_container.addEventListener('click', () => {
  // your JS logic here
  set_cover_visibility(false)
  socket.emit('frontend_log', "Cover clicked");
  socket.emit('cover_visibility', false)
});


function set_cover_visibility(visible){
  if (visible) {
    logo_container.style.display = 'none';
    cover_container.style.display = 'flex';
  } else {
    logo_container.style.display = 'flex';
    cover_container.style.display = 'none';
  }
}