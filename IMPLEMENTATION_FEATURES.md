# Implementação de Melhorias - Exercícios, Apostilas, Artigos e Novidades

## Resumo das Mudanças

Este documento descreve as implementações realizadas para atender às seguintes solicitações:

1. **Exercícios**: Exibir dificuldade com cores
2. **Apostilas**: Permitir publicação de links (URLs) além de PDFs
3. **Artigos**: Aumentar limite de caracteres do resumo de 1000 para 2000
4. **Novidades**: Adicionar edição, exclusão e visualização detalhada

---

## 1. Exercícios - Display de Dificuldade com Cores

### Mudanças Implementadas

#### Arquivo: `gramatike_app/templates/exercicios.html`

**Novos estilos CSS adicionados:**
```css
.dificuldade-badge { 
    display:inline-block; 
    font-size:.65rem; 
    font-weight:800; 
    letter-spacing:.5px; 
    padding:.35rem .7rem; 
    border-radius:12px; 
    margin-left:.5rem; 
    vertical-align:middle; 
}
.dificuldade-facil { 
    background:#d1f4e0; 
    color:#0a7c42; 
    border:1px solid #9de4bd; 
}
.dificuldade-media { 
    background:#fff3cd; 
    color:#856404; 
    border:1px solid #ffd966; 
}
.dificuldade-dificil { 
    background:#f8d7da; 
    color:#721c24; 
    border:1px solid #f5c6cb; 
}
```

**Badge de dificuldade adicionado:**
```html
{% if qobj.dificuldade %}
    <span class="dificuldade-badge dificuldade-{{ qobj.dificuldade }}">
        {% if qobj.dificuldade == 'facil' %}Fácil
        {% elif qobj.dificuldade == 'media' %}Média
        {% elif qobj.dificuldade == 'dificil' %}Difícil
        {% endif %}
    </span>
{% endif %}
```

### Como Funciona

- **Verde (Fácil)**: Background verde claro (#d1f4e0) com texto verde escuro (#0a7c42)
- **Amarelo (Média)**: Background amarelo claro (#fff3cd) com texto marrom (#856404)
- **Vermelho (Difícil)**: Background vermelho claro (#f8d7da) com texto vermelho escuro (#721c24)

O badge aparece ao lado do enunciado da questão, apenas se a dificuldade estiver definida.

---

## 2. Apostilas - Suporte para Links (URLs)

### Mudanças Implementadas

#### Arquivo: `gramatike_app/templates/admin/dashboard.html`

**Formulário atualizado:**
```html
<input type="file" name="pdf" accept="application/pdf" />
<input name="url" placeholder="OU insira um link (URL)" />
```

- Removido atributo `required` do campo de arquivo PDF
- Adicionado campo de URL como alternativa

#### Arquivo: `gramatike_app/routes/admin.py`

**Lógica de publicação atualizada:**
```python
# Upload de apostila (PDF ou URL)
if tipo == 'apostila':
    pdf_file = request.files.get('pdf')
    # Se forneceu URL, usa a URL
    if url_field:
        file_path = url_field
    elif pdf_file and pdf_file.filename.lower().endswith('.pdf'):
        # ... código de upload de PDF ...
```

**Mensagem de erro atualizada:**
```python
flash('É necessário enviar um arquivo PDF ou um link (URL) para apostila.')
```

### Como Funciona

1. Admin pode escolher entre:
   - Fazer upload de um PDF (comportamento anterior mantido)
   - OU inserir um link (URL) para a apostila
2. Se ambos forem fornecidos, a URL tem prioridade
3. O template de apostilas já estava preparado para exibir links, então nenhuma mudança adicional foi necessária

---

## 3. Artigos - Aumento do Limite de Caracteres do Resumo

### Mudanças Implementadas

#### Arquivo: `gramatike_app/models.py`

**Modelo EduContent atualizado:**
```python
resumo = db.Column(db.String(2000))  # Anteriormente: String(1000)
```

#### Arquivo: `gramatike_app/routes/admin.py`

**Validação atualizada:**
```python
# Validação do resumo (2000 caracteres)
if resumo and len(resumo) > 2000:
    flash(f'O resumo excede o limite de 2000 caracteres (atual: {len(resumo)} caracteres). Por favor, reduza o resumo.')
    return redirect(url_for('admin.dashboard', _anchor='edu'))
```

#### Arquivo: `migrations/versions/i8j9k0l1m2n3_increase_resumo_to_2000.py`

**Nova migração criada:**
```python
def upgrade():
    # Increase resumo field from VARCHAR(1000) to VARCHAR(2000)
    op.alter_column('edu_content', 'resumo',
                    existing_type=sa.String(length=1000),
                    type_=sa.String(length=2000),
                    existing_nullable=True)

def downgrade():
    # Revert resumo field back to VARCHAR(1000)
    op.alter_column('edu_content', 'resumo',
                    existing_type=sa.String(length=2000),
                    type_=sa.String(length=1000),
                    existing_nullable=True)
```

### Como Aplicar

Execute a migração no servidor de produção:
```bash
flask db upgrade
```

---

## 4. Novidades - CRUD Completo e Visualização Detalhada

### Mudanças Implementadas

#### Arquivo: `gramatike_app/routes/admin.py`

**Nova rota de edição adicionada:**
```python
@admin_bp.route('/novidades/<int:nid>/edit', methods=['POST'])
@login_required
def novidades_edit(nid):
    if not getattr(current_user, 'is_admin', False):
        return redirect(url_for('main.index'))
    n = EduNovidade.query.get_or_404(nid)
    n.titulo = (request.form.get('titulo') or '').strip()
    n.descricao = (request.form.get('descricao') or '').strip() or None
    n.link = (request.form.get('link') or '').strip() or None
    if not n.titulo:
        flash('Título é obrigatório para novidade.')
        return redirect(url_for('admin.dashboard', _anchor='gramatike'))
    db.session.commit()
    flash('Novidade atualizada.')
    return redirect(url_for('admin.dashboard', _anchor='gramatike'))
```

#### Arquivo: `gramatike_app/routes/__init__.py`

**Nova rota de visualização detalhada:**
```python
@bp.route('/novidade/<int:novidade_id>')
def novidade_detail(novidade_id):
    n = EduNovidade.query.get_or_404(novidade_id)
    is_admin = getattr(current_user, 'is_authenticated', False) and (
        getattr(current_user, 'is_admin', False) or 
        getattr(current_user, 'is_superadmin', False)
    )
    return render_template('novidade_detail.html', novidade=n, is_admin=is_admin)
```

**API atualizada para usar URLs de detalhe:**
```python
items.append({
    'id': f"nov-{n.id}",
    'title': (n.titulo[:60] + '…') if len(n.titulo) > 60 else n.titulo,
    'snippet': snippet,
    'tags': [],
    'url': url_for('main.novidade_detail', novidade_id=n.id),  # Link para página de detalhe
    'created_at': n.created_at.isoformat() if n.created_at else None,
    'source': 'novidade'
})
```

#### Arquivo: `gramatike_app/templates/novidade_detail.html` (NOVO)

**Template criado com:**
- Design estilo blog/jornal
- Exibição de título, data, autor e descrição
- Link para o conteúdo externo (se disponível)
- Botões de editar e excluir (apenas para admins)
- Modal de edição integrado
- Navegação de volta para o início

### Funcionalidades

1. **Visualização**: Ao clicar em uma novidade no feed, o usuário é direcionado para `/novidade/<id>`
2. **Edição**: Admins veem um botão "Editar" que abre um modal com o formulário de edição
3. **Exclusão**: Admins veem um botão "Excluir" com confirmação
4. **Design**: Estilo consistente com o restante do Gramátike Edu (cores roxas, bordas arredondadas)

---

## Resumo de Arquivos Modificados

### Arquivos Modificados:
1. `gramatike_app/models.py` - Aumentado campo resumo para 2000 caracteres
2. `gramatike_app/routes/admin.py` - Adicionada rota de edição de novidades e atualizada lógica de apostilas
3. `gramatike_app/routes/__init__.py` - Adicionada rota de detalhe de novidades
4. `gramatike_app/templates/exercicios.html` - Adicionados badges de dificuldade com cores
5. `gramatike_app/templates/admin/dashboard.html` - Atualizado formulário de apostilas

### Arquivos Criados:
1. `gramatike_app/templates/novidade_detail.html` - Página de visualização detalhada de novidades
2. `migrations/versions/i8j9k0l1m2n3_increase_resumo_to_2000.py` - Migração para aumentar campo resumo

---

## Instruções de Deploy

1. **Aplicar migração do banco de dados:**
   ```bash
   flask db upgrade
   ```

2. **Reiniciar a aplicação** para carregar as mudanças de código

3. **Verificar funcionalidades:**
   - Exercícios exibem badges de dificuldade coloridos
   - Apostilas podem ser publicadas com URL em vez de PDF
   - Artigos aceitam resumos de até 2000 caracteres
   - Novidades são clicáveis e exibem página de detalhe
   - Admins podem editar e excluir novidades

---

## Considerações de Compatibilidade

- **Exercícios**: Questões sem dificuldade definida não exibem badge (retrocompatível)
- **Apostilas**: Apostilas existentes com PDF continuam funcionando normalmente
- **Artigos**: Resumos com menos de 2000 caracteres continuam válidos
- **Novidades**: Novidades existentes funcionam com a nova visualização detalhada

---

## Próximos Passos (Opcionais)

1. Adicionar filtro de exercícios por dificuldade
2. Adicionar pré-visualização de PDFs externos em apostilas
3. Adicionar indicador visual no admin dashboard para novidades com/sem link
4. Implementar busca avançada nas novidades
