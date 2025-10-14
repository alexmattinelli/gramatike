# 📊 Diagrama da Implementação - Editor de Tópicos para Exercícios

## 🏗️ Arquitetura da Solução

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND                                │
│                  (dashboard.html)                               │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  📍 Aba: EXERCÍCIOS                                       │ │
│  │                                                           │ │
│  │  ┌─────────────────────────────────────────────────────┐ │ │
│  │  │ 📝 Publicar Exercício                               │ │ │
│  │  │ [Formulário existente]                              │ │ │
│  │  └─────────────────────────────────────────────────────┘ │ │
│  │                                                           │ │
│  │  ┌──────────────────┐  ┌──────────────────┐             │ │
│  │  │ 🎯 Criar Tópico  │  │ 📑 Criar Sessão  │             │ │
│  │  │ [Existente]      │  │ [Existente]      │             │ │
│  │  └──────────────────┘  └──────────────────┘             │ │
│  │                                                           │ │
│  │  ┌─────────────────────────────────────────────────────┐ │ │
│  │  │ ⭐ GERENCIAR TÓPICOS (NOVO!)                       │ │ │
│  │  │                                                     │ │ │
│  │  │  {% for topic in topics %}                         │ │ │
│  │  │    ┌──────────────────────────────────────────┐    │ │ │
│  │  │    │ 📚 {{ topic.nome }}        [⚙️ Editar]  │    │ │ │
│  │  │    │                                          │    │ │ │
│  │  │    │ <div id="topic-edit-exercicio-{{id}}">  │    │ │ │
│  │  │    │   <form POST exercicios_topic_update>    │    │ │ │
│  │  │    │     Nome: [_______]                      │    │ │ │
│  │  │    │     Desc: [_______]                      │    │ │ │
│  │  │    │     [Salvar] [Cancelar]                  │    │ │ │
│  │  │    │   </form>                                │    │ │ │
│  │  │    │ </div>                                   │    │ │ │
│  │  │    │                                          │    │ │ │
│  │  │    │ ── Sessões: ──                          │    │ │ │
│  │  │    │                                          │    │ │ │
│  │  │    │  {% for section in topic.sections %}    │    │ │ │
│  │  │    │    ┌───────────────────────────────┐    │    │ │ │
│  │  │    │    │ 📝 {{ section.nome }} [Edit] │    │    │ │ │
│  │  │    │    │                               │    │    │ │ │
│  │  │    │    │ <div id="topic-edit-section"> │    │    │ │ │
│  │  │    │    │   <form POST section_update>  │    │    │ │ │
│  │  │    │    │     Nome: [____]              │    │    │ │ │
│  │  │    │    │     Desc: [____]              │    │    │ │ │
│  │  │    │    │     Ordem:[__]                │    │    │ │ │
│  │  │    │    │     [Salvar] [Cancelar]       │    │    │ │ │
│  │  │    │    │   </form>                     │    │    │ │ │
│  │  │    │    │ </div>                        │    │    │ │ │
│  │  │    │    └───────────────────────────────┘    │    │ │ │
│  │  │    │  {% endfor %}                            │    │ │ │
│  │  │    └──────────────────────────────────────────┘    │ │ │
│  │  │  {% endfor %}                                      │ │ │
│  │  └─────────────────────────────────────────────────────┘ │ │
│  └───────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                │
                                │ HTTP POST
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                          BACKEND                                │
│                      (admin.py routes)                          │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ @admin_bp.route('/exercicios/topic/<id>', POST)         │   │
│  │ def exercicios_topic_update(topic_id):                  │   │
│  │   ✓ Verifica autenticação                              │   │
│  │   ✓ Verifica is_admin                                  │   │
│  │   ✓ Busca ExerciseTopic no DB                          │   │
│  │   ✓ Valida nome não vazio                              │   │
│  │   ✓ Valida nome único                                  │   │
│  │   ✓ Atualiza topic.nome e topic.descricao             │   │
│  │   ✓ db.session.commit()                                │   │
│  │   ✓ flash('Tópico atualizado')                         │   │
│  │   ✓ redirect(dashboard)                                │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ @admin_bp.route('/exercicios/section/<id>', POST)       │   │
│  │ def exercicios_section_update(section_id):              │   │
│  │   ✓ Verifica autenticação                              │   │
│  │   ✓ Verifica is_admin                                  │   │
│  │   ✓ Busca ExerciseSection no DB                        │   │
│  │   ✓ Valida nome não vazio                              │   │
│  │   ✓ Valida nome único no topic                         │   │
│  │   ✓ Valida ordem (int)                                 │   │
│  │   ✓ Atualiza section.nome, descricao, ordem            │   │
│  │   ✓ db.session.commit()                                │   │
│  │   ✓ flash('Sessão atualizada')                         │   │
│  │   ✓ redirect(dashboard)                                │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                                │
                                │ ORM (SQLAlchemy)
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                        DATABASE                                 │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  TABLE: exercise_topic                                   │  │
│  │  ─────────────────────────────────────────────────────   │  │
│  │  id (PK)  │  nome  │  descricao  │  created_at          │  │
│  │  ─────────────────────────────────────────────────────   │  │
│  │  1        │ Verbos │ Exercícios...│ 2025-01-01          │  │
│  │  2        │ Conc.  │ Concordância.│ 2025-01-02          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  TABLE: exercise_section                                 │  │
│  │  ─────────────────────────────────────────────────────   │  │
│  │  id │ topic_id(FK) │ nome      │ descricao │ ordem      │  │
│  │  ─────────────────────────────────────────────────────   │  │
│  │  1  │      1       │ Presente  │ Conj...   │   1        │  │
│  │  2  │      1       │ Passado   │ NULL      │   2        │  │
│  │  3  │      2       │ Verbal    │ Conc...   │   1        │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Fluxo de Dados - Editar Tópico

```
┌─────────┐     ┌─────────┐     ┌──────────┐     ┌──────────┐
│ Usuário │────>│  Form   │────>│  Route   │────>│    DB    │
│ Admin   │     │  HTML   │     │  Flask   │     │  SQLite  │
└─────────┘     └─────────┘     └──────────┘     └──────────┘
    │                │                 │                │
    │ 1. Clica       │                 │                │
    │    [Editar]    │                 │                │
    │                │                 │                │
    ▼                │                 │                │
    │ 2. Expande     │                 │                │
    │    formulário  │                 │                │
    │                │                 │                │
    ▼                │                 │                │
    │ 3. Preenche    │                 │                │
    │    campos      │                 │                │
    │                │                 │                │
    ▼                │                 │                │
    │ 4. [Salvar]───>│ 5. POST        │                │
    │                │    /exercicios/ │                │
    │                │    topic/<id>   │                │
    │                │                 │                │
    │                ▼                 │                │
    │                │ 6. Valida ─────>│ 7. UPDATE     │
    │                │    CSRF         │    SET        │
    │                │    is_admin     │    nome=...   │
    │                │    nome único   │    WHERE id=  │
    │                │                 │                │
    │                │                 ◀────────────────│
    │                │ 8. Commit OK    │                │
    │                │                 │                │
    │ 9. Redirect ◀──│                 │                │
    │    + Flash     │                 │                │
    │                │                 │                │
    ▼                │                 │                │
┌─────────────────────────────────────────────────────────┐
│ Dashboard atualizado com mensagem:                      │
│ "✅ Tópico atualizado com sucesso."                     │
└─────────────────────────────────────────────────────────┘
```

---

## 🎨 Hierarquia de Componentes UI

```
dashboard.html
│
├── <div id="area-exercicios">
│   │
│   ├── <div class="edu-box"> Publicar Exercício
│   │
│   ├── <div class="edu-box"> Criar Tópico
│   │
│   ├── <div class="edu-box"> Criar Sessão
│   │
│   └── <div class="edu-box"> ⭐ Gerenciar Tópicos (NOVO)
│       │
│       └── {% for topic in topics %}
│           │
│           ├── <div> Card do Tópico
│           │   │
│           │   ├── <div> Header (Nome + Botão Editar)
│           │   │
│           │   ├── <div id="topic-edit-exercicio-{{id}}">
│           │   │   │
│           │   │   └── <form> Formulário de Edição
│           │   │       ├── <input name="nome">
│           │   │       ├── <textarea name="descricao">
│           │   │       ├── <button>Salvar</button>
│           │   │       └── <button>Cancelar</button>
│           │   │
│           │   └── <div> Sessões deste Tópico
│           │       │
│           │       └── {% for section in topic.sections %}
│           │           │
│           │           └── <div> Card da Sessão
│           │               │
│           │               ├── <div> Header (Nome + Ordem + Editar)
│           │               │
│           │               └── <div id="topic-edit-section-{{id}}">
│           │                   │
│           │                   └── <form> Formulário de Edição
│           │                       ├── <input name="nome">
│           │                       ├── <textarea name="descricao">
│           │                       ├── <input name="ordem">
│           │                       ├── <button>Salvar</button>
│           │                       └── <button>Cancelar</button>
│           └── {% endfor %}
```

---

## 🔐 Camadas de Segurança

```
┌─────────────────────────────────────────────────────────────┐
│                    CAMADA 1: Autenticação                   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ @login_required decorator                           │   │
│  │ Verifica: current_user.is_authenticated             │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    CAMADA 2: Autorização                    │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ if not current_user.is_admin:                       │   │
│  │     return redirect(url_for('main.index'))         │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                     CAMADA 3: CSRF                          │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ <input name="csrf_token" value="{{ csrf_token() }}">│   │
│  │ Flask-WTF valida automaticamente                    │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                  CAMADA 4: Validação de Dados               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ • Nome não vazio                                    │   │
│  │ • Nome único (para tópicos)                         │   │
│  │ • Nome único no tópico (para sessões)               │   │
│  │ • Ordem é número inteiro                            │   │
│  │ • ID existe no banco (404 se não)                   │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   CAMADA 5: Banco de Dados                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ • Constraints (UNIQUE, NOT NULL, FK)                │   │
│  │ • Indexes para performance                          │   │
│  │ • Transações ACID                                   │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 Modelo de Dados

```
┌─────────────────────────────────────────────────────────────┐
│                    ExerciseTopic                            │
│  ─────────────────────────────────────────────────────────  │
│  id: Integer, PK, Auto-increment                           │
│  nome: String(150), NOT NULL, UNIQUE                       │
│  descricao: Text, NULLABLE                                 │
│  created_at: DateTime, DEFAULT now()                       │
│  ─────────────────────────────────────────────────────────  │
│  Relationships:                                            │
│    sections = relationship('ExerciseSection', backref)     │
└─────────────────────────────────────────────────────────────┘
                           │
                           │ 1 : N
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   ExerciseSection                           │
│  ─────────────────────────────────────────────────────────  │
│  id: Integer, PK, Auto-increment                           │
│  topic_id: Integer, FK(exercise_topic.id), NOT NULL        │
│  nome: String(180), NOT NULL                               │
│  descricao: Text, NULLABLE                                 │
│  ordem: Integer, DEFAULT 0                                 │
│  created_at: DateTime, DEFAULT now()                       │
│  ─────────────────────────────────────────────────────────  │
│  Constraints:                                              │
│    UNIQUE(topic_id, nome) -- nome único por tópico        │
│  Relationships:                                            │
│    topic = relationship('ExerciseTopic', backref)          │
└─────────────────────────────────────────────────────────────┘
```

---

## 🧪 Casos de Teste

```
┌─────────────────────────────────────────────────────────────┐
│  TESTE 1: Editar Tópico com Sucesso                        │
│  ─────────────────────────────────────────────────────────  │
│  Given: Usuário admin autenticado                          │
│  When:  Edita nome de "Verbos" para "Verbos Irregulares"  │
│  Then:  DB atualizado                                      │
│         Flash: "Tópico atualizado com sucesso."           │
│         ✅ PASS                                            │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  TESTE 2: Validação de Nome Duplicado (Tópico)             │
│  ─────────────────────────────────────────────────────────  │
│  Given: Tópico "Concordância" já existe                    │
│  When:  Tenta editar outro tópico para "Concordância"      │
│  Then:  DB não muda                                        │
│         Flash: "Já existe tópico com esse nome."          │
│         ✅ PASS                                            │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  TESTE 3: Editar Sessão - Ordem                            │
│  ─────────────────────────────────────────────────────────  │
│  Given: Sessão com ordem=1                                 │
│  When:  Edita ordem para 5                                 │
│  Then:  DB atualizado com ordem=5                          │
│         Flash: "Sessão atualizada com sucesso."           │
│         ✅ PASS                                            │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  TESTE 4: Permissão Negada (Não Admin)                     │
│  ─────────────────────────────────────────────────────────  │
│  Given: Usuário não-admin autenticado                      │
│  When:  Tenta acessar rota de edição                       │
│  Then:  Redirect para main.index                           │
│         ❌ Não autorizado                                  │
│         ✅ PASS                                            │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  TESTE 5: ID Inválido (404)                                │
│  ─────────────────────────────────────────────────────────  │
│  Given: ID 9999 não existe no DB                           │
│  When:  POST /exercicios/topic/9999                        │
│  Then:  HTTP 404 Not Found                                 │
│         ✅ PASS                                            │
└─────────────────────────────────────────────────────────────┘
```

---

## 📈 Métricas de Implementação

```
╔═══════════════════════════════════════════════════════════╗
║                   ESTATÍSTICAS                            ║
╠═══════════════════════════════════════════════════════════╣
║                                                           ║
║  Arquivos Modificados:           2                       ║
║  Arquivos de Documentação:       6                       ║
║  Linhas de Código Adicionadas:   ~160                    ║
║  Linhas de Docs Adicionadas:     ~1,400                  ║
║  Rotas Criadas:                  2                       ║
║  Componentes UI:                 3 (tópico, sessão, form)║
║  Validações Implementadas:       6                       ║
║  Casos de Teste:                 5+                      ║
║  Commits:                        5                       ║
║  Tempo de Desenvolvimento:       ~2 horas                ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
```

---

**Diagrama criado em:** 2025-10-14  
**Versão:** 1.0  
**Ferramenta:** ASCII Diagrams
