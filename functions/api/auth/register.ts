// functions/api/auth/register.ts - VERSÃO AUTO-ADAPTATIVA
import type { PagesFunction } from '@cloudflare/workers-types';
import type { Env, User } from '../../types';

export const onRequestPost: PagesFunction<Env> = async ({ request, env }) => {
  try {
    const { username, email, password, name } = await request.json();
    
    if (!username || !email || !password) {
      return Response.json({
        success: false,
        error: 'Usuário, email e senha são obrigatórios'
      }, { status: 400 });
    }
    
    // 1. Verificar colunas da tabela users
    const columns = await env.DB.prepare(
      "PRAGMA table_info(users)"
    ).all();
    
    const columnNames = columns.results.map(c => c.name);
    console.log('Colunas disponíveis:', columnNames);
    
    // 2. Construir query dinamicamente baseado nas colunas existentes
    let insertColumns = [];
    let insertValues = [];
    let bindings = [];
    
    // Campos obrigatórios (devem existir)
    if (columnNames.includes('username')) {
      insertColumns.push('username');
      insertValues.push('?');
      bindings.push(username.trim());
    }
    
    if (columnNames.includes('email')) {
      insertColumns.push('email');
      insertValues.push('?');
      bindings.push(email.toLowerCase().trim());
    }
    
    if (columnNames.includes('password_hash')) {
      insertColumns.push('password_hash');
      insertValues.push('?');
      bindings.push(password); // ⚠️ Em produção, hash isso!
    }
    
    // Campos opcionais
    if (columnNames.includes('name')) {
      insertColumns.push('name');
      insertValues.push('?');
      bindings.push((name || username).trim());
    }
    
    if (columnNames.includes('avatar_initials')) {
      insertColumns.push('avatar_initials');
      insertValues.push('?');
      bindings.push(username.trim().charAt(0).toUpperCase());
    }
    
    if (columnNames.includes('verified')) {
      insertColumns.push('verified');
      insertValues.push('?');
      bindings.push(false);
    }
    
    if (columnNames.includes('online_status')) {
      insertColumns.push('online_status');
      insertValues.push('?');
      bindings.push(true);
    }
    
    if (columnNames.includes('role')) {
      insertColumns.push('role');
      insertValues.push('?');
      bindings.push('user');
    }
    
    // 3. Verificar se tem colunas suficientes
    if (insertColumns.length < 3) {
      return Response.json({
        success: false,
        error: `Estrutura insuficiente. Colunas encontradas: ${columnNames.join(', ')}`,
        availableColumns: columnNames
      }, { status: 500 });
    }
    
    // 4. Executar insert
    const query = `
      INSERT INTO users (${insertColumns.join(', ')})
      VALUES (${insertValues.join(', ')})
    `;
    
    console.log('Query:', query);
    console.log('Bindings:', bindings);
    
    const result = await env.DB.prepare(query).bind(...bindings).run();
    
    if (!result.success) {
      throw new Error('Insert failed');
    }
    
    // 5. Retornar sucesso
    return Response.json({
      success: true,
      message: 'Usuário criado com sucesso!',
      columnsUsed: insertColumns,
      userId: result.meta.last_row_id
    }, { status: 201 });
    
  } catch (error: any) {
    console.error('Register adaptive error:', error);
    
    // Diagnosticar erro
    let diagnostic = {
      message: error.message,
      suggestion: ''
    };
    
    if (error.message.includes('no such table')) {
      diagnostic.suggestion = 'Tabela users não existe. Crie com: CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, email TEXT, password_hash TEXT)';
    } else if (error.message.includes('has no column')) {
      diagnostic.suggestion = 'Falta coluna na tabela. Execute /inspect para ver estrutura atual.';
    } else if (error.message.includes('UNIQUE constraint failed')) {
      diagnostic.suggestion = 'Usuário ou email já existe.';
    }
    
    return Response.json({
      success: false,
      error: diagnostic.message,
      suggestion: diagnostic.suggestion,
      fullError: process.env.NODE_ENV === 'development' ? error.stack : undefined
    }, { status: 500 });
  }
};
