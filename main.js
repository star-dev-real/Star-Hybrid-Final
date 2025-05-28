const { app, BrowserWindow } = require('electron');
const { spawn } = require('child_process');
const path = require('path');

let flaskProcess;
let mainWindow;

async function checkServer() {
  const maxAttempts = 30;
  const delay = 1000;
  
  for (let i = 0; i < maxAttempts; i++) {
    try {
      const response = await fetch('http://localhost:5000');
      if (response.ok) return true;
    } catch (err) {
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }
  throw new Error('Server did not start in time');
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      sandbox: true,
      webSecurity: true
    },
    show: false 
  });

  const loadApp = async () => {
    try {
      if (typeof require('wait-on') === 'function') {
        await require('wait-on')({ resources: ['http://localhost:5000'] });
      } else {
        await checkServer();
      }
      await mainWindow.loadURL('http://localhost:5000');
      mainWindow.show();
    } catch (err) {
      console.error('Failed to load app:', err);
      mainWindow.loadFile('error.html'); 
    }
  };

  loadApp();

  mainWindow.on('closed', () => {
    mainWindow = null;
  });

}

app.on('ready', () => {
  try {
    flaskProcess = spawn('python', ['app.py'], {
      cwd: __dirname,
      stdio: 'inherit',
      shell: true 
    });

    flaskProcess.on('error', (err) => {
      console.error('Failed to start Flask:', err);
      app.quit();
    });

    createWindow();
  } catch (err) {
    console.error('App initialization failed:', err);
    app.quit();
  }
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    if (flaskProcess) {
      flaskProcess.kill();
    }
    app.quit();
  }
});

app.on('activate', () => {
  if (mainWindow === null) {
    createWindow();
  }
});

process.on('uncaughtException', (err) => {
  console.error('Uncaught Exception:', err);
  if (flaskProcess) flaskProcess.kill();
  app.quit();
});