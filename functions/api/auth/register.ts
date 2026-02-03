// functions/api/auth/register.ts - VERSÃO AUTO-ADAPTATIVA
import type { PagesFunction } from '@cloudflare/workers-types';
import type { Env, User } from '../../types';
import { hashPassword } from '../../../src/lib/crypto';

export const onRequestPost: PagesFunction<Env> = async ({ request, env }) => {
  try {
    const { username, email, password, name } = await request.json();
    
    console.log('[register] Iniciando registro para:', username, email);
    
    if (!username || !email || !password) {
      return Response.json({
        success: false,
        error: 'Usuário, email e senha são obrigatórios'
      }, { status: 400 });
    }
    
    // Validação de email
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      return Response.json({
        success: false,
        error: 'Email inválido'
      }, { status: 400 });
    }
    
    // Validação de username (3-20 caracteres alfanuméricos)
    const usernameRegex = /^[a-zA-Z0-9_]{3,20}$/;
    if (!usernameRegex.test(username)) {
      return Response.json({
        success: false,
        error: 'Usuário deve ter entre 3 e 20 caracteres (apenas letras, números e _)'
      }, { status: 400 });
    }
    
    // Validação de senha (mínimo 6 caracteres)
    if (password.length < 6) {
      return Response.json({
        success: false,
        error: 'Senha deve ter no mínimo 6 caracteres'
      }, { status: 400 });
    }
    
    // 1. Verificar colunas da tabela users
    const columns = await env.DB.prepare(
      "PRAGMA table_info(users)"
    ).all();
    
    const columnNames = columns.results.map(c => c.name);
    console.log('[register] Colunas disponíveis no banco:', columnNames);
    
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
      // Hash password using PBKDF2 (Web Crypto API)
      const hashedPassword = await hashPassword(password);
      bindings.push(hashedPassword);
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
      bindings.push(0);
    }
    
    if (columnNames.includes('online_status')) {
      insertColumns.push('online_status');
      insertValues.push('?');
      bindings.push(1);
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
    
    console.log('[register] Query SQL:', query);
    console.log('[register] Colunas a inserir:', insertColumns);
    
    const result = await env.DB.prepare(query).bind(...bindings).run();
    
    if (!result.success) {
      throw new Error('Insert failed');
    }
    
    console.log('[register] ✅ Usuário criado com sucesso! ID:', result.meta.last_row_id);
    
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
    } else if (error.message.includes('UNIQUE constraint failed: users.email')) {
      return Response.json({
        success: false,
        error: 'Este email já está cadastrado'
      }, { status: 409 });
    } else if (error.message.includes('UNIQUE constraint failed: users.username')) {
      return Response.json({
        success: false,
        error: 'Este nome de usuário já está em uso'
      }, { status: 409 });
    } else if (error.message.includes('UNIQUE constraint failed')) {
      return Response.json({
        success: false,
        error: 'Usuário ou email já existe'
      }, { status: 409 });
    }
    
    return Response.json({
      success: false,
      error: diagnostic.message,
      suggestion: diagnostic.suggestion,
      fullError: process.env.NODE_ENV === 'development' ? error.stack : undefined
    }, { status: 500 });
  }
};
