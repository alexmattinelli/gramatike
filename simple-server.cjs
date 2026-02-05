const http = require('http');
const fs = require('fs');
const path = require('path');

// Create dates for testing timestamp formatting
const now = new Date();
const fiveMinAgo = new Date(now - 5 * 60 * 1000);
const twoHoursAgo = new Date(now - 2 * 60 * 60 * 1000);
const yesterday = new Date(now - 25 * 60 * 60 * 1000);
const threeDaysAgo = new Date(now - 3 * 24 * 60 * 60 * 1000);

// Create mock users for likes
const mockUsers = [
  { id: 1, username: 'mariasilva', name: 'Maria Silva', avatar_initials: 'MS' },
  { id: 2, username: 'joaocarlos', name: 'João Carlos', avatar_initials: 'JC' },
  { id: 3, username: 'anapaula', name: 'Ana Paula', avatar_initials: 'AP' },
  { id: 4, username: 'pedroalves', name: 'Pedro Alves', avatar_initials: 'PA' },
  { id: 5, username: 'carlaferreira', name: 'Carla Ferreira', avatar_initials: 'CF' },
  { id: 6, username: 'lucassantos', name: 'Lucas Santos', avatar_initials: 'LS' }
];

let posts = [
  { 
    id: 1, 
    user: { id: 1, username: 'mariasilva', name: 'Maria Silva' },
    content: 'Acabei de aprender sobre concordância verbal! 📚', 
    created_at: fiveMinAgo.toISOString(),
    likes: 12,
    comments: 3,
    shares: 1,
    liked_by: [
      { id: 2, username: 'joaocarlos', name: 'João Carlos', avatar_initials: 'JC' },
      { id: 3, username: 'anapaula', name: 'Ana Paula', avatar_initials: 'AP' },
      { id: 4, username: 'pedroalves', name: 'Pedro Alves', avatar_initials: 'PA' }
    ]
  },
  { 
    id: 2, 
    user: { id: 2, username: 'joaocarlos', name: 'João Carlos' },
    content: 'Alguém pode me ajudar com regência nominal? Estou com dúvidas...', 
    created_at: twoHoursAgo.toISOString(),
    likes: 5,
    comments: 8,
    shares: 0,
    liked_by: [
      { id: 1, username: 'mariasilva', name: 'Maria Silva', avatar_initials: 'MS' },
      { id: 5, username: 'carlaferreira', name: 'Carla Ferreira', avatar_initials: 'CF' }
    ]
  },
  { 
    id: 3, 
    user: { id: 3, username: 'anapaula', name: 'Ana Paula' },
    content: 'Compartilhando um exercício interessante de crase que encontrei!', 
    created_at: yesterday.toISOString(),
    likes: 24,
    comments: 6,
    shares: 5,
    liked_by: [
      { id: 6, username: 'lucassantos', name: 'Lucas Santos', avatar_initials: 'LS' },
      { id: 1, username: 'mariasilva', name: 'Maria Silva', avatar_initials: 'MS' },
      { id: 2, username: 'joaocarlos', name: 'João Carlos', avatar_initials: 'JC' }
    ]
  },
  { 
    id: 4, 
    user: { id: 4, username: 'pedroalves', name: 'Pedro Alves' },
    content: 'Gramática é vida! Vamos estudar juntos? 💪', 
    created_at: threeDaysAgo.toISOString(),
    likes: 1,
    comments: 2,
    shares: 2,
    liked_by: [
      { id: 3, username: 'anapaula', name: 'Ana Paula', avatar_initials: 'AP' }
    ]
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
  
  // Handle /api/posts/:id/likes
  const likesMatch = req.url.match(/^\/api\/posts\/(\d+)\/likes$/);
  if (likesMatch) {
    const postId = parseInt(likesMatch[1]);
    const post = posts.find(p => p.id === postId);
    
    if (post) {
      // Generate more mock users for the full list
      const allLikes = [];
      const likeCount = post.likes || 0;
      
      // Add the liked_by users first
      if (post.liked_by) {
        allLikes.push(...post.liked_by);
      }
      
      // Add more mock users to match the like count
      for (let i = allLikes.length; i < likeCount; i++) {
        const userIndex = i % mockUsers.length;
        allLikes.push({
          ...mockUsers[userIndex],
          id: 100 + i // Ensure unique IDs
        });
      }
      
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({
        success: true,
        data: {
          likes: allLikes,
          total: allLikes.length
        }
      }));
    } else {
      res.writeHead(404, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ success: false, error: 'Post não encontrado' }));
    }
    return;
  }
  
  if (req.url === '/api/amigos') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ amigos }));
    return;
  }

  // Handle /api/users/me
  if (req.url === '/api/users/me') {
    const currentUser = {
      id: 1,
      username: 'mariasilva',
      email: 'ma***@email.com',
      name: 'Maria Silva',
      bio: 'Estudante de Letras apaixonada por gramática!',
      genero: 'Mulher (cis)',
      pronome: 'ela/dela',
      avatar_initials: 'MS',
      verified: true,
      online_status: true,
      role: 'user',
      created_at: '2024-01-15T10:00:00Z',
      is_banned: false
    };
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ success: true, data: { user: currentUser } }));
    return;
  }

  // Handle /api/users/:id
  const userMatch = req.url.match(/^\/api\/users\/(\d+)$/);
  if (userMatch) {
    const userId = parseInt(userMatch[1]);
    const user = mockUsers.find(u => u.id === userId);
    
    if (user) {
      const userProfile = {
        ...user,
        bio: `Bio de ${user.name}`,
        genero: 'Prefiro não informar',
        pronome: 'Prefiro não informar',
        verified: userId === 1,
        online_status: userId <= 3,
        created_at: '2024-01-15T10:00:00Z',
        posts_count: posts.filter(p => p.user.id === userId).length,
        followers_count: 42,
        following_count: 38,
        is_following: false,
        follows_you: false,
        is_mutual: false
      };
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ success: true, user: userProfile }));
    } else {
      res.writeHead(404, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: 'Usuário não encontrado' }));
    }
    return;
  }

  // Handle /api/users/:id/posts
  const userPostsMatch = req.url.match(/^\/api\/users\/(\d+)\/posts$/);
  if (userPostsMatch) {
    const userId = parseInt(userPostsMatch[1]);
    const userPosts = posts.filter(p => p.user.id === userId);
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ success: true, data: { posts: userPosts, total: userPosts.length } }));
    return;
  }

  // Serve static files
  // Strip query string from URL
  const urlPath = req.url.split('?')[0];
  let filePath = './public' + urlPath;
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
