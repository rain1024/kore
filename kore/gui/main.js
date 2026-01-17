const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const fs = require('fs');
const { execSync } = require('child_process');

// Resources directory
const RESOURCES_DIR = path.join(__dirname, '..', 'resources');

// Get animation/mindmap and cwd from command line args
let animationArg = null;
let mindmapSvgPath = null;
let workingDir = process.cwd();

for (const arg of process.argv) {
  if (arg.match(/^\w+\.\w+$/) && !arg.includes('/')) {
    animationArg = arg;
  }
  if (arg.startsWith('--cwd=')) {
    workingDir = arg.slice(6);
  }
  if (arg.startsWith('--mindmap=')) {
    mindmapSvgPath = arg.slice(10);
  }
}

let mainWindow;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 500,
    height: 500,
    title: 'Kore',
    titleBarStyle: 'hiddenInset',
    backgroundColor: '#000000',
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false
    }
  });

  mainWindow.loadFile('public/index.html');
}

// IPC: Get requested animation name
ipcMain.handle('get-animation-name', () => {
  return animationArg || 'cat.go';
});

// IPC: Get mindmap SVG content
ipcMain.handle('get-mindmap-svg', () => {
  if (mindmapSvgPath && fs.existsSync(mindmapSvgPath)) {
    return fs.readFileSync(mindmapSvgPath, 'utf-8');
  }
  return null;
});

// IPC: Check if mindmap mode
ipcMain.handle('is-mindmap-mode', () => {
  return !!mindmapSvgPath;
});

// IPC: Get mindmap JSON data
ipcMain.handle('get-mindmap-data', () => {
  const jsonPath = path.join(require('os').tmpdir(), 'kore_mindmap.json');
  if (fs.existsSync(jsonPath)) {
    return JSON.parse(fs.readFileSync(jsonPath, 'utf-8'));
  }
  return null;
});

// IPC: Update mindmap and re-render SVG
ipcMain.handle('update-mindmap', (event, data) => {
  try {
    // Save updated JSON
    const jsonPath = path.join(require('os').tmpdir(), 'kore_mindmap.json');
    fs.writeFileSync(jsonPath, JSON.stringify(data));

    // Generate kore source from mindmap data
    function nodeToKore(node, indent = 0) {
      const prefix = '  '.repeat(indent);
      let result = prefix + node.text + '\n';
      for (const child of node.children || []) {
        result += nodeToKore(child, indent + 1);
      }
      return result;
    }

    const koreSource = 'mindmap ' + data.text + '\n' +
      (data.children || []).map(c => nodeToKore(c, 1)).join('');

    // Write temp .kore file
    const korePath = path.join(require('os').tmpdir(), 'kore_mindmap_temp.kore');
    fs.writeFileSync(korePath, koreSource + '\nsave ' + mindmapSvgPath);

    // Run kore to re-render
    execSync(`kore "${korePath}"`, { cwd: workingDir, encoding: 'utf-8' });

    // Return updated SVG
    return fs.readFileSync(mindmapSvgPath, 'utf-8');
  } catch (err) {
    console.error('Error updating mindmap:', err);
    return null;
  }
});

// IPC: Get animation data
ipcMain.handle('get-animation', (event, name) => {
  const filePath = path.join(RESOURCES_DIR, `${name.toLowerCase()}.json`);
  if (fs.existsSync(filePath)) {
    return JSON.parse(fs.readFileSync(filePath, 'utf-8'));
  }
  return null;
});

// IPC: Execute kore CLI command in original working directory
ipcMain.handle('kore-exec', (event, cmd) => {
  try {
    const result = execSync(`kore -e "${cmd}"`, {
      encoding: 'utf-8',
      cwd: workingDir
    });
    return { success: true, output: result };
  } catch (err) {
    return { success: false, output: err.message };
  }
});

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  app.quit();
});
