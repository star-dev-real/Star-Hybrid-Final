function getTime() {
  return new Date().toLocaleTimeString();
}

function log(message) {
  const logBox = document.getElementById("logBox");
  const line = document.createElement("div");
  line.className = "log-line";
  
  // Color coding based on message content
  if (message.includes("Error")) {
    line.style.color = "#ff3d3d";
  } else if (message.includes("started")) {
    line.style.color = "#00ff9d";
  } else if (message.includes("Detected") || message.includes("Profile")) {
    line.style.color = "#00a8ff";
  }
  
  line.textContent = message;
  logBox.appendChild(line);
  logBox.scrollTop = logBox.scrollHeight;
}

function updateStatus(status, color) {
  const statusDot = document.querySelector(".status-dot");
  const statusText = document.querySelector(".status-text");
  
  statusDot.style.backgroundColor = color;
  statusText.textContent = status;
  statusText.style.color = color;
}

function start() {
  const startBtn = document.getElementById("startBtn");
  startBtn.disabled = true;
  startBtn.innerHTML = '<span class="btn-text">Starting...</span><span class="btn-icon">⏳</span>';
  
  updateStatus("Starting...", "#00a8ff");
  
  log(`[${getTime()}] | Request sent to start proxy...`);
  
  fetch('/start')
    .then(res => res.json())
    .then(data => {
      log(`[${getTime()}] | ${data.status}`);
      updateStatus("Running", "#00ff9d");
      startBtn.innerHTML = '<span class="btn-text">Restart Star Hybrid</span><span class="btn-icon">🔄</span>';
      startBtn.disabled = false;
    })
    .catch(err => {
      log(`[${getTime()}] | Error: ${err.message}`);
      updateStatus("Error", "#ff3d3d");
      startBtn.innerHTML = '<span class="btn-text">Try Again</span><span class="btn-icon">❌</span>';
      startBtn.disabled = false;
    });
}

// Initialize logs
log(`[${getTime()}] | System initialized`);
updateStatus("Idle", "#555");

// Poll for logs every 2 seconds
setInterval(() => {
  fetch('/logs')
    .then(res => res.json())
    .then(logs => {
      const logBox = document.getElementById("logBox");
      // Only update if there are new logs
      if (logs.length > logBox.children.length) {
        logBox.innerHTML = '';
        logs.forEach(line => log(line));
      }
    })
    .catch(err => {
      log(`[${getTime()}] | Error fetching logs: ${err.message}`);
    });
}, 2000);