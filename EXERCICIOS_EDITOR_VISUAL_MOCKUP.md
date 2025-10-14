# 🎨 Visual Mockup: Editor de Tópicos para Exercícios

## 📱 Layout da Interface

```
╔════════════════════════════════════════════════════════════════════╗
║                        PAINEL DE CONTROLE                          ║
║                                                                    ║
║  [Usuários] [EDU] [Publi] [Reportar] [Gramátike] [Divulgação]   ║
║                                                                    ║
║  ┌─────────────────────────────────────────────────────────────┐ ║
║  │ [Artigos] [Apostilas] [Podcasts] [EXERCÍCIOS] [Redação]    │ ║
║  │                                                               │ ║
║  └─────────────────────────────────────────────────────────────┘ ║
╚════════════════════════════════════════════════════════════════════╝

╔════════════════════════════════════════════════════════════════════╗
║                         ABA: EXERCÍCIOS                            ║
╠════════════════════════════════════════════════════════════════════╣
║                                                                    ║
║  ┌──────────────────────────────────────────────────────────────┐ ║
║  │                    📝 Publicar Exercício                     │ ║
║  │                                                              │ ║
║  │  Tópico: [Selecione...        ▼]                           │ ║
║  │  Sessão: [Selecione...        ▼]                           │ ║
║  │  Tipo:   [Múltipla escolha    ▼]                           │ ║
║  │                                                              │ ║
║  │  Enunciado: [_________________________________]             │ ║
║  │             [                                 ]             │ ║
║  │                                                              │ ║
║  │  [Adicionar Exercício]                                       │ ║
║  └──────────────────────────────────────────────────────────────┘ ║
║                                                                    ║
║  ┌────────────────────┐  ┌────────────────────┐                  ║
║  │ 🎯 Criar Tópico    │  │ 📑 Criar Sessão    │                  ║
║  │                    │  │                    │                  ║
║  │ Nome:              │  │ Tópico: [▼]        │                  ║
║  │ [____________]     │  │ Nome:              │                  ║
║  │                    │  │ [____________]     │                  ║
║  │ Descrição:         │  │ Descrição:         │                  ║
║  │ [____________]     │  │ [____________]     │                  ║
║  │                    │  │ Ordem: [0]         │                  ║
║  │ [Criar]            │  │ [Criar Sessão]     │                  ║
║  └────────────────────┘  └────────────────────┘                  ║
║                                                                    ║
║  ╔════════════════════════════════════════════════════════════╗  ║
║  ║          ⭐ GERENCIAR TÓPICOS DE EXERCÍCIOS ⭐            ║  ║
║  ╚════════════════════════════════════════════════════════════╝  ║
║                                                                    ║
║  ┌──────────────────────────────────────────────────────────────┐ ║
║  │  📚 Verbos                                  [⚙️ Editar]      │ ║
║  │  Exercícios sobre conjugação verbal                         │ ║
║  │                                                              │ ║
║  │  ─────────────────── Sessões deste Tópico: ───────────────  │ ║
║  │                                                              │ ║
║  │  ┌────────────────────────────────────────────────────────┐ │ ║
║  │  │ 📝 Presente do Indicativo          [Editar]            │ │ ║
║  │  │    Conjugação no tempo presente                        │ │ ║
║  │  │    Ordem: 1                                            │ │ ║
║  │  └────────────────────────────────────────────────────────┘ │ ║
║  │                                                              │ ║
║  │  ┌────────────────────────────────────────────────────────┐ │ ║
║  │  │ 📝 Pretérito Perfeito              [Editar]            │ │ ║
║  │  │    Ordem: 2                                            │ │ ║
║  │  └────────────────────────────────────────────────────────┘ │ ║
║  │                                                              │ ║
║  │  ┌────────────────────────────────────────────────────────┐ │ ║
║  │  │ 📝 Futuro do Presente              [Editar]            │ │ ║
║  │  │    Ordem: 3                                            │ │ ║
║  │  └────────────────────────────────────────────────────────┘ │ ║
║  └──────────────────────────────────────────────────────────────┘ ║
║                                                                    ║
║  ┌──────────────────────────────────────────────────────────────┐ ║
║  │  📚 Concordância                            [⚙️ Editar]      │ ║
║  │  Concordância verbal e nominal                              │ ║
║  │                                                              │ ║
║  │  ─────────────────── Sessões deste Tópico: ───────────────  │ ║
║  │                                                              │ ║
║  │  ┌────────────────────────────────────────────────────────┐ │ ║
║  │  │ 📝 Concordância Verbal             [Editar]            │ │ ║
║  │  │    Ordem: 1                                            │ │ ║
║  │  └────────────────────────────────────────────────────────┘ │ ║
║  │                                                              │ ║
║  │  ┌────────────────────────────────────────────────────────┐ │ ║
║  │  │ 📝 Concordância Nominal            [Editar]            │ │ ║
║  │  │    Ordem: 2                                            │ │ ║
║  │  └────────────────────────────────────────────────────────┘ │ ║
║  └──────────────────────────────────────────────────────────────┘ ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
```

---

## 🔄 Estado Expandido: Editando Tópico

```
╔════════════════════════════════════════════════════════════════════╗
║  ┌──────────────────────────────────────────────────────────────┐ ║
║  │  📚 Verbos                                  [⚙️ Editar]      │ ║
║  │  Exercícios sobre conjugação verbal                         │ ║
║  │  ──────────────────────────────────────────────────────────  │ ║
║  │                                                              │ ║
║  │  📝 EDITAR TÓPICO                                           │ ║
║  │                                                              │ ║
║  │  Nome                                                        │ ║
║  │  ┌────────────────────────────────────────────────────────┐ │ ║
║  │  │ Verbos                                                 │ │ ║
║  │  └────────────────────────────────────────────────────────┘ │ ║
║  │                                                              │ ║
║  │  Descrição                                                   │ ║
║  │  ┌────────────────────────────────────────────────────────┐ │ ║
║  │  │ Exercícios sobre conjugação verbal                     │ │ ║
║  │  │                                                        │ │ ║
║  │  └────────────────────────────────────────────────────────┘ │ ║
║  │                                                              │ ║
║  │  ┌─────────────┐  ┌─────────────┐                          │ ║
║  │  │ 💾 Salvar   │  │ ❌ Cancelar │                          │ ║
║  │  └─────────────┘  └─────────────┘                          │ ║
║  │                                                              │ ║
║  │  ─────────────────── Sessões deste Tópico: ───────────────  │ ║
║  │  [... sessões listadas ...]                                 │ ║
║  └──────────────────────────────────────────────────────────────┘ ║
╚════════════════════════════════════════════════════════════════════╝
```

---

## 🔄 Estado Expandido: Editando Sessão

```
╔════════════════════════════════════════════════════════════════════╗
║  │  ┌────────────────────────────────────────────────────────┐ │ ║
║  │  │ 📝 Presente do Indicativo          [Editar]            │ │ ║
║  │  │    Conjugação no tempo presente                        │ │ ║
║  │  │    Ordem: 1                                            │ │ ║
║  │  │  ────────────────────────────────────────────────────  │ │ ║
║  │  │                                                        │ │ ║
║  │  │  📝 EDITAR SESSÃO                                      │ │ ║
║  │  │                                                        │ │ ║
║  │  │  Nome                                                  │ │ ║
║  │  │  ┌──────────────────────────────────────────────────┐ │ │ ║
║  │  │  │ Presente do Indicativo                           │ │ │ ║
║  │  │  └──────────────────────────────────────────────────┘ │ │ ║
║  │  │                                                        │ │ ║
║  │  │  Descrição                                             │ │ ║
║  │  │  ┌──────────────────────────────────────────────────┐ │ │ ║
║  │  │  │ Conjugação no tempo presente                     │ │ ║
║  │  │  └──────────────────────────────────────────────────┘ │ │ ║
║  │  │                                                        │ │ ║
║  │  │  Ordem                                                 │ │ ║
║  │  │  ┌─────┐                                              │ │ ║
║  │  │  │  1  │                                              │ │ ║
║  │  │  └─────┘                                              │ │ ║
║  │  │                                                        │ │ ║
║  │  │  ┌────────────┐  ┌────────────┐                       │ │ ║
║  │  │  │ 💾 Salvar  │  │ ❌ Cancelar│                       │ │ ║
║  │  │  └────────────┘  └────────────┘                       │ │ ║
║  │  └────────────────────────────────────────────────────────┘ │ ║
╚════════════════════════════════════════════════════════════════════╝
```

---

## 🎨 Paleta de Cores

```
╔═══════════════════════════════════════════════════════════╗
║  CORES UTILIZADAS                                         ║
╠═══════════════════════════════════════════════════════════╣
║                                                           ║
║  🟦 Background Card:      #f9fbfd (azul muito claro)     ║
║  ━━ Bordas:               #e3e9f0 (cinza claro)          ║
║  🟣 Botão Salvar:         --accent (roxo do tema)        ║
║  ⚪ Background Sessão:     #ffffff (branco)              ║
║  🔤 Texto Principal:       #333333 (cinza escuro)        ║
║  📝 Texto Secundário:      #666666 (cinza médio)         ║
║  🔢 Texto Ordem:           #999999 (cinza claro)         ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
```

---

## 📏 Dimensões e Espaçamento

```
╔═══════════════════════════════════════════════════════════╗
║  MEDIDAS                                                  ║
╠═══════════════════════════════════════════════════════════╣
║                                                           ║
║  Border Radius Card Tópico:     12px                     ║
║  Border Radius Card Sessão:      8px                     ║
║  Border Radius Input:            8px (tópico) / 6px (sessão)
║  Gap entre Cards:                0.8rem                   ║
║  Gap entre Sessões:              0.5rem                   ║
║  Padding Card Tópico:            0.9rem                   ║
║  Padding Card Sessão:            0.6rem                   ║
║  Padding Formulário:             0.5rem (tópico) / 0.4rem (sessão)
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
```

---

## 🔤 Tipografia

```
╔═══════════════════════════════════════════════════════════╗
║  FONTES                                                   ║
╠═══════════════════════════════════════════════════════════╣
║                                                           ║
║  Família Principal:    'Nunito', sans-serif              ║
║                                                           ║
║  Título "Gerenciar...":  H3 (tamanho padrão)            ║
║  Nome do Tópico:         0.85rem, font-weight: 700       ║
║  Descrição Tópico:       0.7rem, color: #666             ║
║  Nome da Sessão:         0.75rem, font-weight: 600       ║
║  Descrição Sessão:       0.65rem, color: #666            ║
║  Label Formulário:       0.7rem (tópico) / 0.65rem (sessão)
║  Input/Textarea:         0.72rem (tópico) / 0.68rem (sessão)
║  Botão:                  0.65rem (tópico) / 0.6rem (sessão)
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
```

---

## 📱 Responsividade

### Desktop (> 980px)
```
┌─────────────────────────────────────────────────────┐
│  ┌──────────────────────┐  ┌────────────────────┐  │
│  │ Criar Tópico         │  │ Criar Sessão       │  │
│  └──────────────────────┘  └────────────────────┘  │
│                                                     │
│  ┌─────────────────────────────────────────────┐   │
│  │ Gerenciar Tópicos (largura completa)        │   │
│  └─────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

### Mobile (≤ 980px)
```
┌──────────────────────┐
│ Criar Tópico         │
│ (largura 100%)       │
└──────────────────────┘

┌──────────────────────┐
│ Criar Sessão         │
│ (largura 100%)       │
└──────────────────────┘

┌──────────────────────┐
│ Gerenciar Tópicos    │
│ (largura 100%)       │
└──────────────────────┘
```

---

## 🖱️ Interações

### Botão [Editar] - Hover
```
┌─────────────────┐        ┌─────────────────┐
│  ⚙️ Editar      │   →    │  ⚙️ Editar      │
│  (normal)       │        │  (hover: accent)│
└─────────────────┘        └─────────────────┘
```

### Formulário - Toggle
```
Estado Inicial:           Ao clicar em [Editar]:
─────────────            ──────────────────────
[Editar] (visível)       [Editar] (visível)
Formulário (oculto)      Formulário (visível)
                         ↑ display: none → block
```

### Feedback Visual
```
✅ Sucesso:  Flash verde (padrão do sistema)
❌ Erro:     Flash vermelho (padrão do sistema)
💾 Salvando: Botão desabilitado (opcional futuro)
```

---

## 🏗️ Estrutura HTML (Simplificada)

```html
<div class="edu-box">
  <h3>Gerenciar Tópicos de Exercícios</h3>
  
  <div> <!-- Container de tópicos -->
    <div> <!-- Card Tópico -->
      <div> <!-- Header com nome e botão -->
        <div>Nome + Descrição</div>
        <button onclick="toggleTopicEdit()">Editar</button>
      </div>
      
      <div id="topic-edit-{id}" style="display:none"> <!-- Formulário -->
        <form action="/admin/exercicios/topic/{id}" method="POST">
          <input name="nome" />
          <textarea name="descricao"></textarea>
          <button type="submit">Salvar</button>
          <button type="button">Cancelar</button>
        </form>
      </div>
      
      <div> <!-- Sessões deste tópico -->
        <div> <!-- Card Sessão -->
          <div>Nome + Descrição + Ordem</div>
          <button onclick="toggleTopicEdit()">Editar</button>
          
          <div id="topic-edit-section-{id}" style="display:none">
            <form action="/admin/exercicios/section/{id}" method="POST">
              <!-- Campos da sessão -->
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>
```

---

## 🎯 Componentes Reutilizados

Usa os mesmos componentes/estilos de:
- ✅ Gerenciar Tópicos de Artigos
- ✅ Gerenciar Tópicos de Apostilas
- ✅ Gerenciar Tópicos de Podcasts
- ✅ Gerenciar Tópicos de Redação
- ✅ Gerenciar Tópicos de Vídeos

**Diferencial:** Adiciona sub-nível (Sessões) dentro de cada Tópico! 🌟

---

**Mockup criado em:** 2025-10-14  
**Design System:** Gramátike Admin Panel  
**Versão:** 1.0
