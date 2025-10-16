# Fix: Redução do Tamanho da Fonte "Ver mais" / "Ver menos"

## Problema Identificado

O usuário solicitou que fosse reduzido o **tamanho da palavra "ver mais"**, não a quantidade de texto exibida. A implementação anterior não especificava um `font-size` para os links "Ver mais" e "Ver menos", fazendo com que herdassem o tamanho padrão do texto, ficando muito grandes em comparação ao resumo.

## Solução Implementada

Adicionado `font-size:.65rem;` aos links "Ver mais" e "Ver menos" no arquivo `gramatike_app/templates/artigos.html`.

### Mudanças no Código

**Arquivo:** `gramatike_app/templates/artigos.html`

**Linha 242 (link "Ver mais"):**
```html
<!-- Antes -->
<a href="javascript:void(0)" class="ver-mais" data-target="{{ c.id }}" style="color:#9B5DE5; font-weight:700; text-decoration:none; cursor:pointer; margin-left:4px;">Ver mais</a>

<!-- Depois -->
<a href="javascript:void(0)" class="ver-mais" data-target="{{ c.id }}" style="color:#9B5DE5; font-weight:700; text-decoration:none; cursor:pointer; margin-left:4px; font-size:.65rem;">Ver mais</a>
```

**Linha 246 (link "Ver menos"):**
```html
<!-- Antes -->
<a href="javascript:void(0)" class="ver-menos" data-target="{{ c.id }}" style="color:#9B5DE5; font-weight:700; text-decoration:none; cursor:pointer; margin-left:4px;">Ver menos</a>

<!-- Depois -->
<a href="javascript:void(0)" class="ver-menos" data-target="{{ c.id }}" style="color:#9B5DE5; font-weight:700; text-decoration:none; cursor:pointer; margin-left:4px; font-size:.65rem;">Ver menos</a>
```

## Resultado

- ✅ O texto "Ver mais" e "Ver menos" agora aparece **menor e mais discreto**
- ✅ A quantidade de texto do resumo exibida **permanece a mesma** (150 caracteres)
- ✅ O estilo visual fica mais harmonioso com o texto do resumo (que usa `.7rem`)
- ✅ A funcionalidade de expandir/retrair o resumo continua funcionando perfeitamente

## Detalhes Técnicos

### Tamanho da Fonte
- **Resumo:** `.7rem` (0.7 × tamanho base = ~11.2px)
- **Links "Ver mais"/"Ver menos":** `.65rem` (0.65 × tamanho base = ~10.4px)
- **Resultado:** Links ligeiramente menores que o texto do resumo, criando uma hierarquia visual clara

### Propriedades Mantidas
- `color: #9B5DE5` - cor roxa característica do site
- `font-weight: 700` - negrito para destaque
- `text-decoration: none` - sem sublinhado padrão
- `cursor: pointer` - indicador visual de clicável
- `margin-left: 4px` - espaçamento adequado

## Compatibilidade

- ✅ Compatível com todos os navegadores modernos
- ✅ Mantém responsividade mobile
- ✅ Não quebra funcionalidade JavaScript existente
- ✅ Sintaxe Jinja2 validada

## Testes Realizados

1. ✅ Validação de sintaxe Jinja2
2. ✅ Verificação visual com screenshot comparativo
3. ✅ Confirmação de que arquivos desnecessários não foram commitados

## Referências

- Commit: `87faec9`
- Arquivo modificado: `gramatike_app/templates/artigos.html`
- Linhas alteradas: 242 e 246
