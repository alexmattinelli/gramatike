// functions/setup.ts
export const onRequestGet = async ({ env }) => {
  try {
    // 1. Adicionar coluna password_hash se não existir
    await env.DB.prepare(`
      ALTER TABLE users 
      ADD COLUMN IF NOT EXISTS password_hash TEXT
    `).run();
    
    // 2. Adicionar outras colunas que possam faltar
    await env.DB.batch([
      env.DB.prepare(`
        ALTER TABLE users 
        ADD COLUMN IF NOT EXISTS banned BOOLEAN DEFAULT FALSE
      `),
      env.DB.prepare(`
        ALTER TABLE users 
        ADD COLUMN IF NOT EXISTS last_active DATETIME
      `)
    ]);
    
    // 3. Criar tabela de sessões se não existir
    await env.DB.prepare(`
      CREATE TABLE IF NOT EXISTS sessions (
        id TEXT PRIMARY KEY,
        user_id INTEGER NOT NULL,
        expires_at DATETIME NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
      )
    `).run();
    
    return new Response(`
      <h1>✅ Banco atualizado!</h1>
      <p>Coluna <code>password_hash</code> adicionada à tabela users.</p>
      <p>Agora você pode:</p>
      <ol>
        <li><a href="/api/auth/register">Registrar novo usuário</a></li>
        <li><a href="/api/auth/login">Fazer login</a></li>
        <li><a href="/feed">Ver o feed</a></li>
      </ol>
      <p>Depois, delete este arquivo <code>functions/setup.ts</code>.</p>
    `, {
      headers: { 'Content-Type': 'text/html' }
    });
    
  } catch (error: any) {
    return new Response(`
      <h1>❌ Erro</h1>
      <pre>${error.message}</pre>
      <p>Talvez a tabela users não exista ainda.</p>
    `, {
      status: 500,
      headers: { 'Content-Type': 'text/html' }
    });
  }
};
