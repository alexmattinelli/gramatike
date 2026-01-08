# 🔐 Credenciais Padrão do Admin

## ⚠️ ATENÇÃO - LEIA ISTO PRIMEIRO! ⚠️

> **IMPORTANTE**: As credenciais abaixo são **temporárias** e devem ser alteradas **IMEDIATAMENTE** após o primeiro login!
> 
> **NÃO USE ESTAS CREDENCIAIS EM PRODUÇÃO** sem alterá-las primeiro.

---

## Usuário Admin Padrão

Após aplicar o schema D1, um usuário admin é criado automaticamente:

**Usuário:** `gramatike`  
**Email:** `contato@gramatike.com`  
**Senha:** `GramatikeAdmin2026!`

## ⚠️ IMPORTANTE - Segurança

1. **Trocar a senha imediatamente** após o primeiro login
2. **Não usar estas credenciais em produção** sem alterar
3. A senha está usando PBKDF2 com 100.000 iterações e SHA-256

## Como Trocar a Senha

### Opção 1: Via Interface (Recomendado)
1. Faça login com as credenciais padrão
2. Vá em **Configurações** → **Alterar Senha**
3. Defina uma senha forte (mínimo 8 caracteres)

### Opção 2: Via SQL (D1)

Se você esquecer a senha, pode resetá-la via Wrangler:

```bash
# Gere um hash para a nova senha
node -e "
const crypto = require('crypto');
async function hashPassword(password) {
  const encoder = new TextEncoder();
  const data = encoder.encode(password);
  const salt = crypto.getRandomValues(new Uint8Array(16));
  const keyMaterial = await crypto.subtle.importKey('raw', data, { name: 'PBKDF2' }, false, ['deriveBits']);
  const derivedBits = await crypto.subtle.deriveBits({ name: 'PBKDF2', salt: salt, iterations: 100000, hash: 'SHA-256' }, keyMaterial, 256);
  const hashArray = new Uint8Array(derivedBits);
  const combined = new Uint8Array(salt.length + hashArray.length);
  combined.set(salt);
  combined.set(hashArray, salt.length);
  return btoa(String.fromCharCode(...combined));
}
hashPassword('SuaNovaSenha123!').then(hash => console.log('Hash:', hash));
"

# Atualize no D1
wrangler d1 execute gramatike --remote --command="UPDATE user SET password = 'SEU-HASH-AQUI' WHERE username = 'gramatike';"
```

## Criação de Novos Admins

Para promover um usuário existente a admin:

```bash
wrangler d1 execute gramatike --remote --command="UPDATE user SET is_admin = 1, is_superadmin = 1 WHERE username = 'nome-do-usuario';"
```

## Tipos de Permissões

- **`is_admin = 1`**: Acesso ao painel administrativo, moderação de conteúdo
- **`is_superadmin = 1`**: Acesso total, incluindo gerenciamento de usuários e configurações

## Dicas de Segurança

1. Use senhas fortes (mínimo 12 caracteres, mix de letras, números e símbolos)
2. Não compartilhe credenciais de admin
3. Revise regularmente os usuários com permissões de admin
4. Use autenticação de dois fatores quando disponível
5. Mantenha backups regulares do banco D1

## Recuperação de Acesso

Se você perder o acesso admin:

1. Use Wrangler para conectar ao D1 diretamente
2. Redefina a senha usando o método SQL acima
3. Ou crie um novo usuário admin temporário
4. Ou reaplique o schema (⚠️ isso apagará todos os dados!)
