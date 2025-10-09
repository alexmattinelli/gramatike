# 🛡️ Melhoria na Moderação de Conteúdo - Gramátike

## 📋 Resumo

Implementada melhoria no sistema de moderação para exibir a palavra específica que causou o bloqueio de conteúdo.

---

## ❓ Problema Anterior

Quando um usuário tentava publicar conteúdo inadequado, recebia apenas uma mensagem genérica:

```
❌ "Não posso ajudar com discurso de ódio, xingamentos ou conteúdo sexual/nudez. 
   Vamos manter um espaço seguro e respeitoso."
```

**Problemas:**
- ❌ Usuário não sabia qual palavra foi bloqueada
- ❌ Dificuldade para entender e corrigir o conteúdo
- ❌ Frustração por não saber o motivo específico
- ❌ Possíveis palavras legítimas bloqueadas sem clareza

---

## ✅ Solução Implementada

Agora o sistema mostra exatamente qual palavra causou o bloqueio:

```
✅ "Seu conteúdo foi bloqueado porque contém a palavra 'porra' que não é permitida.
   Não posso ajudar com discurso de ódio, xingamentos ou conteúdo sexual/nudez. 
   Vamos manter um espaço seguro e respeitoso."
```

**Benefícios:**
- ✅ Transparência total sobre o bloqueio
- ✅ Usuário sabe exatamente o que corrigir
- ✅ Melhor experiência do usuário
- ✅ Redução de frustrações e dúvidas

---

## 🔄 Exemplos Práticos

### Exemplo 1: Palavrão

**Input:**
```
"Isso é uma porra de situação difícil"
```

**Output:**
```json
{
  "error": "conteudo_bloqueado",
  "reason": "profanity",
  "message": "Seu conteúdo foi bloqueado porque contém a palavra 'porra' que não é permitida. Não posso ajudar com discurso de ódio, xingamentos ou conteúdo sexual/nudez. Vamos manter um espaço seguro e respeitoso."
}
```

---

### Exemplo 2: Discurso de Ódio

**Input:**
```
"Que viado chato"
```

**Output:**
```json
{
  "error": "conteudo_bloqueado",
  "reason": "hate",
  "message": "Seu conteúdo foi bloqueado porque contém a palavra 'viado' que não é permitida. Não posso ajudar com discurso de ódio, xingamentos ou conteúdo sexual/nudez. Vamos manter um espaço seguro e respeitoso."
}
```

---

### Exemplo 3: Conteúdo Sexual

**Input:**
```
"Vendo pack de nudes"
```

**Output:**
```json
{
  "error": "conteudo_bloqueado",
  "reason": "nudity",
  "message": "Seu conteúdo foi bloqueado porque contém a palavra 'nudes' que não é permitida. Não posso ajudar com discurso de ódio, xingamentos ou conteúdo sexual/nudez. Vamos manter um espaço seguro e respeitoso."
}
```

---

### Exemplo 4: Conteúdo Permitido

**Input:**
```
"Adorei o artigo sobre concordância verbal!"
```

**Output:**
```json
{
  "success": true
}
```

---

## 🔧 Implementação Técnica

### Função Atualizada: `refusal_message_pt()`

**Localização:** `gramatike_app/utils/moderation.py`

**Antes:**
```python
def refusal_message_pt(category: str) -> str:
    return "Não posso ajudar com discurso de ódio, xingamentos ou conteúdo sexual/nudez. Vamos manter um espaço seguro e respeitoso."
```

**Depois:**
```python
def refusal_message_pt(category: str, matched_word: str = None) -> str:
    """Retorna mensagem de moderação com palavra bloqueada se disponível."""
    base_msg = "Não posso ajudar com discurso de ódio, xingamentos ou conteúdo sexual/nudez. Vamos manter um espaço seguro e respeitoso."
    if matched_word:
        return f"Seu conteúdo foi bloqueado porque contém a palavra '{matched_word}' que não é permitida. {base_msg}"
    return base_msg
```

---

## 📍 Endpoints Atualizados

### 1. Criar Post (`/api/posts`)

**Arquivo:** `gramatike_app/routes/__init__.py`

**Antes:**
```python
ok, cat, _m = check_text(data.get('conteudo') or '')
if not ok:
    return jsonify({'error': 'conteudo_bloqueado', 'reason': cat, 'message': refusal_message_pt(cat)}), 400
```

**Depois:**
```python
ok, cat, matched_word = check_text(data.get('conteudo') or '')
if not ok:
    return jsonify({'error': 'conteudo_bloqueado', 'reason': cat, 'message': refusal_message_pt(cat, matched_word)}), 400
```

---

### 2. Editar Perfil (`/api/editar-perfil`)

**Moderação de Bio:**

**Antes:**
```python
ok_b, cat_b, _ = check_text(bio)
if not ok_b:
    return jsonify({'erro': refusal_message_pt(cat_b)}), 400
```

**Depois:**
```python
ok_b, cat_b, matched_b = check_text(bio)
if not ok_b:
    return jsonify({'erro': refusal_message_pt(cat_b, matched_b)}), 400
```

**Moderação de Username:**

**Antes:**
```python
ok_u, cat_u, _ = check_text(novo_username)
if not ok_u:
    return jsonify({'erro': refusal_message_pt(cat_u)}), 400
```

**Depois:**
```python
ok_u, cat_u, matched_u = check_text(novo_username)
if not ok_u:
    return jsonify({'erro': refusal_message_pt(cat_u, matched_u)}), 400
```

---

### 3. Criar Post com Múltiplas Imagens (`/api/posts_multi`)

**Antes:**
```python
ok, cat, _m = check_text(conteudo)
if not ok:
    return jsonify({'error': 'conteudo_bloqueado', 'reason': cat, 'message': refusal_message_pt(cat)}), 400
```

**Depois:**
```python
ok, cat, matched_word = check_text(conteudo)
if not ok:
    return jsonify({'error': 'conteudo_bloqueado', 'reason': cat, 'message': refusal_message_pt(cat, matched_word)}), 400
```

---

### 4. Criar Comentário

**Antes:**
```python
ok, cat, _m = check_text(conteudo or '')
if not ok:
    return jsonify({'error': 'conteudo_bloqueado', 'reason': cat, 'message': refusal_message_pt(cat)}), 400
```

**Depois:**
```python
ok, cat, matched_word = check_text(conteudo or '')
if not ok:
    return jsonify({'error': 'conteudo_bloqueado', 'reason': cat, 'message': refusal_message_pt(cat, matched_word)}), 400
```

---

## 📊 Categorias de Moderação

O sistema classifica conteúdo bloqueado em 3 categorias:

### 1. `profanity` (Palavrões)
- porra, caralho, merda
- pqp, vtnc, vsf, fdp
- arrombado, arrombada
- otário, otária

### 2. `hate` (Discurso de Ódio)
- viado, bicha, traveco
- sapatão
- preto imundo, macaco
- retardado, mongoloide

### 3. `nudity` (Conteúdo Sexual/Nudez)
- nude, nudes, nudez
- termos sexuais explícitos
- sites adultos (onlyfans, pornhub, etc.)
- pack do/da
- 18+, +18

---

## 🧪 Testes Realizados

### Script de Teste

```python
# Arquivo: /tmp/test_moderation.py

test_cases = [
    ("isso é uma porra", False, "profanity", "porra"),
    ("você é um caralho", False, "profanity", "caralho"),
    ("que merda", False, "profanity", "merda"),
    ("viado de merda", False, "hate", "viado"),
    ("texto normal sem palavrões", True, None, None),
    ("conteúdo com nudes", False, "nudity", "nudes"),
]
```

### Resultados

```
✅ Text: 'isso é uma porra'
   Expected: ok=False, cat=profanity, match=porra
   Got:      ok=False, cat=profanity, match=porra
   Message:  Seu conteúdo foi bloqueado porque contém a palavra 'porra' que não é permitida. [...]

✅ Text: 'você é um caralho'
   Expected: ok=False, cat=profanity, match=caralho
   Got:      ok=False, cat=profanity, match=caralho
   Message:  Seu conteúdo foi bloqueado porque contém a palavra 'caralho' que não é permitida. [...]

✅ Text: 'que merda'
   Expected: ok=False, cat=profanity, match=merda
   Got:      ok=False, cat=profanity, match=merda
   Message:  Seu conteúdo foi bloqueado porque contém a palavra 'merda' que não é permitida. [...]

✅ Text: 'viado de merda'
   Expected: ok=False, cat=hate, match=viado
   Got:      ok=False, cat=hate, match=viado
   Message:  Seu conteúdo foi bloqueado porque contém a palavra 'viado' que não é permitida. [...]

✅ Text: 'texto normal sem palavrões'
   Expected: ok=True, cat=None, match=None
   Got:      ok=True, cat=None, match=None

✅ Text: 'conteúdo com nudes'
   Expected: ok=False, cat=nudity, match=nudes
   Got:      ok=False, cat=nudity, match=nudes
   Message:  Seu conteúdo foi bloqueado porque contém a palavra 'nudes' que não é permitida. [...]
```

**Resultado: 100% dos testes passaram ✅**

---

## 🔒 Segurança e Privacidade

### Considerações Importantes

1. **Privacidade:** A palavra bloqueada é mostrada apenas ao autor do conteúdo
2. **Normalização:** Sistema remove acentos para detectar variações
3. **Prioridade:** Palavras customizadas do admin têm prioridade
4. **Word Boundaries:** Usa regex com `\b` para evitar falsos positivos

### Exemplo de Normalização

```python
# Input com acento
"Que pôrra é essa?"

# Normalizado (sem acento)
"que porra e essa?"

# Match detectado
✅ "porra" bloqueado
```

---

## 📈 Impacto Esperado

### Métricas de Sucesso

- ✅ **Transparência:** Usuários entendem exatamente o motivo do bloqueio
- ✅ **Correção:** Redução de tentativas frustradas de publicação
- ✅ **Educação:** Usuários aprendem termos inadequados
- ✅ **Suporte:** Menos tickets de suporte sobre bloqueios

### KPIs Sugeridos

- Redução de reports de "não sei por que foi bloqueado"
- Redução de tentativas repetidas de publicação
- Melhoria na satisfação do usuário (NPS)

---

## 🚀 Próximas Melhorias (Sugestões)

- [ ] Interface admin para gerenciar palavras bloqueadas
- [ ] Sistema de apelação para bloqueios
- [ ] Sugestões de palavras alternativas
- [ ] Analytics de palavras mais bloqueadas
- [ ] Sistema de educação sobre linguagem inclusiva

---

**Implementado em**: 2025  
**Status**: ✅ Ativo em Produção  
**Cobertura**: 100% dos endpoints com moderação
