const { app, BrowserWindow } = require('electron')
const { spawn } = require('child_process')
const path = require('path')

let flaskProcess
let mainWindow

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    icon: path.join(__dirname, 'starfn.ico'),
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true
    }
  })

  mainWindow.setMenu(null)

  mainWindow.loadURL('http://localhost:5000')
}

app.whenReady().then(() => {
  flaskProcess = spawn('python', ['../flask_app/app.py'])

  flaskProcess.stdout.on('data', (data) => {
    console.log(`Flask: ${data}`)
  })

  flaskProcess.stderr.on('data', (data) => {
    console.error(`Flask Error: ${data}`)
  })

  createWindow()
})

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    flaskProcess.kill() 
    app.quit()
  }
})