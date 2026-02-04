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
  { 
    id: 1, 
    username: 'mariasilva', 
    name: 'Maria Silva', 
    avatar_initials: 'MS',
    bio: 'Apaixonada por gramática e língua portuguesa! 📚',
    genero: 'Mulher (cis)',
    pronome: 'ela/dela',
    verified: true,
    online_status: true,
    created_at: new Date('2024-01-15').toISOString(),
    posts_count: 15,
    followers_count: 120,
    following_count: 85
  },
  { 
    id: 2, 
    username: 'joaocarlos', 
    name: 'João Carlos', 
    avatar_initials: 'JC',
    bio: 'Estudante de Letras - UFMG',
    genero: 'Homem (cis)',
    pronome: 'ele/dele',
    verified: false,
    online_status: true,
    created_at: new Date('2024-02-20').toISOString(),
    posts_count: 8,
    followers_count: 45,
    following_count: 60
  },
  { 
    id: 3, 
    username: 'anapaula', 
    name: 'Ana Paula', 
    avatar_initials: 'AP',
    bio: 'Professora de Português | Amo ensinar! ✨',
    genero: 'Mulher (cis)',
    pronome: 'ela/dela',
    verified: true,
    online_status: false,
    created_at: new Date('2023-11-10').toISOString(),
    posts_count: 42,
    followers_count: 320,
    following_count: 150
  },
  { 
    id: 4, 
    username: 'pedroalves', 
    name: 'Pedro Alves', 
    avatar_initials: 'PA',
    bio: '',
    genero: 'Prefiro não informar',
    pronome: 'Prefiro não informar',
    verified: false,
    online_status: true,
    created_at: new Date('2024-03-05').toISOString(),
    posts_count: 5,
    followers_count: 12,
    following_count: 25
  },
  { 
    id: 5, 
    username: 'carlaferreira', 
    name: 'Carla Ferreira', 
    avatar_initials: 'CF',
    bio: 'Revisora de textos freelancer',
    genero: 'Mulher (cis)',
    pronome: 'ela/dela',
    verified: false,
    online_status: true,
    created_at: new Date('2024-01-28').toISOString(),
    posts_count: 23,
    followers_count: 89,
    following_count: 102
  },
  { 
    id: 6, 
    username: 'lucassantos', 
    name: 'Lucas Santos', 
    avatar_initials: 'LS',
    bio: 'Concurseiro | Foco total! 💪',
    genero: 'Homem (cis)',
    pronome: 'ele/dele',
    verified: false,
    online_status: false,
    created_at: new Date('2023-12-12').toISOString(),
    posts_count: 19,
    followers_count: 67,
    following_count: 78
  }
];

// Current logged-in user (simulated)
const currentUser = mockUsers[0]; // Maria Silva

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

  // Handle GET /api/users/me - Get current user
  if (req.url === '/api/users/me' && req.method === 'GET') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      success: true,
      data: {
        user: {
          id: currentUser.id,
          username: currentUser.username,
          name: currentUser.name,
          bio: currentUser.bio,
          genero: currentUser.genero,
          pronome: currentUser.pronome,
          avatar_initials: currentUser.avatar_initials,
          verified: currentUser.verified,
          online_status: currentUser.online_status,
          created_at: currentUser.created_at,
          email: 'ma***@example.com' // Partially hidden
        }
      }
    }));
    return;
  }

  // Handle GET /api/users/:id - Get user profile
  const userIdMatch = req.url.match(/^\/api\/users\/(\d+)$/);
  if (userIdMatch && req.method === 'GET') {
    const userId = parseInt(userIdMatch[1]);
    const user = mockUsers.find(u => u.id === userId);
    
    if (user) {
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({
        success: true,
        user: {
          id: user.id,
          username: user.username,
          name: user.name,
          bio: user.bio,
          genero: user.genero,
          pronome: user.pronome,
          avatar_initials: user.avatar_initials,
          verified: user.verified,
          online_status: user.online_status,
          created_at: user.created_at,
          posts_count: user.posts_count,
          followers_count: user.followers_count,
          following_count: user.following_count,
          is_following: false,
          follows_you: false,
          is_mutual: false
        }
      }));
    } else {
      res.writeHead(404, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ success: false, error: 'Usuário não encontrado' }));
    }
    return;
  }

  // Handle PATCH /api/posts/:id - Like/unlike a post
  const postPatchMatch = req.url.match(/^\/api\/posts\/(\d+)$/);
  if (postPatchMatch && req.method === 'PATCH') {
    const postId = parseInt(postPatchMatch[1]);
    const post = posts.find(p => p.id === postId);
    
    if (post) {
      // Check if current user has already liked this post
      const likedByCurrentUser = post.liked_by && post.liked_by.some(u => u.id === currentUser.id);
      
      if (likedByCurrentUser) {
        // Unlike - remove the like
        post.liked_by = post.liked_by.filter(u => u.id !== currentUser.id);
        post.likes = Math.max(0, post.likes - 1);
        
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({
          success: true,
          message: 'Curtida removida',
          data: {
            likes: post.likes,
            liked: false,
            likedBy: post.liked_by.slice(0, 3)
          }
        }));
      } else {
        // Like - add the like
        if (!post.liked_by) {
          post.liked_by = [];
        }
        post.liked_by.unshift({
          id: currentUser.id,
          username: currentUser.username,
          name: currentUser.name,
          avatar_initials: currentUser.avatar_initials
        });
        post.likes += 1;
        
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({
          success: true,
          message: 'Post curtido',
          data: {
            likes: post.likes,
            liked: true,
            likedBy: post.liked_by.slice(0, 3)
          }
        }));
      }
    } else {
      res.writeHead(404, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ success: false, error: 'Post não encontrado' }));
    }
    return;
  }

  // Handle GET /api/users/:id/posts - Get user's posts
  const userPostsMatch = req.url.match(/^\/api\/users\/(\d+)\/posts/);
  if (userPostsMatch && req.method === 'GET') {
    const userId = parseInt(userPostsMatch[1]);
    const userPosts = posts.filter(p => p.user.id === userId);
    
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      success: true,
      posts: userPosts,
      pagination: {
        total: userPosts.length,
        page: 1,
        perPage: 30
      }
    }));
    return;
  }

  // Handle GET /api/users/:id/followers - Get user's followers
  const followersMatch = req.url.match(/^\/api\/users\/(\d+)\/followers$/);
  if (followersMatch && req.method === 'GET') {
    const userId = parseInt(followersMatch[1]);
    const user = mockUsers.find(u => u.id === userId);
    
    if (user) {
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({
        success: true,
        count: user.followers_count || 0,
        followers: []
      }));
    } else {
      res.writeHead(404, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ success: false, error: 'Usuário não encontrado' }));
    }
    return;
  }

  // Handle GET /api/users/:id/following - Get user's following
  const followingMatch = req.url.match(/^\/api\/users\/(\d+)\/following$/);
  if (followingMatch && req.method === 'GET') {
    const userId = parseInt(followingMatch[1]);
    const user = mockUsers.find(u => u.id === userId);
    
    if (user) {
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({
        success: true,
        count: user.following_count || 0,
        following: []
      }));
    } else {
      res.writeHead(404, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ success: false, error: 'Usuário não encontrado' }));
    }
    return;
  }

  // Serve static files
  // Remove query parameters from URL
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
