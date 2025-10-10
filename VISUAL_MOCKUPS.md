# Visual Mockups - "Quem Sou Eu" Enhancements

## 1. Photo Upload - Create Form

### Before (URL Input):
```
┌────────────────────────────────────────┐
│ ○ Frase  ● Foto                        │
│                                        │
│ URL da Foto                            │
│ ┌────────────────────────────────────┐ │
│ │ https://...                        │ │
│ └────────────────────────────────────┘ │
└────────────────────────────────────────┘
```

### After (File Upload):
```
┌────────────────────────────────────────┐
│ ○ Frase  ● Foto                        │
│                                        │
│ Foto                                   │
│ ┌────────────────────────────────────┐ │
│ │ 📁 Escolher arquivo...             │ │
│ └────────────────────────────────────┘ │
│                                        │
│ Resposta Correta (opcional)            │
│ ┌────────────────────────────────────┐ │
│ │ Ex: masculino, feminino...         │ │
│ └────────────────────────────────────┘ │
└────────────────────────────────────────┘
```

## 2. Photo Upload - Edit Form

### With Existing Photo:
```
┌────────────────────────────────────────┐
│ ○ Frase  ● Foto                        │
│                                        │
│ Foto                                   │
│ ┌────────────────────────────────────┐ │
│ │ 📁 Escolher arquivo...             │ │
│ └────────────────────────────────────┘ │
│ Atual: ver foto ↗                      │
│                                        │
│ Resposta Correta (opcional)            │
│ ┌────────────────────────────────────┐ │
│ │ não-binário                        │ │
│ └────────────────────────────────────┘ │
└────────────────────────────────────────┘
```

## 3. Reset Password Form

### Before:
```
┌──────────────────────────────┐
│   Redefinir senha            │
│                              │
│ NOVA SENHA                   │
│ ┌──────────────────────────┐ │
│ │ ••••••••                 │ │
│ └──────────────────────────┘ │
│                              │
│ CONFIRMAR NOVA SENHA         │
│ ┌──────────────────────────┐ │
│ │ ••••••••                 │ │
│ └──────────────────────────┘ │
│                              │
│ ┌──────────────────────────┐ │
│ │  Salvar nova senha       │ │
│ └──────────────────────────┘ │
└──────────────────────────────┘
```

### After:
```
┌──────────────────────────────────────┐
│      Redefinir senha                 │
│                                      │
│ NOVA SENHA                           │
│ ┌──────────────────────────────────┐ │
│ │ ••••••••                    👁   │ │
│ └──────────────────────────────────┘ │
│                                      │
│ CONFIRMAR NOVA SENHA                 │
│ ┌──────────────────────────────────┐ │
│ │ ••••••••                    👁   │ │
│ └──────────────────────────────────┘ │
│                                      │
│ ┌──────────────────────────────────┐ │
│ │      Salvar nova senha           │ │
│ └──────────────────────────────────┘ │
└──────────────────────────────────────┘
```

**Enhanced Features:**
- Purple heading (#6233B5)
- Eye toggle for password visibility
- Modern rounded corners (20px)
- Better shadow and spacing
- Focus state changes border to purple

## 4. Accuracy View - Admin Dashboard

### Overall Accuracy Card:
```
┌──────────────────────────────────────────┐
│          Taxa de Acertos                 │
│                                          │
│          ┌────────────────────┐          │
│          │                    │          │
│          │      85.5%         │          │
│          │                    │          │
│          │ Taxa de Acertos    │          │
│          │      Geral         │          │
│          │                    │          │
│          └────────────────────┘          │
│          (Purple background)              │
└──────────────────────────────────────────┘
```

### Per-Item Breakdown:
```
┌──────────────────────────────────────────┐
│ Por Item:                                │
│                                          │
│ ┌──────────────────────────────────────┐ │
│ │ Item 1    [frase]           92.3%   │ │
│ │ ───────────────────────────────────  │ │
│ │ "Eu me identifico como pessoa       │ │
│ │  que não se encaixa no binário..."  │ │
│ │                                      │ │
│ │ Resposta correta: não-binário        │ │
│ │ 12 de 13 acertaram                   │ │
│ └──────────────────────────────────────┘ │
│                                          │
│ ┌──────────────────────────────────────┐ │
│ │ Item 2    [foto]            78.6%   │ │
│ │ ───────────────────────────────────  │ │
│ │ Foto: ver imagem ↗                   │ │
│ │                                      │ │
│ │ Resposta correta: masculino          │ │
│ │ 11 de 14 acertaram                   │ │
│ └──────────────────────────────────────┘ │
│                                          │
│ ┌──────────────────────────────────────┐ │
│ │ Item 3    [frase]           66.7%   │ │
│ │ ───────────────────────────────────  │ │
│ │ "Eu uso pronomes neutres"            │ │
│ │                                      │ │
│ │ Resposta correta: não-binário        │ │
│ │ 8 de 12 acertaram                    │ │
│ └──────────────────────────────────────┘ │
└──────────────────────────────────────────┘
```

## 5. Create Form - Complete View

```
┌────────────────────────────────────────────────┐
│            Criar dinâmica                      │
│                                                │
│ Tipo                                           │
│ ┌────────────────────────────────────────────┐ │
│ │ Quem sou eu?                          ▼   │ │
│ └────────────────────────────────────────────┘ │
│                                                │
│ Título                                         │
│ ┌────────────────────────────────────────────┐ │
│ │ Identidade de Gênero                      │ │
│ └────────────────────────────────────────────┘ │
│                                                │
│ Descrição (opcional)                           │
│ ┌────────────────────────────────────────────┐ │
│ │ Vamos explorar identidades...             │ │
│ └────────────────────────────────────────────┘ │
│                                                │
│ O que a pessoa deve descobrir?                 │
│ ┌────────────────────────────────────────────┐ │
│ │ identidade de gênero                      │ │
│ └────────────────────────────────────────────┘ │
│                                                │
│ Moral/Mensagem Final                           │
│ ┌────────────────────────────────────────────┐ │
│ │ A identidade de gênero é única...         │ │
│ └────────────────────────────────────────────┘ │
│                                                │
│ ┌────────────────────────────────────────────┐ │
│ │ [Item 1] ○ Frase ● Foto     [Remover]    │ │
│ │                                            │ │
│ │ Foto                                       │ │
│ │ ┌────────────────────────────────────────┐ │ │
│ │ │ 📁 pride_flag.jpg                     │ │ │
│ │ └────────────────────────────────────────┘ │ │
│ │                                            │ │
│ │ Resposta Correta (opcional)                │ │
│ │ ┌────────────────────────────────────────┐ │ │
│ │ │ não-binário                            │ │ │
│ │ └────────────────────────────────────────┘ │ │
│ └────────────────────────────────────────────┘ │
│                                                │
│ ┌────────────────────────────────────────────┐ │
│ │ [Item 2] ● Frase ○ Foto     [Remover]    │ │
│ │                                            │ │
│ │ Frase                                      │ │
│ │ ┌────────────────────────────────────────┐ │ │
│ │ │ Eu me identifico como pessoa que...   │ │ │
│ │ └────────────────────────────────────────┘ │ │
│ │                                            │ │
│ │ Resposta Correta (opcional)                │ │
│ │ ┌────────────────────────────────────────┐ │ │
│ │ │ não-binário                            │ │ │
│ │ └────────────────────────────────────────┘ │ │
│ └────────────────────────────────────────────┘ │
│                                                │
│ [+ Item (Frase ou Foto)]                       │
│                                                │
│ ┌────────────────────────────────────────────┐ │
│ │              Criar                         │ │
│ └────────────────────────────────────────────┘ │
└────────────────────────────────────────────────┘
```

## 6. Color Scheme

### Primary Colors:
- **Primary Purple:** `#9B5DE5` - Buttons, headings, accents
- **Dark Purple:** `#6233B5` - Text, labels
- **Light Purple:** `#f0e5ff` - Backgrounds, highlights

### Neutral Colors:
- **Border:** `#cfd7e2` - Input borders, dividers
- **Text:** `#222` - Primary text
- **Muted:** `#666` - Secondary text
- **Background:** `#f7f8ff` - Page background

### Feedback Colors:
- **Success:** `#10b981` - Correct answers
- **Error:** `#ef4444` - Wrong answers
- **Warning:** `#f59e0b` - Alerts

## 7. Responsive Behavior

### Desktop (> 980px):
- Form max-width: 980px
- Two-column layout where appropriate
- Larger font sizes
- More spacing

### Mobile (< 980px):
- Single column layout
- Compact spacing
- Touch-friendly buttons (min 44px height)
- Simplified navigation

### File Input:
- Desktop: Shows "Escolher arquivo" with filename
- Mobile: Native file picker with camera option

## 8. Animation & Transitions

### Focus States:
```css
input:focus {
  border-color: #9B5DE5;
  transition: border-color 0.2s;
}
```

### Hover Effects:
```css
.btn:hover {
  background: #7d3dc9;
  transition: background 0.2s;
}
```

### Toggle Animation:
```javascript
// Eye icon changes on click
'👁' → '🙈' (with type change)
password → text
```

## 9. Accessibility Features

- **Labels:** All inputs have associated labels
- **ARIA:** `aria-label` on icon buttons
- **Focus:** Clear focus indicators
- **Contrast:** WCAG AA compliant colors
- **Touch Targets:** Minimum 44x44px
- **Keyboard:** Full keyboard navigation support

## 10. Error States

### Upload Error:
```
┌────────────────────────────────────────┐
│ Foto                                   │
│ ┌────────────────────────────────────┐ │
│ │ 📁 Escolher arquivo...             │ │
│ └────────────────────────────────────┘ │
│ ❌ Erro ao fazer upload da foto       │
└────────────────────────────────────────┘
```

### Validation Error:
```
┌────────────────────────────────────────┐
│ O que a pessoa deve descobrir?         │
│ ┌────────────────────────────────────┐ │
│ │                                    │ │ (red border)
│ └────────────────────────────────────┘ │
│ ⚠️ Este campo é obrigatório           │
└────────────────────────────────────────┘
```
