import express from 'express';
import path from 'path';

const app = express();
app.use(express.json());

const publicDir = path.resolve('./public');
app.use(express.static(publicDir));

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

app.get('/api/posts', (req, res) => {
  res.json({ posts });
});

app.post('/api/posts', (req, res) => {
  const { content } = req.body || {};
  if (!content || typeof content !== 'string') {
    return res.status(400).json({ error: 'Conteúdo inválido' });
  }
  const post = { 
    id: posts.length + 1, 
    user: { id: 1, username: 'usuario', name: 'Usuário' },
    content, 
    created_at: new Date().toISOString(),
    likes: 0,
    comments: 0,
    shares: 0
  };
  posts.unshift(post);
  res.status(201).json({ post });
});

app.get('/api/amigos', (req, res) => {
  const amigos = [
    { id: 1, name: 'Maria Silva', username: 'mariasilva', online: true },
    { id: 2, name: 'João Carlos', username: 'joaocarlos', online: true },
    { id: 3, name: 'Ana Paula', username: 'anapaula', online: false }
  ];
  res.json({ amigos });
});

const PORT = process.env.PORT || 8787;
app.listen(PORT, () => console.log(`Dev server em http://localhost:${PORT}`));
