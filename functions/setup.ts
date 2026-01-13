// functions/setup.ts
export const onRequestGet = async ({ env }) => {
  try {
    // 1. Verificar se a tabela users existe
    const tables = await env.DB.prepare(
      "SELECT name FROM sqlite_master WHERE type='table' AND name='users'"
    ).first();
    
    if (!tables) {
      // Tabela não existe, criar do zero
      await env.DB.batch([
        // Tabela users COMPLETA
        env.DB.prepare(`
          CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE,
            name TEXT,
            avatar_initials TEXT DEFAULT 'U',
            password_hash TEXT,
            verified BOOLEAN DEFAULT FALSE,
            online_status BOOLEAN DEFAULT TRUE,
            role TEXT DEFAULT 'user',
            banned BOOLEAN DEFAULT FALSE,
            banned_at DATETIME,
            banned_by INTEGER,
            last_active DATETIME,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
          )
        `),
        
        // Tabela posts
        env.DB.prepare(`
          CREATE TABLE posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            likes INTEGER DEFAULT 0,
            comments INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME,
            FOREIGN KEY (user_id) REFERENCES users(id)
          )
        `),
        
        // Tabela sessions
        env.DB.prepare(`
          CREATE TABLE sessions (
            id TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            expires_at DATETIME NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
          )
        `)
      ]);
      
      // Inserir admin padrão
      await env.DB.prepare(`
        INSERT INTO users (username, email, name, avatar_initials, password_hash, verified, role) 
        VALUES ('admin', 'admin@gramatike.com', 'Administrador', 'A', 'admin123', true, 'admin')
      `).run();
      
      // Posts de exemplo
      await env.DB.batch([
        env.DB.prepare(`
          INSERT INTO posts (user_id, content, likes, comments) 
          VALUES (1, 'Bem-vindo ao Gramátike! 🎉 Esta é a nova rede social para amantes da língua portuguesa.', 15, 3)
        `),
        env.DB.prepare(`
          INSERT INTO posts (user_id, content, likes, comments) 
          VALUES (1, 'Dica de hoje: Nunca use ''mesmo'' como pronome. Diga ''ele mesmo'' e não ''para o mesmo''. #gramática', 42, 7)
        `)
      ]);
      
      return new Response(`
        <h1>✅ Banco criado do zero!</h1>
        <p>Todas as tabelas foram criadas.</p>
        <p>Usuário admin criado:</p>
        <ul>
          <li>Email: admin@gramatike.com</li>
          <li>Senha: admin123</li>
        </ul>
        <p><a href="/feed">Ir para o feed</a></p>
      `, {
        headers: { 'Content-Type': 'text/html' }
      });
    }
    
    // 2. Tabela já existe, verificar colunas faltantes
    let output = '<h1>✅ Verificando estrutura...</h1><ul>';
    
    // Verificar colunas da tabela users
    const columns = await env.DB.prepare("PRAGMA table_info(users)").all();
    const columnNames = columns.results.map((col: any) => col.name);
    
    // Adicionar colunas que faltam (manualmente)
    const missingColumns = [];
    
    if (!columnNames.includes('password_hash')) {
      try {
        await env.DB.prepare('ALTER TABLE users ADD COLUMN password_hash TEXT').run();
        missingColumns.push('password_hash');
        output += '<li>✅ Coluna password_hash adicionada</li>';
      } catch (e) {
        output += `<li>❌ Erro ao adicionar password_hash: ${e.message}</li>`;
      }
    } else {
      output += '<li>✅ Coluna password_hash já existe</li>';
    }
    
    if (!columnNames.includes('banned')) {
      try {
        await env.DB.prepare('ALTER TABLE users ADD COLUMN banned BOOLEAN DEFAULT FALSE').run();
        missingColumns.push('banned');
        output += '<li>✅ Coluna banned adicionada</li>';
      } catch (e) {
        output += `<li>❌ Erro ao adicionar banned: ${e.message}</li>`;
      }
    }
    
    if (!columnNames.includes('last_active')) {
      try {
        await env.DB.prepare('ALTER TABLE users ADD COLUMN last_active DATETIME').run();
        missingColumns.push('last_active');
        output += '<li>✅ Coluna last_active adicionada</li>';
      } catch (e) {
        output += `<li>❌ Erro ao adicionar last_active: ${e.message}</li>`;
      }
    }
    
    // Verificar tabela sessions
    const sessionsTable = await env.DB.prepare(
      "SELECT name FROM sqlite_master WHERE type='table' AND name='sessions'"
    ).first();
    
    if (!sessionsTable) {
      await env.DB.prepare(`
        CREATE TABLE sessions (
          id TEXT PRIMARY KEY,
          user_id INTEGER NOT NULL,
          expires_at DATETIME NOT NULL,
          created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
      `).run();
      output += '<li>✅ Tabela sessions criada</li>';
    } else {
      output += '<li>✅ Tabela sessions já existe</li>';
    }
    
    output += '</ul>';
    
    if (missingColumns.length > 0) {
      output += `<p><strong>${missingColumns.length} colunas adicionadas!</strong></p>`;
    } else {
      output += '<p>Todas as colunas já existem.</p>';
    }
    
    output += `
      <p>Agora você pode:</p>
      <ol>
        <li><a href="/api/auth/register">Registrar novo usuário</a></li>
        <li><a href="/api/auth/login">Fazer login</a></li>
        <li><a href="/feed">Ver o feed</a></li>
      </ol>
      <p>Depois, delete este arquivo <code>functions/setup.ts</code>.</p>
    `;
    
    return new Response(output, {
      headers: { 'Content-Type': 'text/html' }
    });
    
  } catch (error: any) {
    return new Response(`
      <h1>❌ Erro no setup</h1>
      <pre>${error.message}</pre>
      <p>Stack: ${error.stack || 'N/A'}</p>
    `, {
      status: 500,
      headers: { 'Content-Type': 'text/html' }
    });
  }
};
