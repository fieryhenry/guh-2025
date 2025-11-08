const input = document.getElementById('files');
const fileList = document.getElementById('fileList');
const summary = document.getElementById('summary');

function formatBytes(bytes) {
  if (bytes === 0) return '0 B';
  const units = ['B','KB','MB','GB','TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  return (bytes / Math.pow(1024, i)).toFixed(2) + ' ' + units[i];
}

// create a UI row for a file and return elements to update
function createFileRow(file) {
  const li = document.createElement('li');
  li.className = "audio-list-item"
  const name = document.createElement('div');
  name.textContent = file.name;

  const progWrap = document.createElement('div');
  progWrap.className = "prog-wrap";
  const prog = document.createElement('div');
  prog.className = "prog"
  progWrap.appendChild(prog);

  const status = document.createElement('div');
  status.className = "status";
  status.textContent = 'Queued';

  const meta = document.createElement('div');
  meta.className = "meta";

  const topRow = document.createElement('div');
  topRow.className = "top-row";
  topRow.appendChild(name);
  topRow.appendChild(progWrap);
  topRow.appendChild(status);
  li.appendChild(topRow);
  li.appendChild(meta);

  fileList.appendChild(li);
  return { li, prog, status, meta, progWrap };
}

// upload a single file using XMLHttpRequest to get progress, return parsed JSON
function uploadSingleFile(file, onProgress) {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    xhr.open('POST', '/upload', true);
    xhr.responseType = 'json';

    xhr.upload.addEventListener('progress', (e) => {
      if (e.lengthComputable && onProgress) {
        onProgress(e.loaded / e.total);
      }
    });

    xhr.onload = () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        // server returns an object like {"<filename>": {"genre":"x","tempo":120}}
        resolve(xhr.response);
      } else {
        reject(new Error('Upload failed: ' + xhr.status));
      }
    };

    xhr.onerror = () => reject(new Error('Network error'));
    xhr.onabort = () => reject(new Error('Upload aborted'));

    const form = new FormData();
    form.append('file', file, file.name);
    xhr.send(form);
  });
}

var new_files = [];

input.addEventListener('change', () => {
  fileList.innerHTML = '';
  const files = Array.from(input.files);
  if (files.length === 0) {
    summary.textContent = '';
    return;
  }

  let total = 0;
  files.forEach(f => total += f.size);
  summary.textContent = `${files.length} file(s), total ${formatBytes(total)}`;

  // Start uploading each file (parallel). Wait for response per file and update UI.
  files.forEach(file => {
    const { prog, status, meta, progWrap } = createFileRow(file);
    status.textContent = 'Uploading...';

    uploadSingleFile(file, (fraction) => {
      prog.style.width = Math.round(fraction * 100) + '%';
    }).then(responseJson => {
      // responseJson expected: { { "genre": "...", "tempo": ... } }
      prog.style.width = '100%';
      progWrap.style.display = 'none';
      status.style.display = 'none';
      status.textContent = 'Done';

      const info = responseJson;
      // Display genre and tempo if present
      if (info && (info.genre || info.tempo || info.tempo === 0)) {
        const parts = [];
        if (info.genre) parts.push(`Genre: ${info.genre}`);
        if (typeof info.tempo !== 'undefined') parts.push(`Tempo: ${info.tempo}`);
        let filename = info.filename;

        new_files.push(info);

        
        meta.textContent = parts.join(' • ');
      } else {
        // if server returned other shape, show it
        meta.textContent = JSON.stringify(responseJson);
      }
    }).catch(err => {
      prog.style.background = '#e55353';
      status.textContent = 'Error';
      meta.textContent = err.message || 'Upload failed';
      console.error('Upload error', err);
    });
  });

  
  if (files.length != 0) {
      document.getElementById("collide").style.display = "";
  }

  // reset input so same files can be selected again if desired
  input.value = '';
});

let collide = document.getElementById("collide");

collide.addEventListener('click', () => {
  fetch('/collide', {
        method: 'POST', // Use the POST method to send data
        headers: {
            'Content-Type': 'application/json', // Specify the content type
        },
        body: JSON.stringify(new_files), // Convert the object to JSON
    })
    .then(response => response.blob()) // Parse the JSON response
    .then(blob => {
      const audioUrl = URL.createObjectURL(blob);

        const audioElement = document.getElementById("audio");
        audioElement.src = audioUrl;
       

        audioElement.style.display = ""

        // Optionally, play the audio automatically
        audioElement.play();
    })
    .catch((error) => {
        console.error('Error:', error); // Handle any errors
    });
  
});
