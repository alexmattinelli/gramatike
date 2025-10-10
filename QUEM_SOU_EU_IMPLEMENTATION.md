# Implementação Completa: Dinâmica "Quem sou eu?"

## 📋 Visão Geral

Nova opção de dinâmica interativa onde o administrador pode criar um jogo de descoberta. Os participantes veem uma série de frases ou fotos e devem responder sobre características específicas (gênero, orientação sexual, pronome, etc.). Ao final, é exibida uma moral/mensagem educativa.

## ✅ Funcionalidades Implementadas

### 1. Criação da Dinâmica (Admin)

#### Interface de Criação
- **Novo tipo no dropdown**: "Quem sou eu?"
- **Campos de configuração**:
  - `questao_tipo`: O que a pessoa deve descobrir (ex: "gênero", "orientação sexual", "pronome")
  - `moral`: Mensagem final/moral da história
  - Lista de itens (frases ou fotos)

#### Adição de Itens
Cada item possui:
- **Tipo**: Frase ou Foto
- **Conteúdo**: 
  - Se frase: texto livre
  - Se foto: URL da imagem
- Botão de remoção

#### Validações Backend
- Mínimo 1 item obrigatório
- Campo `questao_tipo` obrigatório
- Campo `moral` obrigatório
- Todos os itens devem ter conteúdo

### 2. Experiência do Participante

#### Fase 1: Instruções
```
┌─────────────────────────────────────┐
│ 📝 Instruções                       │
│                                     │
│ Você verá X itens (frases ou fotos)│
│ Para cada um, digite sua resposta   │
│ sobre: [questao_tipo]               │
│                                     │
│        [Começar]                    │
└─────────────────────────────────────┘
```

#### Fase 2: Quiz Interativo
- **Exibição item por item**
- Contador de progresso: "Item X de Y"
- Input de texto para resposta
- Navegação:
  - Botão "← Anterior" (exceto no primeiro item)
  - Botão "Próximo →" (itens intermediários)
  - Botão "Finalizar ✓" (último item)
- Respostas são preservadas ao navegar

#### Fase 3: Conclusão
Após finalizar:
```
┌─────────────────────────────────────┐
│ ✓ Você já completou esta dinâmica!  │
│                                     │
│      [Ver Minhas Respostas]        │
└─────────────────────────────────────┘
```

#### Fase 4: Visualização de Respostas
Ao clicar em "Ver Minhas Respostas":
- Lista todos os itens com as respostas dadas
- Exibe a moral/mensagem final em destaque
- Botão toggle para ocultar/mostrar

### 3. Visualização Admin

#### Página de Respostas
- Tabela com todas as respostas dos participantes
- Colunas: Usuárie, Quando, Conteúdo
- Formato de conteúdo:
  ```
  Item 1: [resposta]
  Item 2: [resposta]
  Item 3: [resposta]
  ```

#### Exportação CSV
Formato de linha:
```csv
timestamp,dynamic_id,usuario_id,tipo,content
2025-10-10T19:00:00,1,42,quemsoeu,"Item 1: resposta1 | Item 2: resposta2 | Item 3: resposta3"
```

### 4. Edição de Dinâmica

- Interface similar à criação
- Campos pré-preenchidos com dados existentes
- Permite adicionar/remover/editar itens
- Atualização de `questao_tipo` e `moral`

## 🔧 Detalhes Técnicos

### Arquivos Modificados

#### 1. `gramatike_app/templates/dinamicas.html`
**Adições**:
- Opção "quemsoeu" no dropdown de tipos
- Seção `quemsoeu_builder` com:
  - Input para `questao_tipo`
  - Textarea para `moral`
  - Lista de itens (`items_list`)
  - Botão "+" para adicionar itens
  - Hidden input `quemsoeu_config_json`
- JavaScript para gerenciar itens:
  - Função `renderItems()`: renderiza lista de itens
  - Função `addItem()`: adiciona novo item
  - Serialização no submit do formulário

#### 2. `gramatike_app/templates/dinamica_view.html`
**Adições**:
- Seção condicional `{% elif d.tipo == 'quemsoeu' %}`
- **Para usuários que já responderam**:
  - Badge de confirmação
  - Botão "Ver Minhas Respostas"
  - Lista de respostas com toggle
  - Card de moral em destaque
- **Para usuários que não responderam**:
  - Div `quemsoeuInstrucoes` com instruções
  - Botão "Começar"
  - Div `quemsoeuJogo` (inicialmente oculta)
  - Formulário com inputs hidden dinâmicos
- JavaScript interativo:
  - Array `items` carregado do config
  - Variável `questaoTipo`
  - Array `respostas` para armazenar respostas temporárias
  - Função `mostrarItem(idx)`: renderiza item atual
  - Event listeners para navegação
  - Submit do formulário com inputs hidden

#### 3. `gramatike_app/templates/dinamica_edit.html`
**Adições**:
- Seção condicional para edição de quemsoeu
- Campos pré-preenchidos:
  - `questao_tipo` com valor de `cfg.get('questao_tipo', '')`
  - `moral` com valor de `cfg.get('moral', '')`
- Lista de itens carregada de `cfg.get('items', [])`
- JavaScript similar ao de criação para edição de itens

#### 4. `gramatike_app/templates/dinamica_admin.html`
**Adições**:
- Seção condicional para exibição de respostas quemsoeu
- Loop sobre `r.payload.respostas` para exibir respostas
- Formato: "Item X: [resposta]"
- Correção no formato de exibição de respostas oneword (word1, word2, word3)

#### 5. `gramatike_app/routes/__init__.py`

**Função `dinamicas_create()` - Linhas ~1221-1260**:
```python
elif tipo == 'quemsoeu':
    # Coleta e valida questao_tipo, moral e items
    # Normaliza estrutura dos itens
    # Valida conteúdo obrigatório
```

**Função `dinamica_update()` - Linhas ~1580-1620**:
```python
elif d.tipo == 'quemsoeu':
    # Atualiza configuração de quem sou eu
    # Preserva config existente se parcial
    # Valida e normaliza itens
```

**Função `dinamica_responder()` - Linhas ~1690-1700**:
```python
elif d.tipo == 'quemsoeu':
    # Coleta respostas do formulário
    # Formato: resposta_0, resposta_1, ...
    # Armazena em payload['respostas']
```

**CSV Export - Linhas ~1730-1740**:
```python
elif d.tipo == 'quemsoeu':
    # Formata: "Item 1: resposta1 | Item 2: resposta2"
```

### Estrutura de Dados

#### Config JSON (d.config)
```json
{
  "questao_tipo": "gênero",
  "moral": "Mensagem final aqui...",
  "items": [
    {
      "id": 1,
      "tipo": "frase",
      "conteudo": "Texto da frase aqui"
    },
    {
      "id": 2,
      "tipo": "foto",
      "conteudo": "https://example.com/imagem.jpg"
    }
  ]
}
```

#### Payload de Resposta (DynamicResponse.payload)
```json
{
  "respostas": [
    "resposta do item 1",
    "resposta do item 2",
    "resposta do item 3"
  ]
}
```

## 🎯 Casos de Uso

### Exemplo 1: Descobrir Gênero
- **questao_tipo**: "qual é o gênero?"
- **Items**:
  1. Frase: "Eu me identifico como uma pessoa não-binária"
  2. Frase: "Meus pronomes são ele/dele"
  3. Foto: [Imagem de símbolo de gênero neutro]
- **Moral**: "Gênero é uma construção social e cada pessoa tem o direito de se identificar como se sentir mais confortável!"

### Exemplo 2: Orientação Sexual
- **questao_tipo**: "orientação sexual"
- **Items**:
  1. Frase: "Sinto atração por pessoas de diferentes gêneros"
  2. Foto: [Bandeira pansexual]
  3. Frase: "Não sinto atração sexual por ninguém"
- **Moral**: "A orientação sexual é diversa e cada experiência é válida. Respeito e acolhimento são fundamentais!"

### Exemplo 3: Pronomes
- **questao_tipo**: "pronomes"
- **Items**:
  1. Frase: "Prefiro que me chamem no neutro"
  2. Frase: "Uso ela/dela nas minhas redes sociais"
  3. Frase: "Aceito qualquer pronome"
- **Moral**: "Respeitar os pronomes de cada pessoa é uma forma básica de respeito e reconhecimento de identidade!"

## 🧪 Testes Recomendados

### Testes Funcionais
- [ ] Criar dinâmica quemsoeu com 1 item (frase)
- [ ] Criar dinâmica quemsoeu com múltiplos itens (mix frase/foto)
- [ ] Validar erro se questao_tipo não for preenchido
- [ ] Validar erro se moral não for preenchida
- [ ] Validar erro se nenhum item for adicionado
- [ ] Testar navegação (Anterior/Próximo) durante quiz
- [ ] Verificar preservação de respostas ao navegar
- [ ] Testar submit e persistência de respostas
- [ ] Verificar visualização de respostas após conclusão
- [ ] Testar toggle de "Ver Minhas Respostas"
- [ ] Verificar exibição da moral
- [ ] Testar edição de dinâmica existente
- [ ] Verificar admin view com respostas
- [ ] Testar exportação CSV

### Testes de Interface
- [ ] Responsividade mobile
- [ ] Exibição correta de imagens
- [ ] Quebra de linha em frases longas
- [ ] Estados de botões (disabled/enabled)
- [ ] Feedback visual de progresso

### Testes de Segurança
- [ ] CSRF token presente em todos os formulários
- [ ] Validação de URLs de imagem (prevenir XSS)
- [ ] Sanitização de input de texto
- [ ] Verificação de permissões (admin only para criação/edição)
- [ ] Prevenção de múltiplas respostas do mesmo usuário

## 📝 Notas de Implementação

### Decisões de Design
1. **Step-by-step interface**: Escolhido para melhor foco e experiência mobile
2. **Navegação livre**: Permite revisitar respostas anteriores
3. **Moral revelada apenas após conclusão**: Mantém o suspense educativo
4. **Suporte a imagens via URL**: Evita complexidade de upload, usa Supabase se necessário
5. **Respostas de texto livre**: Permite análise qualitativa pelo admin

### Limitações Conhecidas
- Imagens devem ser URLs públicas (não há upload nesta versão)
- Não há validação de formato de imagem (aceita qualquer URL)
- Respostas são texto livre (sem opções pré-definidas)
- Não há pontuação ou "respostas corretas"

### Possíveis Melhorias Futuras
- Upload de imagens para Supabase
- Opção de resposta múltipla escolha
- Sistema de pontuação/gamificação
- Compartilhamento de resultados
- Análise de respostas com IA
- Exportação para PDF com respostas e moral

## 🚀 Deployment

### Checklist de Deploy
- [x] Templates HTML atualizados
- [x] Rotas backend implementadas
- [x] JavaScript validado
- [x] Jinja2 tags balanceados
- [x] CSRF protection em todos os forms
- [x] Validação de input no backend
- [x] Tratamento de erros
- [x] Suporte a CSV export
- [x] Documentação criada

### Variáveis de Ambiente
Não requer novas variáveis de ambiente. Usa a infraestrutura existente.

### Migrations
Não requer mudanças no schema do banco de dados. Usa os modelos existentes:
- `Dynamic` (tipo='quemsoeu', config=JSON)
- `DynamicResponse` (payload=JSON com respostas)

## 📚 Referências

- Modelo base: Dinâmicas existentes (poll, oneword, form)
- Padrão de UI: Template Bootstrap do projeto
- JavaScript: Vanilla JS (sem dependências externas)
- Inspiração: Google Forms, Quizzes interativos

---

**Implementado em**: Outubro 2025  
**Versão**: 1.0  
**Status**: ✅ Completo
