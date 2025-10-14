# Fix: "Falha ao salvar" ao tentar salvar resumo de Podcast

## 🐛 Problema Reportado

**Mensagem do usuário**: "está dando isso 'Falha ao salvar' ao tentar salvar o resumo"

**Exemplo de resumo que não salvava** (1090 caracteres):
> Neste texto, proponho uma abordagem de neutralização de gênero em português brasileiro na perspectiva do sistema linguístico. Para isso, parto de considerações sobre a caracterização de mudanças deliberadas e sobre os padrões de marcação e produtividade de gênero gramatical na língua. São avaliados, nessa perspectiva, quatro tipos de empregos correntes de gênero inclusivo: uso de feminino marcado no caso de substantivos comuns de dois gêneros (ex. a presidenta); emprego de formas femininas e masculinas, sobretudo em vocativos, em vez do uso genérico do masculino (ex. alunas e alunos); inclusão de novas marcas no final de nomes e adjetivos, como x e @ (ex. amigx, amig@), ou ampliação da função de marcas já existentes, como -e (ex. amigue); alteração na base de pronomes e artigos (ex. ile, le). Desses empregos, além do feminino marcado e do contraste entre formas femininas e masculinas, que já têm uso significativo na língua, proponho que, no domínio da palavra, -e encontra condições menos limitadas para expansão no sistema no subconjunto de substantivos e adjetivos sexuados.

## 🔍 Diagnóstico

### Root Cause Analysis

O formulário de edição de podcasts no dashboard administrativo estava com dois problemas críticos:

1. **Faltava o token CSRF** - O form não tinha o campo `<input type="hidden" name="csrf_token">`, necessário para validação de segurança do Flask-WTF
2. **Faltava `credentials: 'same-origin'`** - A requisição fetch não enviava os cookies de sessão, impedindo que o servidor validasse o CSRF token

### Por que não afetava outros conteúdos?

- ✅ **Artigos** (`artigos.html`): Já tinha CSRF token E credentials
- ✅ **Apostilas** (`apostilas.html`): Já tinha CSRF token E credentials  
- ❌ **Podcasts** (`admin/dashboard.html`): Faltavam ambos

### Verificações realizadas

- ✅ Campo `resumo` no banco: `VARCHAR(2000)` - suficiente para o texto de 1090 chars
- ✅ Rota `/admin/edu/content/<id>/update` requer CSRF (não tem `@csrf.exempt`)
- ✅ Resumo de exemplo tem 1090 caracteres (bem abaixo do limite de 2000)

## ✅ Solução Implementada

### Arquivo: `gramatike_app/templates/admin/dashboard.html`

**Linha 997 - Adicionado token CSRF ao formulário:**
```html
<form id="podcastEditForm" method="post">
    <h3>Editar Podcast</h3>
    <input type="hidden" name="csrf_token" value="{{ csrf_token() if csrf_token is defined else '' }}" />
    <input type="hidden" name="content_id" id="pe_id" />
    <!-- resto do form -->
</form>
```

**Linha 1108 - Adicionado `credentials: 'same-origin'` ao fetch:**
```javascript
form.addEventListener('submit', async (e)=>{
    e.preventDefault();
    const id = pe_id.value;
    const fd = new FormData(form);
    try{
        const res = await fetch(`/admin/edu/content/${id}/update`, { 
            method:'POST', 
            body: fd, 
            credentials: 'same-origin'  // ← ADICIONADO
        });
        if(res.ok){ dlg.close(); buscar(q.value.trim()); } else { alert('Falha ao salvar'); }
    }catch(err){ alert('Erro de rede'); }
});
```

## 🧪 Validação

### Testes Realizados
- ✅ Validação de sintaxe Jinja2 do template
- ✅ Verificação de que apenas 2 linhas foram modificadas
- ✅ Confirmação de que a mudança segue o padrão já aplicado em artigos.html e apostilas.html

### Como Testar em Produção

1. **Login como admin** no dashboard
2. **Navegue até a seção "Podcasts"** no menu Edu
3. **Clique em "Editar"** em algum podcast existente
4. **Adicione um resumo longo** (como o exemplo de 1090 caracteres acima)
5. **Clique em "Salvar"**
6. ✅ **Resultado esperado**: 
   - Nenhuma mensagem de erro "Falha ao salvar"
   - O diálogo deve fechar
   - A lista de podcasts deve recarregar
   - O resumo deve estar salvo ao reabrir o editor

## 📋 Resumo

| Aspecto | Detalhes |
|---------|----------|
| **Problema** | "Falha ao salvar" ao tentar salvar resumo de podcast |
| **Causa** | Falta de CSRF token e credentials no formulário de edição |
| **Solução** | Adicionados CSRF token e `credentials: 'same-origin'` |
| **Arquivo** | `gramatike_app/templates/admin/dashboard.html` |
| **Linhas** | 997 (CSRF token), 1108 (credentials) |
| **Impacto** | Mínimo - 2 linhas alteradas |
| **Status** | ✅ Corrigido |

## 🔗 Referências

- Documentação similar: `FIX_CSRF_CREDENTIALS.md` - mesmo problema em outros formulários
- Padrão aplicado: Mesmo fix já implementado em `artigos.html` e `apostilas.html`
- Issue relacionada: Artigos e apostilas tiveram o mesmo problema e foram corrigidos anteriormente

## 💡 Lições Aprendidas

1. **Sempre incluir CSRF token** em formulários que fazem POST via fetch/AJAX
2. **Sempre incluir `credentials: 'same-origin'`** para que cookies de sessão sejam enviados
3. **Validar consistência** entre diferentes seções do admin que usam padrões similares
4. **A mensagem de erro genérica** "Falha ao salvar" pode esconder problemas de CSRF
