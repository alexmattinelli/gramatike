# Fix: Article Summary (Resumo) Truncation with "Ver mais"

## Issue
The user reported that they couldn't display the full article summary (resumo) when it's very long. They wanted a solution to show a truncated version with "..." and a "Ver mais" (See more) option to expand it.

## Example of Long Resumo
The user provided this example:
> "Neste texto, proponho uma abordagem de neutralização de gênero em português brasileiro na perspectiva do sistema linguístico. Para isso, parto de considerações sobre a caracterização de mudanças deliberadas e sobre os padrões de marcação e produtividade de gênero gramatical na língua. São avaliados, nessa perspectiva, quatro tipos de empregos correntes de gênero inclusivo: uso de feminino marcado no caso de substantivos comuns de dois gêneros (ex. a presidenta); emprego de formas femininas e masculinas, sobretudo em vocativos, em vez do uso genérico do masculino (ex. alunas e alunos); inclusão de novas marcas no final de nomes e adjetivos, como x e @ (ex. amigx, amig@), ou ampliação da função de marcas já existentes, como -e (ex. amigue); alteração na base de pronomes e artigos (ex. ile, le). Desses empregos, além do feminino marcado e do contraste entre formas femininas e masculinas, que já têm uso significativo na língua, proponho que, no domínio da palavra, -e encontra condições menos limitadas para expansão no sistema no subconjunto de substantivos e adjetivos sexuados."

Length: 1090 characters

## Solution Implemented

### 1. Smart Truncation Logic
- **Resumos ≤ 300 characters**: Display in full (no truncation)
- **Resumos > 300 characters**: Show first 300 chars + "..." + "Ver mais" link

### 2. Interactive "Ver mais" / "Ver menos"
- Clicking "Ver mais" expands to show the full resumo
- Clicking "Ver menos" collapses back to the truncated version
- Smooth toggle without page reload
- Each article maintains its own state

## How It Works

### Before (Short Resumo)
```
Este é um resumo curto que não precisa de truncagem.
```
✓ Displays as-is (no "Ver mais" link)

### Before (Long Resumo - Truncated)
```
Neste texto, proponho uma abordagem de neutralização de gênero em português 
brasileiro na perspectiva do sistema linguístico. Para isso, parto de 
considerações sobre a caracterização de mudanças deliberadas e sobre os 
padrões de marcação e produtividade de gênero gramatical na língua. São 
avaliados,...

[Ver mais]  ← Click to expand
```

### After (Long Resumo - Expanded)
```
Neste texto, proponho uma abordagem de neutralização de gênero em português 
brasileiro na perspectiva do sistema linguístico. Para isso, parto de 
considerações sobre a caracterização de mudanças deliberadas e sobre os 
padrões de marcação e produtividade de gênero gramatical na língua. São 
avaliados, nessa perspectiva, quatro tipos de empregos correntes de gênero 
inclusivo: uso de feminino marcado no caso de substantivos comuns de dois 
gêneros (ex. a presidenta); emprego de formas femininas e masculinas, 
sobretudo em vocativos, em vez do uso genérico do masculino (ex. alunas e 
alunos); inclusão de novas marcas no final de nomes e adjetivos, como x e 
@ (ex. amigx, amig@), ou ampliação da função de marcas já existentes, como 
-e (ex. amigue); alteração na base de pronomes e artigos (ex. ile, le). 
Desses empregos, além do feminino marcado e do contraste entre formas 
femininas e masculinas, que já têm uso significativo na língua, proponho 
que, no domínio da palavra, -e encontra condições menos limitadas para 
expansão no sistema no subconjunto de substantivos e adjetivos sexuados.

[Ver menos]  ← Click to collapse
```

## Technical Implementation

### Template Changes (artigos.html)
1. **Jinja2 Logic**: Check if resumo length > 300 characters
2. **HTML Structure**: Two divs (short and full), toggled via JavaScript
3. **Styling**: Consistent with existing design (purple links)

### JavaScript
- Event listener for "Ver mais" / "Ver menos" clicks
- Toggle display of `.resumo-short` and `.resumo-full` divs
- Uses data attributes to target specific articles

## Files Modified
- `gramatike_app/templates/artigos.html`
  - Added truncation logic (lines 236-250)
  - Added JavaScript toggle functionality (lines 528-545)

## Database Support
✓ Already supports up to 2000 characters for `resumo` field (model and migrations)
✓ No database changes needed

## Benefits
1. **Better UX**: Users can scan articles quickly without overwhelming text
2. **Full Access**: Users can still read complete summaries on demand
3. **Clean Design**: Maintains visual consistency with site design
4. **No Breaking Changes**: Short summaries display exactly as before
5. **Progressive Enhancement**: Works without JavaScript (shows full text)

## Testing Performed
✓ Jinja2 template syntax validation passed
✓ Test rendering with 1090-character resumo (example from issue)
✓ Test rendering with 52-character resumo (short example)
✓ Verified 300-character truncation point
✓ Verified "Ver mais" / "Ver menos" toggle HTML generation

## User Experience
- **Mobile-friendly**: Collapsed by default saves vertical space
- **Accessible**: Clickable links with clear labels
- **Intuitive**: Standard "Ver mais" / "Ver menos" pattern familiar to users
- **Performant**: Pure CSS/JS toggle, no server requests
