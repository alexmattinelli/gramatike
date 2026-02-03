const http = require('http');
const fs = require('fs');
const path = require('path');

// Create dates for testing timestamp formatting
const now = new Date();
const fiveMinAgo = new Date(now - 5 * 60 * 1000);
const twoHoursAgo = new Date(now - 2 * 60 * 60 * 1000);
const yesterday = new Date(now - 25 * 60 * 60 * 1000);
const threeDaysAgo = new Date(now - 3 * 24 * 60 * 60 * 1000);

let posts = [
  { 
    id: 1, 
    user: { id: 1, username: 'mariasilva', name: 'Maria Silva' },
    content: 'Acabei de aprender sobre concordância verbal! 📚', 
    created_at: fiveMinAgo.toISOString(),
    likes: 12,
    comments: 3,
    shares: 1
  },
  { 
    id: 2, 
    user: { id: 2, username: 'joaocarlos', name: 'João Carlos' },
    content: 'Alguém pode me ajudar com regência nominal? Estou com dúvidas...', 
    created_at: twoHoursAgo.toISOString(),
    likes: 5,
    comments: 8,
    shares: 0
  },
  { 
    id: 3, 
    user: { id: 3, username: 'anapaula', name: 'Ana Paula' },
    content: 'Compartilhando um exercício interessante de crase que encontrei!', 
    created_at: yesterday.toISOString(),
    likes: 24,
    comments: 6,
    shares: 5
  },
  { 
    id: 4, 
    user: { id: 4, username: 'pedroalves', name: 'Pedro Alves' },
    content: 'Gramática é vida! Vamos estudar juntos? 💪', 
    created_at: threeDaysAgo.toISOString(),
    likes: 8,
    comments: 2,
    shares: 2
  }
];

const amigos = [
  { id: 1, name: 'Maria Silva', username: 'mariasilva', online: true },
  { id: 2, name: 'João Carlos', username: 'joaocarlos', online: true },
  { id: 3, name: 'Ana Paula', username: 'anapaula', online: false }
];

const mimeTypes = {
  '.html': 'text/html',
  '.js': 'text/javascript',
  '.css': 'text/css',
  '.json': 'application/json',
  '.png': 'image/png',
  '.jpg': 'image/jpg',
  '.gif': 'image/gif',
  '.svg': 'image/svg+xml',
  '.ico': 'image/x-icon'
};

const server = http.createServer((req, res) => {
  // Handle API routes
  if (req.url === '/api/posts') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ posts }));
    return;
  }
  
  if (req.url === '/api/amigos') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ amigos }));
    return;
  }

  // Serve static files
  let filePath = './public' + req.url;
  if (filePath === './public/') {
    filePath = './public/index.html';
  }

  const extname = String(path.extname(filePath)).toLowerCase();
  const contentType = mimeTypes[extname] || 'application/octet-stream';

  fs.readFile(filePath, (error, content) => {
    if (error) {
      if (error.code === 'ENOENT') {
        res.writeHead(404);
        res.end('404 - File not found');
      } else {
        res.writeHead(500);
        res.end('500 - Internal server error');
      }
    } else {
      res.writeHead(200, { 'Content-Type': contentType });
      res.end(content, 'utf-8');
    }
  });
});

const PORT = 8787;
server.listen(PORT, () => {
  console.log(`Server running at http://localhost:${PORT}/`);
});
