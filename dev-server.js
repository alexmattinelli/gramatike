import express from 'express';
import path from 'path';

const app = express();
app.use(express.json());

const publicDir = path.resolve('./public');
app.use(express.static(publicDir));

let posts = [
  { id: 1, user_id: 1, username: 'admin', name: 'Admin', content: 'Post de teste', created_at: new Date().toISOString() }
];

app.get('/api/posts', (req, res) => {
  res.json({ posts });
});

app.post('/api/posts', (req, res) => {
  const { content } = req.body || {};
  if (!content || typeof content !== 'string') {
    return res.status(400).json({ error: 'Conteúdo inválido' });
  }
  const post = { id: posts.length + 1, user_id: 1, username: 'admin', name: 'Admin', content, created_at: new Date().toISOString() };
  posts.unshift(post);
  res.status(201).json({ post });
});

const PORT = process.env.PORT || 8787;
app.listen(PORT, () => console.log(`Dev server em http://localhost:${PORT}`));
