// functions/setup.ts
export const onRequestGet = async ({ env }) => {
  try {
    // 1. Adicionar colunas faltantes na tabela users
    await env.DB.batch([
      // Adicionar password_hash se não existir
      env.DB.prepare(`
        ALTER TABLE users 
        ADD COLUMN IF NOT EXISTS password_hash TEXT
      `),
      
      // Adicionar banned se não existir
      env.DB.prepare(`
        ALTER TABLE users 
        ADD COLUMN IF NOT EXISTS banned BOOLEAN DEFAULT FALSE
      `),
      
      // Adicionar last_active se não existir
      env.DB.prepare(`
        ALTER TABLE users 
        ADD COLUMN IF NOT EXISTS last_active DATETIME
      `),
      
      // Adicionar banned_at se não existir
      env.DB.prepare(`
        ALTER TABLE users 
        ADD COLUMN IF NOT EXISTS banned_at DATETIME
      `),
      
      // Adicionar banned_by se não existir
      env.DB.prepare(`
        ALTER TABLE users 
        ADD COLUMN IF NOT EXISTS banned_by INTEGER
      `)
    ]);
    
    // 2. Criar tabela de sessões se não existir
    await env.DB.prepare(`
      CREATE TABLE IF NOT EXISTS sessions (
        id TEXT PRIMARY KEY,
        user_id INTEGER NOT NULL,
        expires_at DATETIME NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
      )
    `).run();
    
    // 3. Inserir usuário admin padrão se não existir
    await env.DB.prepare(`
      INSERT OR IGNORE INTO users (username, email, password_hash, name, avatar_initials, verified, role) 
      VALUES ('admin', 'admin@gramatike.com', 'admin123', 'Administrador', 'A', true, 'admin')
    `).run();
    
    // 4. Criar alguns posts de exemplo
    await env.DB.prepare(`
      INSERT OR IGNORE INTO posts (user_id, content, likes, comments) 
      VALUES (1, 'Bem-vindo ao Gramátike! 🎉 Esta é a nova rede social para amantes da língua portuguesa.', 15, 3)
    `).run();
    
    await env.DB.prepare(`
      INSERT OR IGNORE INTO posts (user_id, content, likes, comments) 
      VALUES (1, 'Dica de hoje: Nunca use ''mesmo'' como pronome. Diga ''ele mesmo'' e não ''para o mesmo''. #gramática', 42, 7)
    `).run();
    
    return new Response(`
      <h1>✅ Banco de dados configurado com sucesso!</h1>
      <p>As tabelas foram atualizadas e dados de exemplo inseridos.</p>
      <p>Usuário admin criado:</p>
      <ul>
        <li>Email: admin@gramatike.com</li>
        <li>Senha: admin123</li>
      </ul>
      <p><a href="/feed">Ir para o feed</a></p>
    `, {
      headers: { 'Content-Type': 'text/html' }
    });
    
  } catch (error) {
    console.error('Setup error:', error);
    return new Response(`
      <h1>❌ Erro no setup</h1>
      <pre>${error.message}</pre>
      <p>Verifique se as tabelas base existem.</p>
    `, {
      status: 500,
      headers: { 'Content-Type': 'text/html' }
    });
  }
};
