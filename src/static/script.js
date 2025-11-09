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

  const drums = document.createElement('div');
  drums.className = "drums";

  const drumsCheckbox = document.createElement('input');
  drumsCheckbox.type = 'checkbox';
  drumsCheckbox.className = "drum-checkbox"
  drumsCheckbox.id = `drums-${file.name}`;
  const checkboxLabel = document.createElement('label');
  checkboxLabel.textContent = 'Only Mix Percussion';
  checkboxLabel.htmlFor = drumsCheckbox.id;

  drums.appendChild(drumsCheckbox);
  drums.appendChild(checkboxLabel);

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

    // Create the remove button
  const removeButton = document.createElement('button');
  removeButton.textContent = 'Remove';
  removeButton.className = 'remove-btn';
  
  // Add event listener to remove the file row on button click
  removeButton.addEventListener('click', () => {
    fileList.removeChild(li);

        // Remove the file from new_files
    new_files = new_files.filter(f => f.original_filename !== file.name);

    // Remove the file from the input files array
    // filesArray = files.filter(f => f.name !== file.name);

    if (new_files.length == 0){
      document.getElementById('collide').style.display = "none";
      
    }
    
  });


  li.appendChild(topRow);
  li.appendChild(meta);
  li.appendChild(drums);
  li.appendChild(removeButton);  // Append the remove button to the list item

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
        reject(new Error('Invalid audio file '));
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
  // fileList.innerHTML = '';
  var files = Array.from(input.files);
  if (files.length === 0) {
    // summary.textContent = '';
    return;
  }



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

        info.original_filename = file.name;
        new_files.push(info);

        if (new_files.length == files.length) {
            document.getElementById("collide").style.display = "";
        }
        
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

  

  
  // reset input so same files can be selected again if desired
  input.value = '';
});

let collide = document.getElementById("collide");

collide.addEventListener('click', () => {
  collide.textContent = "Colliding..."
  const filesWithDrumFlag = new_files.map(file => {
    const checkbox = document.getElementById(`drums-${file.original_filename}`); // Assuming file has a filename property
    return {
      ...file,
      drumsOnly: checkbox ? checkbox.checked : false // Read the checkbox value, default to false if not found
    };
  });
  fetch('/collide', {
        method: 'POST', // Use the POST method to send data
        headers: {
            'Content-Type': 'application/json', // Specify the content type
        },
        body: JSON.stringify(filesWithDrumFlag), // Convert the object to JSON
    })
    .then(response => response.json()) // Parse the JSON response
    .then(responseJson => {
      const audioUrl = `data:audio/wav;base64,${responseJson.file}`;

        const audioElement = document.getElementById("audio");
        audioElement.src = audioUrl;

        const audioWrapper = document.getElementById("audio-wrapper");
       

        audioWrapper.style.display = ""

        let meta = document.getElementById("audio-meta");

        let info = responseJson;
        const parts = [];
        if (info.genre) parts.push(`Genre: ${info.genre}`);
        if (typeof info.tempo !== 'undefined') parts.push(`Tempo: ${info.tempo}`);

        meta.textContent = parts.join(' • ');

        // Optionally, play the audio automatically
        audioElement.play();
        collide.textContent = "Collide!";
    })
    .catch((error) => {
        console.error('Error:', error); // Handle any errors
    });
  
});

const downloadBtn = document.querySelector('.download-btn');
const audioElement = document.getElementById('audio');

// Add event listener to the download button
downloadBtn.addEventListener('click', () => {
  const audioSrc = audioElement.src; // Get the audio source URL
  if (audioSrc) {
    const a = document.createElement('a'); // Create a temporary anchor element
    a.href = audioSrc; // Set the href to the audio source
    a.download = 'audio-file.wav'; // Set the download attribute
    document.body.appendChild(a); // Append the anchor to the body
    a.click(); // Programmatically click the anchor to trigger the download
    document.body.removeChild(a); // Remove the anchor from the DOM
  } else {
    alert('No audio file available for download.'); // Alert if no audio is found
  }
});
