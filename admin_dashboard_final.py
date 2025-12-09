
# ========== Admin Dashboard Helpers ==========

def escape_html(text):
    """Escapa HTML para prevenir XSS"""
    if not text:
        return ""
    return (str(text)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#x27;"))

def build_users_table_rows(all_users, limit=100):
    """Constrói linhas da tabela de usuáries"""
    rows = ""
    for user in (all_users[:limit] if len(all_users) > limit else all_users):
        user_id = user.get('id', 0)
        username = escape_html(user.get('username', ''))
        email = escape_html(user.get('email', ''))
        is_admin = user.get('is_admin', False)
        is_superadmin = user.get('is_superadmin', False)
        is_banned = user.get('is_banned', False)
        
        badge = ""
        if is_superadmin:
            badge = '<span class="badge badge-superadmin">SUPERADMIN</span>'
        elif is_admin:
            badge = '<span class="badge badge-admin">ADMIN</span>'
        elif is_banned:
            badge = '<span class="badge" style="background:#f44;color:#fff;">BANIDO</span>'
        
        rows += f"""
        <tr>
            <td data-label="ID">{user_id}</td>
            <td data-label="Username">{username}</td>
            <td data-label="Email">{email}</td>
            <td data-label="Status">{badge}</td>
            <td data-label="Ações" class="actions-stack">
                <form method="POST" action="/admin/users/{user_id}/promote" class="inline">
                    <button type="submit" class="action-btn">Promover</button>
                </form>
                <form method="POST" action="/admin/users/{user_id}/ban" class="inline">
                    <button type="submit" class="action-btn danger">Banir</button>
                </form>
                <form method="POST" action="/admin/users/{user_id}/delete" class="inline" onsubmit="return confirm('Excluir?')">
                    <button type="submit" class="action-btn danger">Deletar</button>
                </form>
            </td>
        </tr>
        """
    
    return rows

def build_edu_topics_list(topics, area_filter=None):
    """Constrói lista de tópicos educacionais"""
    filtered = [t for t in topics if not area_filter or t.get('area') == area_filter]
    
    if not filtered:
        return '<p class="muted-inline">Nenhum tópico criado ainda.</p>'
    
    html = '<div style="display:grid; gap:.8rem; grid-template-columns:1fr;">'
    for topic in filtered:
        topic_id = topic.get('id', 0)
        nome = escape_html(topic.get('nome', ''))
        descricao = escape_html(topic.get('descricao', ''))
        
        html += f"""
        <div style="background:#f9fbfd; border:1px solid #e3e9f0; border-radius:12px; padding:.9rem;">
            <div style="display:flex; justify-content:space-between; align-items:start; gap:.8rem;">
                <div style="flex:1;">
                    <div style="font-weight:700; font-size:.85rem; color:#333;">{nome}</div>
                    {"<div style='font-size:.7rem; color:#666;'>" + descricao + "</div>" if descricao else ""}
                </div>
                <button onclick="toggleTopicEdit('{area_filter}-{topic_id}')" class="action-btn" style="font-size:.6rem;">
                    Editar
                </button>
            </div>
            <div id="topic-edit-{area_filter}-{topic_id}" style="display:none; margin-top:.8rem; padding-top:.8rem; border-top:1px solid #e3e9f0;">
                <form method="POST" action="/admin/edu/topics/{topic_id}/update">
                    <input name="nome" value="{nome}" required style="width:100%; padding:.5rem; margin-bottom:.5rem; border:1px solid #cfd7e2; border-radius:8px;">
                    <textarea name="descricao" style="width:100%; padding:.5rem; margin-bottom:.5rem; border:1px solid #cfd7e2; border-radius:8px; min-height:60px;">{descricao}</textarea>
                    <button type="submit" class="action-btn">Salvar</button>
                    <button type="button" onclick="toggleTopicEdit('{area_filter}-{topic_id}')" class="action-btn">Cancelar</button>
                </form>
            </div>
        </div>
        """
    
    html += '</div>'
    return html

def build_divulgacoes_list(divulgacoes):
    """Constrói lista de divulgações"""
    if not divulgacoes:
        return '<p class="small-muted">Nenhuma divulgação cadastrada.</p>'
    
    html = '<div style="display:grid; gap:1rem; grid-template-columns:1fr;">'
    for div in divulgacoes:
        div_id = div.get('id', 0)
        titulo = escape_html(div.get('titulo', ''))
        texto = escape_html(div.get('texto', ''))
        link = escape_html(div.get('link', ''))
        ativa = div.get('ativa', False)
        
        status_class = ' promo-active' if ativa else ''
        
        html += f"""
        <div class="card{status_class}">
            <h4>{titulo}</h4>
            <p class="small-muted">{texto}</p>
            <div style="margin-top:.8rem; display:flex; gap:.4rem;">
                <form method="POST" action="/admin/divulgacoes/{div_id}/toggle" class="inline">
                    <button type="submit" class="action-btn">{"Desativar" if ativa else "Ativar"}</button>
                </form>
                <button class="action-btn" onclick="editDivulgacao({div_id})">Editar</button>
                <form method="POST" action="/admin/divulgacoes/{div_id}/delete" class="inline" onsubmit="return confirm('Excluir?')">
                    <button type="submit" class="action-btn danger">Excluir</button>
                </form>
            </div>
        </div>
        """
    
    html += '</div>'
    return html

# ========== Fim dos Helpers ==========



# Constantes do Admin Dashboard - AUTO-GERADAS

ADMIN_CSS = """
:root {
            --bg: #f5f7fb;
            --bg-alt:#ffffff;
            --border:#dbe2ea;
            --border-strong:#c2ccd8;
            --text:#2b3542;
            --text-soft:#5b6a7c;
            --accent:#9B5DE5;
            --accent-hover:#7d3dc9;
            --danger:#eb5757;
            --danger-hover:#d04444;
            --warn:#f5a540;
            --radius:16px;
            --shadow-sm:0 1px 2px rgba(0,0,0,.06),0 0 0 1px rgba(0,0,0,.04);
            --shadow:0 4px 10px -2px rgba(30,41,59,.08),0 2px 4px rgba(30,41,59,.06);
            --grad:linear-gradient(120deg,#9B5DE5,#b896e8 55%,#d8b5f0);
        }
        .dark {
            --bg:#0e1621; --bg-alt:#172231; --border:#253242; --border-strong:#334355; --text:#f5f8fc; --text-soft:#a3b2c2;
            --accent:#9B5DE5; --accent-hover:#7d3dc9; --danger:#ff6b6b; --danger-hover:#e24f4f; --warn:#ffb347; --grad:linear-gradient(120deg,#7d3dc9,#8a5dd4 55%,#9B5DE5);
            --shadow-sm:0 1px 2px rgba(0,0,0,.4),0 0 0 1px rgba(255,255,255,.04);
            --shadow:0 4px 18px -4px rgba(0,0,0,.5),0 2px 6px rgba(0,0,0,.45);
        }
    html,body { margin:0; padding:0; font-family:'Nunito', system-ui, -apple-system, "Segoe UI", Roboto, Arial, sans-serif !important; background:var(--bg); color:var(--text); -webkit-font-smoothing:antialiased; }
        body { min-height:100vh; display:flex; flex-direction:column; }
    /* Permite que o conteúdo (main) expanda e empurre o footer para o final da tela mesmo quando houver pouco conteúdo */
        main { flex:1; display:flex; flex-direction:column; }
    /* ===== Cabeçalho unificado (igual páginas públicas) ===== */
    header.site-head { background:#333; padding:28px clamp(16px,4vw,40px) 46px; border-bottom-left-radius:40px; border-bottom-right-radius:40px; position:relative; display:flex; flex-direction:column; align-items:center; text-align:center; }
    /* Mobile: Header mais compacto */
    @media (max-width: 900px){ 
      header.site-head { padding:18px clamp(12px,3vw,24px) 28px; }
      .logo { font-size:1.8rem !important; }
    }
    .logo { font-family:'Mansalva', cursive; font-size:2.6rem; color:#fff; letter-spacing:1px; font-weight:400; margin:0; text-shadow:0 2px 6px rgba(0,0,0,.35); }
    .admin-badge { position:absolute; top:16px; left:16px; background:#444; border:1px solid #555; color:#fff; padding:6px 12px; font-size:.55rem; font-weight:800; letter-spacing:.6px; border-radius:10px; text-transform:uppercase; box-shadow:0 4px 10px -2px rgba(0,0,0,.4); }
    /* Pills em modo escuro/cinza */
    .tabs { margin-top:1.1rem; display:flex; flex-wrap:wrap; gap:.65rem; justify-content:center; border:none; padding:0; }
    .tab-link { text-decoration:none; font-weight:700; font-size:.7rem; letter-spacing:.55px; padding:.65rem 1.05rem .62rem; background:#ffffff14; color:#fff; border:1px solid #ffffff25; backdrop-filter:blur(4px); -webkit-backdrop-filter:blur(4px); border-radius:22px; display:inline-flex; align-items:center; gap:.35rem; box-shadow:0 2px 6px rgba(0,0,0,.28); transition:.25s; position:static; top:0; }
    .tab-link:hover { background:#555; color:#fff; }
    .tab-link.active { background:#fff; color:#333; box-shadow:0 6px 18px -4px rgba(0,0,0,.55); }
    /* Mobile: Smaller tabs, keep in same line */
    @media (max-width: 900px){ 
      .tabs { gap:.4rem; margin-top:.8rem; padding:0 12px; }
      .tab-link { font-size:.6rem; padding:.5rem .75rem .48rem; letter-spacing:.4px; }
    }
    /* Back button styling */
    .back-btn:hover { background:#ffffff33 !important; }
    /* (Removido hack que ocultava header) */
        /* Footer unificado */
    /* Footer cola no final: margin-top:auto garante posicionamento inferior quando o conteúdo é curto */
    .footer-bar { background:#333; color:#fff; text-align:center; padding:1.1rem 0 1.1rem; font-size:1rem; border-top-left-radius:32px; border-top-right-radius:32px; margin-top:auto; letter-spacing:.5px; }
        @media (max-width:900px){ .top-bar { min-height:100px; padding-bottom:1.4rem; } .top-bar h1 { font-size:1.55rem; padding-top:1.3rem; } .footer-bar { font-size:.9rem; } }
        /* Cards */
        .cards-grid { display:grid; gap:1rem; grid-template-columns:repeat(auto-fill,minmax(260px,1fr)); }
        .card { background:var(--bg-alt); border:1px solid var(--border); border-radius:var(--radius); padding:1.05rem 1rem 1.25rem; box-shadow:var(--shadow-sm); position:relative; overflow:hidden; }
        .card:before { content:""; position:absolute; inset:0; background:linear-gradient(140deg,rgba(255,255,255,.06),transparent 35%); pointer-events:none; }
        .card h4 { margin:.2rem 0 .65rem; font-size:.82rem; letter-spacing:.5px; font-weight:600; }
        .small-muted { font-size:.63rem; color:var(--text-soft); letter-spacing:.4px; }
        /* Form inline */
        .inline-form { display:flex; gap:.55rem; flex-wrap:wrap; }
        .inline-form input, .inline-form textarea { padding:.55rem .7rem; border:1px solid var(--border-strong); border-radius:9px; font-size:.72rem; flex:1; background:var(--bg); color:var(--text); }
        .inline-form textarea { min-height:90px; resize:vertical; }
        .inline-form button { padding:.55rem 1rem; background:var(--accent); color:#fff; font-weight:600; border:none; border-radius:9px; cursor:pointer; font-size:.7rem; letter-spacing:.5px; box-shadow:var(--shadow-sm); }
        .inline-form button:hover { background:var(--accent-hover); }
        /* Table */
        table.admin-usuaries { width:100%; border-collapse:separate; border-spacing:0; font-size:0.74rem; overflow:hidden; border:1px solid var(--border); border-radius:18px; box-shadow:var(--shadow-sm); }
        table.admin-usuaries th, table.admin-usuaries td { padding:9px 12px; text-align:left; }
        table.admin-usuaries thead th { background:var(--bg-alt); position:sticky; top:0; z-index:1; font-weight:600; font-size:.68rem; letter-spacing:.7px; text-transform:uppercase; color:var(--text-soft); border-bottom:1px solid var(--border); }
        table.admin-usuaries tbody tr { border-bottom:1px solid var(--border); transition:.25s; }
        table.admin-usuaries tbody tr:last-child { border-bottom:none; }
        table.admin-usuaries tbody tr:hover { background:rgba(0,0,0,.03); }
        .badge { display:inline-block; padding:3px 8px 4px; border-radius:14px; font-size:0.55rem; font-weight:600; letter-spacing:.6px; background:var(--bg); color:var(--text-soft); text-transform:uppercase; box-shadow:inset 0 0 0 1px var(--border); }
        .badge-admin { background:var(--accent); color:#fff; box-shadow:none; }
        .badge-superadmin { background:linear-gradient(120deg,#ffb347,#ff6b6b); color:#fff; box-shadow:none; }
        /* Buttons */
        form.inline { display:inline; margin:0; }
        .actions-stack { display:flex; flex-wrap:wrap; gap:.4rem .35rem; max-width:320px; }
        button.action-btn { cursor:pointer; background:var(--bg-alt); border:1px solid var(--border-strong); padding:4px 10px 5px; border-radius:7px; font-size:0.58rem; font-weight:600; letter-spacing:.55px; color:var(--text-soft); display:inline-flex; gap:.35rem; align-items:center; transition:.25s; position:relative; }
        button.action-btn:hover { background:var(--accent); color:#fff; border-color:var(--accent); }
        button.action-btn.danger:hover { background:var(--danger); border-color:var(--danger); }
        button.action-btn.danger { border-color:var(--danger); color:var(--danger); }
        .muted { color:var(--text-soft); font-size:0.62rem; }
    /* Gramátike (antigo Delu) reports table override smaller font */
    #tab-gramatike table.admin-usuaries { font-size:.66rem; }
    #tab-gramatike table.admin-usuaries th { font-size:.55rem; }
        /* ===== Fim das alterações ===== */
    /* Avisos rápidos (Publi) */
    .publi-aviso-form { display:flex; flex-direction:column; gap:.55rem; }
    .publi-aviso-form .lbl { font-size:.55rem; font-weight:800; letter-spacing:.6px; text-transform:uppercase; color:var(--text-soft); }
    .publi-aviso-form input, .publi-aviso-form textarea { background:var(--bg); border:1px solid var(--border-strong); border-radius:8px; padding:.55rem .65rem; font-size:.7rem; font-weight:600; }
    .publi-aviso-form textarea { min-height:90px; resize:vertical; }
    .publi-aviso-form .btn-add-aviso { align-self:flex-start; background:var(--accent); border:none; color:#fff; font-weight:700; padding:.55rem 1.05rem; border-radius:8px; cursor:pointer; font-size:.65rem; letter-spacing:.5px; box-shadow:var(--shadow-sm); }
    .publi-aviso-form .btn-add-aviso:hover { background:var(--accent-hover); }
    .lista-avisos, .lista-avisos-vazia { margin-top:.9rem; display:flex; flex-direction:column; gap:.6rem; }
    .aviso-item { background:var(--bg-alt); border:1px solid var(--border); border-radius:12px; padding:.65rem .75rem .7rem; box-shadow:var(--shadow-sm); position:relative; }
    .aviso-item:before { content:""; position:absolute; inset:0; background:linear-gradient(130deg,rgba(255,255,255,.5),transparent 60%); pointer-events:none; border-radius:inherit; }
    .aviso-head { display:flex; justify-content:space-between; align-items:center; gap:1rem; }
    .aviso-head strong { font-size:.7rem; letter-spacing:.4px; }
    .aviso-head time { font-size:.5rem; color:var(--text-soft); font-weight:600; letter-spacing:.4px; }
    .aviso-item p { margin:.35rem 0 0; font-size:.6rem; line-height:1.3; color:var(--text-soft); font-weight:600; }
    .promo-active { background:#4caf50 !important; color:#fff !important; border-color:#4caf50 !important; }
        /* Pagination buttons */
        .pag-btn { padding:.55rem .9rem; border-radius:18px; background:var(--accent); color:#fff; text-decoration:none; display:inline-block; font-weight:600; font-size:.7rem; letter-spacing:.3px; }
        .pag-btn.disabled { pointer-events:none; opacity:.45; }
        .pag-btn:hover { background:var(--accent-hover); }
        /* Responsive */
        @media (max-width:880px){
            header h1 { font-size:1.05rem; }
            table.admin-usuaries thead { display:none; }
            table.admin-usuaries, table.admin-usuaries tbody, table.admin-usuaries tr, table.admin-usuaries td { display:block; width:100%; }
            table.admin-usuaries tr { margin:0 0 .75rem; background:var(--bg-alt); border:1px solid var(--border); border-radius:14px; padding:.4rem .6rem .55rem; }
            table.admin-usuaries td { border:none !important; padding:5px 4px; font-size:.68rem; }
            table.admin-usuaries td::before { content:attr(data-label); display:block; font-weight:600; font-size:.55rem; text-transform:uppercase; letter-spacing:.5px; color:var(--text-soft); margin-bottom:1px; }
            .actions-stack { max-width:100%; }
        }
.tabs { display:flex; gap:.6rem; border-bottom:2px solid #e3e8ef; margin-bottom:1.2rem; flex-wrap:wrap; }
            .tab-link { padding:.65rem 1rem; border:1px solid #d4dde7; background:#fafbfc; border-radius:10px 10px 0 0; text-decoration:none; font-size:.85rem; font-weight:600; color:#425269; position:relative; top:2px; transition:.25s; }
            .tab-link.active { background:#ffffff; border-bottom-color:#ffffff; box-shadow:0 -2px 6px rgba(0,0,0,0.04); color:#1f2d40; }
            .tab-link:hover { background:#f0f5fa; }
            section.tab-panel { display:none; animation: fade .35s ease; }
            section.tab-panel.active { display:block; }
            @keyframes fade { from{opacity:0; transform:translateY(6px);} to{opacity:1; transform:translateY(0);} }
            table.admin-usuaries { width:100%; border-collapse: collapse; font-size:0.95rem; }
            table.admin-usuaries th, table.admin-usuaries td { padding:8px 10px; border:1px solid #e2e6eb; text-align:left; }
            table.admin-usuaries th { background:#f5f7fa; }
            .badge { display:inline-block; padding:2px 8px; border-radius:12px; font-size:0.58rem; font-weight:600; letter-spacing:.5px; }
            .badge-admin { background:#9B5DE5; color:#fff; }
            .badge-superadmin { background:linear-gradient(120deg,#ffb347,#ff6b6b); color:#fff; box-shadow:0 0 0 1px #ffa540 inset; }
            form.inline { display:inline; margin:0; }
            button.action-btn { cursor:pointer; background:#ffffff; border:1px solid #cfd7e2; padding:4px 10px; border-radius:6px; font-size:0.65rem; font-weight:600; letter-spacing:.5px; transition:.25s; }
            button.action-btn:hover { background:#f0f6ff; border-color:#9bb9ee; }
            button.action-btn.danger:hover { background:#ffecec; border-color:#f5a2a2; }
            button.action-btn.danger { border-color:#e7b1b1; }
            .muted { color:#777; font-size:0.7rem; }
            .cards-grid { display:grid; gap:1rem; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); }
            .card { background:#fff; border:1px solid #e5ebf2; border-radius:14px; padding:1rem 1rem 1.15rem; box-shadow:0 2px 4px rgba(0,0,0,.04); position:relative; }
            .card h4 { margin:.2rem 0 .6rem; font-size:.9rem; }
            .small-muted { font-size:.65rem; color:#768396; letter-spacing:.4px; }
            .inline-form { display:flex; gap:.55rem; flex-wrap:wrap; }
            .inline-form input, .inline-form textarea { padding:.55rem .7rem; border:1px solid #cfd7e2; border-radius:8px; font-size:.75rem; flex:1; }
            .inline-form textarea { min-height:90px; resize:vertical; }
            .inline-form button { padding:.55rem 1rem; background:#9B5DE5; color:#fff; font-weight:600; border:none; border-radius:8px; cursor:pointer; font-size:.72rem; }
            .inline-form button:hover { background:#7d3dc9; }
.edu-area-btn { background:#fff; border:1px solid #d1dae5; padding:.45rem .85rem; border-radius:8px; font-size:.7rem; cursor:pointer; font-weight:600; letter-spacing:.4px; }
                .edu-area-btn.active { background:#9B5DE5; color:#fff; border-color:#9B5DE5; }
                .edu-area-section { display:none; animation:fade .3s ease; }
                .edu-area-section.active { display:block; }
                .edu-two-col { display:grid; gap:1rem; grid-template-columns:repeat(auto-fit,minmax(300px,1fr)); }
                .edu-box { background:#fff; border:1px solid #e3e9f0; border-radius:14px; padding:1rem .95rem 1.1rem; box-shadow:0 2px 4px rgba(0,0,0,.04); }
                .edu-box h3 { margin:.1rem 0 .7rem; font-size:.9rem; }
                .edu-box form { display:flex; flex-direction:column; gap:.5rem; }
                .edu-box input, .edu-box textarea, .edu-box select { padding:.55rem .6rem; border:1px solid #cfd7e2; border-radius:8px; font-size:.72rem; background:#f9fbfd; }
                .edu-box textarea { min-height:150px; resize:vertical; }
                .edu-box button { padding:.55rem .9rem; border:none; background:#9B5DE5; color:#fff; font-weight:600; border-radius:8px; font-size:.7rem; cursor:pointer; }
                .edu-box button:hover { background:#7d3dc9; }
                .muted-inline { font-size:.6rem; color:#6b7785; margin-top:-.3rem; }
                /* Quill editor styles for dashboard */
                #novidade-editor-container { min-height:200px; background:#fff; border:1px solid #cfd7e2; border-radius:8px; }
                .ql-toolbar.ql-snow { border-top-left-radius:8px; border-top-right-radius:8px; background:#f9fafb; }
                .ql-container.ql-snow { border-bottom-left-radius:8px; border-bottom-right-radius:8px; font-size:.72rem; }
/* Container interno para afastar conteúdo das bordas laterais */
            .admin-main-wrap { padding:0 clamp(20px,5vw,70px) 0; }
            .tab-panel > *:first-child { margin-top:0; }
            /* Ajusta espaçamento vertical inicial de cada painel */
            .tab-panel { padding-top:.4rem; }
            @media (max-width:820px){ .admin-main-wrap { padding:0 20px 0; } }
"""

GERAL_TAB_HTML = f"""
<h2 style="margin-top:0;">Usuáries</h2>
            <div class="card" style="margin:0 0 1rem; display:flex; flex-direction:column; gap:.6rem;">
                <h4>Promover a Admin</h4>
                <form method="POST" action="/admin/promover_admin" class="inline-form" style="align-items:flex-end;">
                    
                    <div style="flex:1; min-width:220px;">
                        <label style="display:block; font-size:.6rem; font-weight:600; letter-spacing:.5px; text-transform:uppercase; margin:0 0 4px; color:var(--text-soft);">Username ou Email</label>
                        <input name="ident" placeholder="ex: alex ou pessoa@dominio" required />
                    </div>
                    <button type="submit">Promover</button>
                </form>
            </div>
            <div class="card" style="margin:0 0 1rem;">
                <h4>Moderação — Palavras bloqueadas</h4>
                <form method="POST" action="/admin/add_blocked_word" class="inline-form" style="align-items:flex-end; gap:.6rem;">
                    
                    <div style="flex:2; min-width:220px;">
                        <label style="display:block; font-size:.6rem; font-weight:700; letter-spacing:.5px; text-transform:uppercase; margin:0 0 4px; color:var(--text-soft);">Termo</label>
                        <input name="term" placeholder="palavra ou expressão" required />
                    </div>
                    <div style="flex:1; min-width:160px;">
                        <label style="display:block; font-size:.6rem; font-weight:700; letter-spacing:.5px; text-transform:uppercase; margin:0 0 4px; color:var(--text-soft);">Categoria</label>
                        <select name="category">
                            <option value="custom">Custom</option>
                            <option value="profanity">Xingamento</option>
                            <option value="hate">Ódio/Discriminação</option>
                            <option value="nudity">Nudez/Sexual</option>
                        </select>
                    </div>
                    <button type="submit">Adicionar</button>
                </form>
                <div style="margin-top:.8rem;">
                    
blocked_words_html = ""
if blocked_words:
    blocked_words_html = f"""
<table class="admin-usuaries" style="font-size:.72rem;">
                            <thead>
                                <tr>
                                    <th style="width:55%">Termo</th>
                                    <th style="width:20%">Categoria</th>
                                    <th style="width:15%">Criado em</th>
                                    <th style="width:10%">Ações</th>
                                </tr>
                            </thead>
                            <tbody>
                                
blocked_words_html = ""
for bw in blocked_words:
    blocked_words_html += f"""
<tr>
                                    <td data-label="Termo">{bw.term}</td>
                                    <td data-label="Categoria">{{ bw.category|capitalize }}</td>
                                    <td data-label="Criado em">{{ bw.created_at.strftime('%d/%m/%Y %H:%M') if bw.created_at else '-' }}</td>
                                    <td data-label="Ações">
                                        <form class="inline" method="POST" action="/admin/delete_blocked_word/{bw.id}" onsubmit="return confirm('Remover termo bloqueado?');">
                                            
                                            <button type="submit" class="action-btn danger">Excluir</button>
                                        </form>
                                    </td>
                                </tr>
    """
{blocked_words_html}

                            </tbody>
                        </table>
                        <!-- IF blocked_words_pagination and blocked_words_pagination.pages > 1 START -->
                        <div class="pagination" style="margin-top:1rem; display:flex; gap:.4rem; justify-content:center; align-items:center; flex-wrap:wrap; font-size:.7rem;">
                            <!-- IF blocked_words_pagination.has_prev START -->
                                <a href="/admin/dashboard/{'geral', moderation_page=blocked_words_pagination.prev_num}" class="pag-btn">← Anterior</a>
    """
{blocked_words_html}

                            {% for page_num in range(1, blocked_words_pagination.pages + 1) %}
                                
if page_num == blocked_words_pagination.page:
    page_num_html = f"""
<span class="pag-btn disabled" style="background:var(--accent); color:#fff;">{page_num}</span>
    """
else:
    page_num_html = f"""
<a href="/admin/dashboard/{'geral', moderation_page=page_num}" class="pag-btn">{page_num}</a>
    """
{page_num_html}

                            <!-- FOR END -->
                            
blocked_words_pagination_html = ""
if blocked_words_pagination.has_next:
    blocked_words_pagination_html = f"""
<a href="/admin/dashboard/{'geral', moderation_page=blocked_words_pagination.next_num}" class="pag-btn">Próximo →</a>
    """
{blocked_words_pagination_html}

                        </div>
                        
END_html = ""
if END -->
                    <!-- ELSE -->
                        <p class="small-muted" style="margin:0;">Nenhum termo personalizado cadastrado.</p>
                    <!-- IF END -->
                </div>
            </div>
            <table class="admin-usuaries" role="grid" aria-describedby="legenda-usuaries">
                <thead>
                    <tr><th>ID</th><th>Username</th><th>Email</th><th>Privilégios</th><th>Ações</th></tr>
                </thead>
                <tbody>
                
usuaries_html = ""
for u in usuaries:
    usuaries_html += f"""
<tr>
                        <td data-label="ID">{u.id}</td>
                        <td data-label="Username">{u.username} <!-- IF u.is_superadmin:
    END_html = f"""
<span class="badge badge-superadmin">SUPERADMIN</span><!-- ELIF u.is_admin --><span class="badge badge-admin">ADMIN</span>
    """
{END_html}
</td>
                        <td data-label="Email">{u.email}</td>
                        <td data-label="Privilégios">
                            
if u.is_superadmin:
    u_html = f"""
Superadmin<!-- ELIF u.is_admin -->Admin
    """
else:
    u_html = f"""
<span class="muted">Padrão</span>
    """
{u_html}

                            
u_html = ""
if u.is_banned:
    u_html = f"""
<br><span class="badge" style="background:#222;color:#fff;">BANIDO</span><!-- ELIF u.suspended_until and u.suspended_until > now --><br><span class="badge" style="background:#f5a540;color:#fff;">SUSPENSO</span>
    """
{u_html}

                        </td>
                        <td data-label="Ações">
                            
if not u.is_superadmin:
    not_html = f"""
<div class="actions-stack">
                                    <form class="inline" method="POST" action="/main/gerenciar_usuaries">
                                        
                                        <input type="hidden" name="user_id" value="{u.id}" />
                                        <button type="submit" class="action-btn"><!-- IF u.is_admin START -->Remover Admin
    """
else:
    not_html = f"""
Tornar Admin
    """
{not_html}
</button>
                                    </form>
                                    
if u.is_banned:
    u_html = f"""
<form class="inline" method="POST" action="/admin/unban_user/{u.id}">
                                            
                                            <button type="submit" class="action-btn">Desbanir</button>
                                        </form>
    """
else:
    u_html = f"""
<form class="inline" method="POST" action="/admin/ban_user/{u.id}">
                                            
                                            <input type="hidden" name="reason" value="Violação de regras" />
                                            <button type="submit" class="action-btn danger">Banir</button>
                                        </form>
    """
{u_html}

                                    
if u.suspended_until and u.suspended_until > now:
    u_html = f"""
<form class="inline" method="POST" action="/admin/unsuspend_user/{u.id}">
                                            
                                            <button type="submit" class="action-btn">Remover Susp.</button>
                                        </form>
    """
else:
    u_html = f"""
<form class="inline" method="POST" action="/admin/suspend_user/{u.id}">
                                            
                                            <input style="width:48px" name="hours" placeholder="h" />
                                            <button type="submit" class="action-btn">Suspender</button>
                                        </form>
    """
{u_html}

                                    
u_html = ""
if u.id != current_user.id:
    u_html = f"""
<form class="inline" method="POST" action="/admin/excluir_usuarie/{u.id}" onsubmit="return confirm('Excluir {u.username}?');">
                                        
                                        <button type="submit" class="action-btn danger">Excluir</button>
                                    </form>
    """
{u_html}

                                </div>
                            <!-- ELSE --><span class="muted">Protegide</span>
END_html = ""
if END -->
                        </td>
                    </tr>
    """
{usuaries_html}

                </tbody>
            </table>
            <!-- IF users_pagination:
    END_html = f"""
<div class="pagination" style="margin-top:1rem; display:flex; gap:.4rem; justify-content:center; align-items:center; flex-wrap:wrap; font-size:.7rem;">
                <!-- IF users_pagination.has_prev START -->
                <a href="/admin/dashboard/{users_pagination.prev_num, _anchor='geral'}" class="pag-btn">← Anterior</a>
    """
{END_html}

                {% for page_num in range(1, users_pagination.pages + 1) %}
                    
if page_num == users_pagination.page:
    page_num_html = f"""
<span class="pag-btn disabled" style="background:var(--accent); color:#fff;">{page_num}</span>
    """
else:
    page_num_html = f"""
<a href="/admin/dashboard/{page_num, _anchor='geral'}" class="pag-btn">{page_num}</a>
    """
{page_num_html}

                <!-- FOR END -->
                
users_pagination_html = ""
if users_pagination.has_next:
    users_pagination_html = f"""
<a href="/admin/dashboard/{users_pagination.next_num, _anchor='geral'}" class="pag-btn">Próxima →</a>
    """
{users_pagination_html}

            </div>
            
END_html = ""
if END -->
"""

ANALYTICS_TAB_HTML = f"""
<h2 style="margin-top:0;">Analytics</h2>
            <div style="display:grid; gap:1rem; grid-template-columns:repeat(auto-fit,minmax(300px,1fr));">
                <div class="card" style="margin:0;">
                    <h4>Crescimento de Usuáries</h4>
                    <canvas id="usersChart" height="120" style="width:100%;"></canvas>
                </div>
                <div class="card" style="margin:0;">
                    <h4>Criação de Conteúdo Edu</h4>
                    <canvas id="contentChart" height="120" style="width:100%;"></canvas>
                </div>
            </div>
            <div style="display:grid; gap:1rem; grid-template-columns:repeat(auto-fit,minmax(280px,1fr)); margin-top:1rem;">
                <div class="card" style="margin:0;">
                    <h4>Posts Criados (últimos 7 dias)</h4>
                    <canvas id="postsChart" height="100" style="width:100%;"></canvas>
                </div>
                <div class="card" style="margin:0;">
                    <h4>Atividade por Tipo</h4>
                    <canvas id="activityChart" height="100" style="width:100%;"></canvas>
                </div>
            </div>
"""

PUBLI_TAB_HTML = f"""
<h2 style="margin-top:0;">Publi / Divulgação</h2>
            <div class="cards-grid" style="grid-template-columns:repeat(auto-fit,minmax(300px,1fr));">
                <div class="card">
                    <h4 style="margin:0 0 .8rem; font-size:.85rem; letter-spacing:.5px;">Nova Divulgação</h4>
                    <form method="POST" action="/main/admin_divulgacao_new" class="publi-aviso-form" style="gap:.5rem;">
                        
                        <input type="hidden" name="ativo" value="1" />
                        <!-- Campo 'Área' removido: destino controlado por 'Exibir em' -->
            <label class="lbl">Exibir em</label>
                        <div style="display:flex; gap:.6rem; flex-wrap:wrap;">
                            <label style="display:flex; align-items:center; gap:.35rem; font-size:.65rem;">
                <input type="checkbox" name="show_on_index" value="1" checked /> Card Gramátike (Início)
                                <input type="hidden" name="show_on_index" value="0" />
                            </label>
                            <label style="display:flex; align-items:center; gap:.35rem; font-size:.65rem;">
                <input type="checkbox" name="show_on_edu" value="1" checked /> Card Gramátike Edu
                                <input type="hidden" name="show_on_edu" value="0" />
                            </label>
                            
                        </div>
                        <label class="lbl">Título</label>
                        <input name="titulo" placeholder="Ex: Guia de Gênero Neutro" required />
                        <label class="lbl">Texto (curto)</label>
                        <textarea name="texto" placeholder="Chamada curta"></textarea>
                        <label class="lbl">Link (destino)</label>
                        <input name="link" placeholder="https://... ou /videos" />
                        <label class="lbl">Imagem (URL ou caminho em /static)</label>
                        <input name="imagem" placeholder="Ex: uploads/divulgacao/xyz.png" />
                        <label class="lbl">Ordem</label>
                        <input name="ordem" type="number" value="0" />
                        <button type="submit" class="btn-add-aviso">Criar Divulgação</button>
                        <div style="margin-top:.4rem;">
                            <form method="POST" action="/main/admin_divulgacao_upload" enctype="multipart/form-data" style="display:flex; gap:.5rem; align-items:center; flex-wrap:wrap;">
                                
                                <label class="lbl" style="margin:0;">ou envie uma imagem:</label>
                                <input type="file" name="arquivo" accept="image/*" />
                                <button type="submit" class="action-btn" style="font-size:.62rem;">Upload</button>
                            </form>
                            <!-- IF session.get('last_divulgacao_image'):
    END_html = f"""
<p class="small-muted" style="margin:.3rem 0 0;">Último arquivo: <code>{{ session.get('last_divulgacao_image') }}</code></p>
    """
{END_html}

                        </div>
                    </form>
                </div>
                <!-- Divulgações feitas ao lado do card de Nova Divulgação -->
                <div class="card">
                    <h4 style="margin:0 0 .9rem; font-size:.85rem; letter-spacing:.5px;">Divulgações feitas</h4>
                    
divulgacoes_html = ""
if divulgacoes:
    divulgacoes_html = f"""
<div style="display:flex; flex-direction:column; gap:.8rem; max-height:600px; overflow-y:auto;">
                        
divulgacoes_html = ""
for d in divulgacoes:
    divulgacoes_html += f"""
<div class="promo-item" style="background:var(--bg-alt); border:1px solid var(--border); border-radius:14px; padding:.7rem .75rem .85rem; position:relative; display:flex; flex-direction:column; gap:.55rem;">
                            <div style="display:flex; justify-content:space-between; align-items:center; gap:.6rem;">
                                <div>
                                    <strong style="font-size:.7rem; letter-spacing:.4px;">{d.titulo}</strong>
                                    <!-- IF not d.ativo START -->
                                        <span class="badge" style="background:#6b7280;color:#fff; margin-left:.35rem;">Arquivada</span>
    """
{divulgacoes_html}

                                    <div class="small-muted" style="margin-top:.15rem;">Ordem: {d.ordem}</div>
                                </div>
                                <form method="POST" action="/main/admin_divulgacao_update/{d.id}" style="margin:0; display:flex; gap:.35rem; align-items:center;">
                                    
                                    <input type="hidden" name="next" value="/admin/dashboard#publi" />
                                    <input type="hidden" name="ativo" value="{{ '0' if d.ativo else '1' }}" />
                                    <button type="submit" class="action-btn
d_html = ""
if d.ativo:
    d_html = f"""
promo-active
    """
{d_html}
" style="font-size:.52rem; padding:3px 8px;">{{ 'Ativo' if d.ativo else 'Inativo' }}</button>
                                </form>
                            </div>
                            
d_html = ""
if d.texto:
    d_html = f"""
<p style="margin:0; font-size:.58rem; line-height:1.3; color:var(--text-soft);">{d.texto}</p>
    """
{d_html}

                            
d_html = ""
if d.imagem:
    d_html = f"""
{% set imgsrc = d.imagem if d.imagem.startswith('http') else url_for('static', filename=d.imagem) %}
                                <img src="{imgsrc}" alt="{d.titulo}" style="max-width:100%; border-radius:10px; box-shadow:0 4px 12px rgba(0,0,0,.12);" loading="lazy" />
    """
{d_html}

                            
d_html = ""
if d.link:
    d_html = f"""
<a href="{d.link}" target="_blank" rel="noopener" style="font-size:.55rem; font-weight:700; color:var(--accent); text-decoration:none;">Abrir link →</a>
    """
{d_html}

                            <details style="margin-top:.25rem;">
                                <summary class="small-muted" style="cursor:pointer;">Editar</summary>
                                <form method="POST" action="/main/admin_divulgacao_update/{d.id}" class="publi-aviso-form" style="margin-top:.5rem; gap:.45rem;">
                                    
                                    <input type="hidden" name="next" value="/admin/dashboard#publi" />
                                    <!-- Campo 'Área' removido nos edits -->
                    <label class="lbl">Exibir em</label>
                                    <div style="display:flex; gap:.6rem; flex-wrap:wrap;">
                                        <label style="display:flex; align-items:center; gap:.35rem; font-size:.65rem;">
                        <input type="checkbox" name="show_on_index" value="1" 
d_html = ""
if d.show_on_index:
    d_html = f"""
checked
    """
{d_html}
 /> Card Gramátike (Início)
                                            <input type="hidden" name="show_on_index" value="0" />
                                        </label>
                                        <label style="display:flex; align-items:center; gap:.35rem; font-size:.65rem;">
                        <input type="checkbox" name="show_on_edu" value="1" 
d_html = ""
if d.show_on_edu:
    d_html = f"""
checked
    """
{d_html}
 /> Card Gramátike Edu
                                            <input type="hidden" name="show_on_edu" value="0" />
                                        </label>
                                        
                                    </div>
                                    <label class="lbl">Título</label>
                                    <input name="titulo" value="{d.titulo}" />
                                    <label class="lbl">Texto</label>
                                    <textarea name="texto">{d.texto}</textarea>
                                    <label class="lbl">Link</label>
                                    <input name="link" value="{d.link}" />
                                    <label class="lbl">Imagem</label>
                                    <input name="imagem" value="{d.imagem}" />
                                    <label class="lbl">Ordem</label>
                                    <input name="ordem" type="number" value="{d.ordem}" />
                                    <div style="display:flex; gap:.5rem;">
                                        <button type="submit" class="action-btn" style="font-size:.65rem;">Salvar</button>
                                    </div>
                                </form>
                            </details>
                            <div style="display:flex; gap:.4rem; flex-wrap:wrap;">
                                
if d.ativo:
    d_html = f"""
<form method="POST" action="/main/admin_divulgacao_update/{d.id}" onsubmit="return confirm('Arquivar esta divulgação?');" style="margin:0;">
                                    
                                    <input type="hidden" name="next" value="/admin/dashboard#publi" />
                                    <input type="hidden" name="ativo" value="0" />
                                    <button type="submit" class="action-btn" style="font-size:.5rem; padding:3px 8px;">Arquivar</button>
                                </form>
    """
else:
    d_html = f"""
<form method="POST" action="/main/admin_divulgacao_update/{d.id}" style="margin:0;">
                                    
                                    <input type="hidden" name="next" value="/admin/dashboard#publi" />
                                    <input type="hidden" name="ativo" value="1" />
                                    <button type="submit" class="action-btn" style="font-size:.5rem; padding:3px 8px;">Reativar</button>
                                </form>
    """
{d_html}

                                <form method="POST" action="/main/admin_divulgacao_delete/{d.id}" onsubmit="return confirm('Remover divulgação?');" style="margin:0;">
                                    
                                    <input type="hidden" name="next" value="/admin/dashboard#publi" />
                                    <button type="submit" class="action-btn danger" style="font-size:.5rem; padding:3px 8px;">Excluir</button>
                                </form>
                            </div>
                        </div>
                        <!-- ELSE -->
                            <p class="small-muted" style="font-size:.6rem;">Sem divulgações.</p>
    """
{divulgacoes_html}

                    </div>
                    <!-- ELSE -->
                        <p class="small-muted" style="margin-top:1rem; font-size:.6rem;">Nenhuma divulgação cadastrada.</p>
                    
END_html = ""
if END -->
                </div>
            </div>
            <script>
            // Placeholder simples em memória para avisos até existir backend
            (function(){
                const store = [];
                const listEl = document.getElementById('publiAvisos');
                function render(){
                    if(!listEl) return;
                    if(store.length===0){
                        listEl.className='lista-avisos-vazia';
                        listEl.innerHTML = `<span class='muted' style="font-size:.62rem;">${listEl.getAttribute('data-empty-msg')}</span>`;
                        return;
                    }
                    listEl.className='lista-avisos';
                    listEl.innerHTML = store.map(a=>{
                        return `<div class=\"aviso-item\" role=\"listitem\"><div class=\"aviso-head\"><strong>${a.titulo}</strong><time>${a.ts.toLocaleString('pt-BR')}</time></div><p>${a.mensagem}</p></div>`;
                    }).join('');
                }
                window.addPubliAviso = function(form){
                    const titulo = form.titulo.value.trim();
                    const mensagem = form.mensagem.value.trim();
                    if(!titulo || !mensagem) return;
                    store.unshift({titulo, mensagem, ts:new Date()});
                    form.reset();
                    render();
                };
                render();
            })();
            </script>
"""

EDU_TAB_HTML = f"""
<h2 style="margin-top:0;">Gramátike Edu</h2>
            <div style="margin:.5rem 0 1rem; display:flex; gap:.5rem; flex-wrap:wrap;">
                <button class="edu-area-btn" data-area="artigos">Artigos</button>
                <button class="edu-area-btn" data-area="apostilas">Apostilas</button>
                <button class="edu-area-btn" data-area="podcasts">Podcasts</button>
                <button class="edu-area-btn" data-area="redacao">Redação</button>
                <button class="edu-area-btn" data-area="exercicios">Exercícios</button>
                <button class="edu-area-btn" data-area="videos">Vídeos</button>
                <button class="edu-area-btn" data-area="gramatike">Gramátike</button>
            </div>
            <style>
                .edu-area-btn { background:#fff; border:1px solid #d1dae5; padding:.45rem .85rem; border-radius:8px; font-size:.7rem; cursor:pointer; font-weight:600; letter-spacing:.4px; }
                .edu-area-btn.active { background:#9B5DE5; color:#fff; border-color:#9B5DE5; }
                .edu-area-section { display:none; animation:fade .3s ease; }
                .edu-area-section.active { display:block; }
                .edu-two-col { display:grid; gap:1rem; grid-template-columns:repeat(auto-fit,minmax(300px,1fr)); }
                .edu-box { background:#fff; border:1px solid #e3e9f0; border-radius:14px; padding:1rem .95rem 1.1rem; box-shadow:0 2px 4px rgba(0,0,0,.04); }
                .edu-box h3 { margin:.1rem 0 .7rem; font-size:.9rem; }
                .edu-box form { display:flex; flex-direction:column; gap:.5rem; }
                .edu-box input, .edu-box textarea, .edu-box select { padding:.55rem .6rem; border:1px solid #cfd7e2; border-radius:8px; font-size:.72rem; background:#f9fbfd; }
                .edu-box textarea { min-height:150px; resize:vertical; }
                .edu-box button { padding:.55rem .9rem; border:none; background:#9B5DE5; color:#fff; font-weight:600; border-radius:8px; font-size:.7rem; cursor:pointer; }
                .edu-box button:hover { background:#7d3dc9; }
                .muted-inline { font-size:.6rem; color:#6b7785; margin-top:-.3rem; }
                /* Quill editor styles for dashboard */
                #novidade-editor-container { min-height:200px; background:#fff; border:1px solid #cfd7e2; border-radius:8px; }
                .ql-toolbar.ql-snow { border-top-left-radius:8px; border-top-right-radius:8px; background:#f9fafb; }
                .ql-container.ql-snow { border-bottom-left-radius:8px; border-bottom-right-radius:8px; font-size:.72rem; }
            </style>
            <!-- Artigos -->
            <!-- Gramátike (Novidades / Avisos internos para revisar materiais) -->
            <div class="edu-area-section" id="area-gramatike">
                <div class="edu-two-col">
                    <div class="edu-box" style="grid-column:1/-1;">
                        <h3>Postar Novidade</h3>
                        <form id="formNovidadeGmtk" method="POST" action="/admin/novidades_create">
                            
                            <input type="hidden" name="descricao" id="novidade-descricao-input" />
                            <input name="titulo" placeholder="Título da novidade" required />
                            <div style="margin:.5rem 0;">
                                <div id="novidade-editor-container"></div>
                            </div>
                            <input name="link" placeholder="Link opcional para o conteúdo (URL interna ou externa)" />
                            <button type="submit">Adicionar</button>
                        </form>
                        <!-- Lista de novidades removida do dashboard a pedido -->
                    </div>
                    <div class="edu-box" style="grid-column:1/-1;">
                        <h3 style="display:flex; align-items:center; gap:.4rem;"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#9B5DE5" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/></svg> Palavra do Dia</h3>
                        <form method="POST" action="/admin/palavra_do_dia_create">
                            
                            <input name="palavra" placeholder="Palavra ou expressão" required />
                            <textarea name="significado" placeholder="Significado (explicação curta e inclusiva)" required></textarea>
                            <button type="submit">Adicionar Palavra</button>
                        </form>
                    </div>
                    <div class="edu-box" style="grid-column:1/-1;">
                        <h3>Palavras Cadastradas</h3>
                        <div id="lista-palavras-do-dia" style="display:flex; flex-direction:column; gap:.5rem;">
                            <div style="text-align:center; color:#999; font-size:.7rem;">Carregando...</div>
                        </div>
                    </div>
                    <div class="edu-box" style="grid-column:1/-1;">
                        <h3><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#9B5DE5" stroke-width="2.2" style="display:inline-block;vertical-align:middle;margin-right:4px;"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg> Ver Respostas</h3>
                        <div style="display:flex; gap:.5rem; margin-bottom:.8rem;">
                            <input id="filtro-palavra-id" placeholder="ID da palavra (opcional)" style="width:150px;" />
                            <button type="button" onclick="carregarRespostasPalavras()" style="padding:.55rem 1rem;">Buscar Respostas</button>
                        </div>
                        <div id="lista-respostas-palavras" style="display:flex; flex-direction:column; gap:.5rem;">
                            <div style="text-align:center; color:#999; font-size:.7rem;">Clique em "Buscar Respostas" para ver as interações</div>
                        </div>
                    </div>
                    <!-- Cards "Ideias / Backlog" e "Atalhos Rápidos" removidos a pedido -->
                </div>
                <script>
                // Initialize Quill editor for Novidade
                var novidadeQuill = new Quill('#novidade-editor-container', {
                    theme: 'snow',
                    modules: {
                        toolbar: [
                            [{ 'header': [1, 2, 3, false] }],
                            ['bold', 'italic', 'underline'],
                            [{ 'list': 'ordered'}, { 'list': 'bullet' }],
                            ['link'],
                            ['clean']
                        ]
                    },
                    placeholder: 'Escreva a descrição da novidade...'
                });
                
                // Update hidden input on form submit
                document.getElementById('formNovidadeGmtk').addEventListener('submit', function() {
                    document.getElementById('novidade-descricao-input').value = novidadeQuill.root.innerHTML;
                });
                
                // Palavra do Dia - Listar
                async function carregarPalavrasDoDia() {
                    const container = document.getElementById('lista-palavras-do-dia');
                    if (!container) return;
                    
                    try {
                        const res = await fetch('/admin/palavra-do-dia/list');
                        const palavras = await res.json();
                        
                        if (!palavras.length) {
                            container.innerHTML = '<div style="text-align:center; color:#999; font-size:.7rem;">Nenhuma palavra cadastrada</div>';
                            return;
                        }
                        
                        container.innerHTML = palavras.map(p => `
                            <div style="border:1px solid #e3e9f0; border-radius:10px; padding:.7rem; background:#f9fbfd; display:flex; justify-content:space-between; align-items:center;">
                                <div style="flex:1;">
                                    <div style="font-weight:700; font-size:.85rem;">${p.palavra}</div>
                                    <div style="font-size:.65rem; color:#666; margin-top:.2rem;">${p.significado}</div>
                                    <div style="font-size:.6rem; color:#999; margin-top:.3rem;">
                                        Ordem: ${p.ordem} | ${p.ativo ? '✅ Ativa' : '❌ Inativa'} | Interações: ${p.interacoes_count || 0}
                                    </div>
                                </div>
                                <div style="display:flex; gap:.4rem;">
                                    <form method="POST" action="/admin/palavra-do-dia/${p.id}/toggle" style="display:inline;">
                                        
                                        <button type="submit" class="action-btn" style="font-size:.6rem;">
                                            ${p.ativo ? 'Desativar' : 'Ativar'}
                                        </button>
                                    </form>
                                    <form method="POST" action="/admin/palavra-do-dia/${p.id}/delete" onsubmit="return confirm('Excluir esta palavra?');" style="display:inline;">
                                        
                                        <button type="submit" class="action-btn danger" style="font-size:.6rem;">Excluir</button>
                                    </form>
                                </div>
                            </div>
                        `).join('');
                    } catch (e) {
                        container.innerHTML = '<div style="text-align:center; color:#f44; font-size:.7rem;">Erro ao carregar</div>';
                    }
                }
                
                // Palavra do Dia - Respostas
                window.carregarRespostasPalavras = async function() {
                    const container = document.getElementById('lista-respostas-palavras');
                    const palavraId = document.getElementById('filtro-palavra-id').value.trim();
                    if (!container) return;
                    
                    container.innerHTML = '<div style="text-align:center; color:#999; font-size:.7rem;">Carregando...</div>';
                    
                    try {
                        const url = '/admin/palavra-do-dia/respostas' + (palavraId ? `?palavra_id=${palavraId}` : '');
                        const res = await fetch(url);
                        const respostas = await res.json();
                        
                        if (!respostas.length) {
                            container.innerHTML = '<div style="text-align:center; color:#999; font-size:.7rem;">Nenhuma resposta encontrada</div>';
                            return;
                        }
                        
                        container.innerHTML = respostas.map(r => `
                            <div style="border:1px solid #e3e9f0; border-radius:10px; padding:.7rem; background:#fff;">
                                <div style="display:flex; justify-content:space-between; margin-bottom:.4rem;">
                                    <div style="font-weight:700; font-size:.75rem;">${r.palavra}</div>
                                    <div style="font-size:.65rem; color:#999;">${r.data}</div>
                                </div>
                                <div style="font-size:.7rem; color:#666; margin-bottom:.3rem;">
                                    <strong>Usuárie:</strong> ${r.usuario} | <strong>Tipo:</strong> ${r.tipo === 'frase' ? 'Frase' : 'Significado'}
                                </div>
                                ${r.frase ? `<div style="font-size:.7rem; color:#333; background:#f1edff; padding:.5rem; border-radius:8px; margin-top:.4rem;">"${r.frase}"</div>` : ''}
                            </div>
                        `).join('');
                    } catch (e) {
                        container.innerHTML = '<div style="text-align:center; color:#f44; font-size:.7rem;">Erro ao carregar</div>';
                    }
                }
                
                // Carregar palavras ao mostrar a seção
                document.addEventListener('DOMContentLoaded', () => {
                    const btns = document.querySelectorAll('.edu-area-btn');
                    btns.forEach(btn => {
                        btn.addEventListener('click', () => {
                            if (btn.dataset.area === 'gramatike') {
                                setTimeout(carregarPalavrasDoDia, 100);
                            }
                        });
                    });
                });
                </script>
            </div>
            <div class="edu-area-section active" id="area-artigos">
                <div class="edu-two-col">
                    <div class="edu-box">
                        <h3>Publicar Artigo</h3>
                        <form method="POST" action="/admin/edu_publicar" enctype="multipart/form-data">
                            
                            <input type="hidden" name="tipo" value="artigo" />
                            <input name="titulo" placeholder="Título" required />
                            <input name="autor" placeholder="Autore (opcional)" />
                            <select name="topic_id">
                                <option value="">(Tópico)</option>
                                {% for t in edu_topics if t.area=='artigo' %}<option value="{t.id}">{t.nome}</option><!-- FOR END -->
                            </select>
                            <input name="url" placeholder="Link (fonte)" />
                            <textarea name="resumo" placeholder="Resumo"></textarea>
                            <button type="submit">Publicar</button>
                        </form>
                    </div>
                    <div class="edu-box">
                        <h3>Criar Tópico</h3>
                        <form method="POST" action="/admin/edu_topic_create">
                            
                            <input type="hidden" name="area" value="artigo" />
                            <input name="nome" placeholder="Nome" required />
                            <textarea name="descricao" placeholder="Descrição"></textarea>
                            <button type="submit">Criar</button>
                        </form>
                    </div>
                </div>
                <!-- Gerenciar Tópicos de Artigos -->
                <div class="edu-box" style="margin-top:1rem;">
                    <h3>Gerenciar Tópicos de Artigos</h3>
                    <!-- IF edu_topics:
    END_html = f"""
{% set artigo_topics = edu_topics | selectattr('area', 'equalto', 'artigo') | list %}
                        <!-- IF artigo_topics START -->
                            <div style="display:grid; gap:.8rem; grid-template-columns:1fr;">
                                
artigo_topics_html = ""
for topic in artigo_topics:
    artigo_topics_html += f"""
<div style="background:#f9fbfd; border:1px solid #e3e9f0; border-radius:12px; padding:.9rem;">
                                    <div style="display:flex; justify-content:space-between; align-items:start; gap:.8rem;">
                                        <div style="flex:1;">
                                            <div style="font-weight:700; font-size:.85rem; color:#333; margin-bottom:.3rem;">{topic.nome}</div>
                                            <!-- IF topic.descricao START -->
                                                <div style="font-size:.7rem; color:#666; margin-bottom:.5rem;">{topic.descricao}</div>
    """
{END_html}

                                        </div>
                                        <button onclick="toggleTopicEdit('artigo-{topic.id}')" class="action-btn" style="font-size:.6rem; padding:4px 10px;">
                                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:middle;">
                                                <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
                                            </svg>
                                            Editar
                                        </button>
                                    </div>
                                    <div id="topic-edit-artigo-{topic.id}" style="display:none; margin-top:.8rem; padding-top:.8rem; border-top:1px solid #e3e9f0;">
                                        <form method="POST" action="/admin/edu_topic_update/{topic.id}" style="display:flex; flex-direction:column; gap:.5rem;">
                                            
                                            <label style="font-size:.7rem; font-weight:600; color:#666;">Nome</label>
                                            <input name="nome" value="{topic.nome}" placeholder="Nome" style="padding:.5rem; border:1px solid #cfd7e2; border-radius:8px; font-size:.72rem;" required />
                                            <label style="font-size:.7rem; font-weight:600; color:#666;">Descrição</label>
                                            <textarea name="descricao" placeholder="Descrição" style="padding:.5rem; border:1px solid #cfd7e2; border-radius:8px; font-size:.72rem; min-height:60px;">{{ topic.descricao or '' }}</textarea>
                                            <div style="display:flex; gap:.5rem; margin-top:.3rem;">
                                                <button type="submit" class="action-btn" style="background:var(--accent); color:#fff; border:none; font-size:.65rem; padding:.5rem .9rem;">Salvar</button>
                                                <button type="button" onclick="toggleTopicEdit('artigo-{topic.id}')" class="action-btn" style="font-size:.65rem; padding:.5rem .9rem;">Cancelar</button>
                                            </div>
                                        </form>
                                    </div>
                                </div>
    """
{artigo_topics_html}

                            </div>
                        <!-- ELSE -->
                            <p class="muted-inline">Nenhum tópico criado ainda.</p>
                        
END_html = ""
if END -->
                    <!-- IF END -->
                </div>
            </div>
            <!-- Apostilas -->
            <div class="edu-area-section" id="area-apostilas">
                <div class="edu-two-col">
                    <div class="edu-box">
                        <h3>Publicar Apostila</h3>
                        <form method="POST" action="/admin/edu_publicar" enctype="multipart/form-data">
                            
                            <input type="hidden" name="tipo" value="apostila" />
                            <input name="titulo" placeholder="Título" required />
                            <input name="autor" placeholder="Autore (opcional)" />
                            <select name="topic_id">
                                <option value="">(Tópico)</option>
                                {% for t in edu_topics if t.area=='apostila' %}<option value="{t.id}">{t.nome}</option><!-- FOR END -->
                            </select>
                            <input type="file" name="pdf" accept="application/pdf" />
                            <input name="url" placeholder="OU insira um link (URL)" />
                            <textarea name="resumo" placeholder="Descrição"></textarea>
                            <button type="submit">Publicar</button>
                        </form>
                    </div>
                    <div class="edu-box">
                        <h3>Criar Tópico</h3>
                        <form method="POST" action="/admin/edu_topic_create">
                            
                            <input type="hidden" name="area" value="apostila" />
                            <input name="nome" placeholder="Nome" required />
                            <textarea name="descricao" placeholder="Descrição"></textarea>
                            <button type="submit">Criar</button>
                        </form>
                    </div>
                </div>
                <!-- Gerenciar Tópicos de Apostilas -->
                <div class="edu-box" style="margin-top:1rem;">
                    <h3>Gerenciar Tópicos de Apostilas</h3>
                    <!-- IF edu_topics:
    END_html = f"""
{% set apostila_topics = edu_topics | selectattr('area', 'equalto', 'apostila') | list %}
                        <!-- IF apostila_topics START -->
                            <div style="display:grid; gap:.8rem; grid-template-columns:1fr;">
                                
apostila_topics_html = ""
for topic in apostila_topics:
    apostila_topics_html += f"""
<div style="background:#f9fbfd; border:1px solid #e3e9f0; border-radius:12px; padding:.9rem;">
                                    <div style="display:flex; justify-content:space-between; align-items:start; gap:.8rem;">
                                        <div style="flex:1;">
                                            <div style="font-weight:700; font-size:.85rem; color:#333; margin-bottom:.3rem;">{topic.nome}</div>
                                            <!-- IF topic.descricao START -->
                                                <div style="font-size:.7rem; color:#666; margin-bottom:.5rem;">{topic.descricao}</div>
    """
{END_html}

                                        </div>
                                        <button onclick="toggleTopicEdit('apostila-{topic.id}')" class="action-btn" style="font-size:.6rem; padding:4px 10px;">
                                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:middle;">
                                                <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
                                            </svg>
                                            Editar
                                        </button>
                                    </div>
                                    <div id="topic-edit-apostila-{topic.id}" style="display:none; margin-top:.8rem; padding-top:.8rem; border-top:1px solid #e3e9f0;">
                                        <form method="POST" action="/admin/edu_topic_update/{topic.id}" style="display:flex; flex-direction:column; gap:.5rem;">
                                            
                                            <label style="font-size:.7rem; font-weight:600; color:#666;">Nome</label>
                                            <input name="nome" value="{topic.nome}" placeholder="Nome" style="padding:.5rem; border:1px solid #cfd7e2; border-radius:8px; font-size:.72rem;" required />
                                            <label style="font-size:.7rem; font-weight:600; color:#666;">Descrição</label>
                                            <textarea name="descricao" placeholder="Descrição" style="padding:.5rem; border:1px solid #cfd7e2; border-radius:8px; font-size:.72rem; min-height:60px;">{{ topic.descricao or '' }}</textarea>
                                            <div style="display:flex; gap:.5rem; margin-top:.3rem;">
                                                <button type="submit" class="action-btn" style="background:var(--accent); color:#fff; border:none; font-size:.65rem; padding:.5rem .9rem;">Salvar</button>
                                                <button type="button" onclick="toggleTopicEdit('apostila-{topic.id}')" class="action-btn" style="font-size:.65rem; padding:.5rem .9rem;">Cancelar</button>
                                            </div>
                                        </form>
                                    </div>
                                </div>
    """
{apostila_topics_html}

                            </div>
                        <!-- ELSE -->
                            <p class="muted-inline">Nenhum tópico criado ainda.</p>
                        
END_html = ""
if END -->
                    <!-- IF END -->
                </div>
            </div>
            <!-- Podcasts -->
            <div class="edu-area-section" id="area-podcasts">
                <div class="edu-two-col">
                    <div class="edu-box">
                        <h3>Publicar Podcast</h3>
                        <form method="POST" action="/admin/edu_publicar">
                            
                            <input type="hidden" name="tipo" value="podcast" />
                            <input name="titulo" placeholder="Título" required />
                            <input name="autor" placeholder="Autore (opcional)" />
                            <select name="topic_id">
                                <option value="">(Tópico)</option>
                                {% for t in edu_topics if t.area=='podcast' %}<option value="{t.id}">{t.nome}</option><!-- FOR END -->
                            </select>
                            <input name="url" id="podcast-url" placeholder="Link do Spotify ou URL de áudio (.mp3)" />
                            <small class="muted-inline">Cole um link/iframe do Spotify (gera player automático) ou um link direto .mp3.</small>
                            <div id="podcast-preview" style="margin-top:.6rem; padding:.6rem; border:1px dashed #cfd7e2; border-radius:10px; background:#f9fbfd; display:none;"></div>
                            <textarea name="resumo" placeholder="Descrição"></textarea>
                            <button type="submit">Publicar</button>
                        </form>
                        <script>
                        (function(){
                            const input = document.getElementById('podcast-url');
                            const box = document.getElementById('podcast-preview');
                            if(!input || !box) return;
                            function extractSpotifyId(val){
                                // Se for iframe, extrai src
                                const mIframe = val.match(/src=\"https?:\/\/open\.spotify\.com\/embed\/(episode|show)\/([A-Za-z0-9]+)[^\"]*\"/);
                                if(mIframe) return { kind: mIframe[1], id: mIframe[2] };
                                // Se for link comum
                                const mLink = val.match(/spotify\.com\/(episode|show)\/([A-Za-z0-9]+)/);
                                if(mLink) return { kind: mLink[1], id: mLink[2] };
                                return null;
                            }
                            function render(){
                                const val = (input.value||'').trim();
                                if(!val){ box.style.display='none'; box.innerHTML=''; return; }
                                // Spotify
                                const sp = extractSpotifyId(val);
                                if(sp){
                                    const embed = `https://open.spotify.com/embed/${sp.kind}/${sp.id}?utm_source=generator`;
                                    box.innerHTML = `<iframe data-testid="embed-iframe" style="border-radius:12px; width:100%;" src="${embed}" width="100%" height="352" frameBorder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>`;
                                    box.style.display='block';
                                    return;
                                }
                                // MP3
                                if(/\.mp3($|\?)/i.test(val)){
                                    box.innerHTML = `<audio controls preload="none" style="width:100%"><source src="${val}" type="audio/mpeg" />Seu navegador não suporta áudio.</audio>`;
                                    box.style.display='block';
                                    return;
                                }
                                // Outro: limpa preview
                                box.style.display='none';
                                box.innerHTML='';
                            }
                            input.addEventListener('input', render);
                            input.addEventListener('change', render);
                            input.addEventListener('paste', ()=>setTimeout(render, 0));
                        })();
                        </script>
                    </div>
                    <div class="edu-box">
                        <h3>Criar Tópico</h3>
                        <form method="POST" action="/admin/edu_topic_create">
                            
                            <input type="hidden" name="area" value="podcast" />
                            <input name="nome" placeholder="Nome" required />
                            <textarea name="descricao" placeholder="Descrição"></textarea>
                            <button type="submit">Criar</button>
                        </form>
                    </div>
                </div>
                <!-- Gerenciar Tópicos de Podcasts -->
                <div class="edu-box" style="margin-top:1rem;">
                    <h3>Gerenciar Tópicos de Podcasts</h3>
                    <!-- IF edu_topics:
    END_html = f"""
{% set podcast_topics = edu_topics | selectattr('area', 'equalto', 'podcast') | list %}
                        <!-- IF podcast_topics START -->
                            <div style="display:grid; gap:.8rem; grid-template-columns:1fr;">
                                
podcast_topics_html = ""
for topic in podcast_topics:
    podcast_topics_html += f"""
<div style="background:#f9fbfd; border:1px solid #e3e9f0; border-radius:12px; padding:.9rem;">
                                    <div style="display:flex; justify-content:space-between; align-items:start; gap:.8rem;">
                                        <div style="flex:1;">
                                            <div style="font-weight:700; font-size:.85rem; color:#333; margin-bottom:.3rem;">{topic.nome}</div>
                                            <!-- IF topic.descricao START -->
                                                <div style="font-size:.7rem; color:#666; margin-bottom:.5rem;">{topic.descricao}</div>
    """
{END_html}

                                        </div>
                                        <button onclick="toggleTopicEdit('podcast-{topic.id}')" class="action-btn" style="font-size:.6rem; padding:4px 10px;">
                                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:middle;">
                                                <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
                                            </svg>
                                            Editar
                                        </button>
                                    </div>
                                    <div id="topic-edit-podcast-{topic.id}" style="display:none; margin-top:.8rem; padding-top:.8rem; border-top:1px solid #e3e9f0;">
                                        <form method="POST" action="/admin/edu_topic_update/{topic.id}" style="display:flex; flex-direction:column; gap:.5rem;">
                                            
                                            <label style="font-size:.7rem; font-weight:600; color:#666;">Nome</label>
                                            <input name="nome" value="{topic.nome}" placeholder="Nome" style="padding:.5rem; border:1px solid #cfd7e2; border-radius:8px; font-size:.72rem;" required />
                                            <label style="font-size:.7rem; font-weight:600; color:#666;">Descrição</label>
                                            <textarea name="descricao" placeholder="Descrição" style="padding:.5rem; border:1px solid #cfd7e2; border-radius:8px; font-size:.72rem; min-height:60px;">{{ topic.descricao or '' }}</textarea>
                                            <div style="display:flex; gap:.5rem; margin-top:.3rem;">
                                                <button type="submit" class="action-btn" style="background:var(--accent); color:#fff; border:none; font-size:.65rem; padding:.5rem .9rem;">Salvar</button>
                                                <button type="button" onclick="toggleTopicEdit('podcast-{topic.id}')" class="action-btn" style="font-size:.65rem; padding:.5rem .9rem;">Cancelar</button>
                                            </div>
                                        </form>
                                    </div>
                                </div>
    """
{podcast_topics_html}

                            </div>
                        <!-- ELSE -->
                            <p class="muted-inline">Nenhum tópico criado ainda.</p>
                        
END_html = ""
if END -->
                    <!-- IF END -->
                </div>
                <div class="edu-box" style="margin-top:1rem;">
                    <h3>Podcasts Recentes</h3>
                    <div style="display:flex; gap:.5rem; align-items:center; margin-bottom:.6rem;">
                        <input id="busca-podcasts" placeholder="Buscar por título/descrição..." style="flex:1;" />
                        <button type="button" id="btn-buscar-podcasts" aria-label="Buscar" title="Buscar" style="width:42px; display:inline-flex; align-items:center; justify-content:center; padding:0;">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                                <circle cx="11" cy="11" r="7"></circle>
                                <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                            </svg>
                        </button>
                    </div>
                    <ul id="lista-podcasts" style="list-style:none; padding:0; margin:0; display:grid; grid-template-columns:repeat(auto-fit,minmax(300px,1fr)); gap:.6rem;"></ul>
                    <dialog id="podcastEditDialog">
                        <form id="podcastEditForm" method="post">
                            <h3>Editar Podcast</h3>
                            
                            <input type="hidden" name="content_id" id="pe_id" />
                            <label style="display:block; font-size:.75rem; margin:.4rem 0 .2rem;">Título</label>
                            <input name="titulo" id="pe_titulo" required />
                            <label style="display:block; font-size:.75rem; margin:.6rem 0 .2rem;">Autore</label>
                            <input name="autor" id="pe_autor" />
                            <label style="display:block; font-size:.75rem; margin:.6rem 0 .2rem;">Resumo</label>
                            <textarea name="resumo" id="pe_resumo" rows="8" style="min-height:200px; resize:vertical;"></textarea>
                            <label style="display:block; font-size:.75rem; margin:.6rem 0 .2rem;">URL/iframe do Spotify ou áudio (.mp3)</label>
                            <input name="url" id="pe_url" />
                            <label style="display:block; font-size:.75rem; margin:.6rem 0 .2rem;">Tópico</label>
                            <select name="topic_id" id="pe_topic"></select>
                            <menu style="display:flex; gap:8px; justify-content:flex-end; margin-top:12px;">
                                <button type="button" id="pe_cancel">Cancelar</button>
                                <button type="submit" class="action-btn">Salvar</button>
                            </menu>
                        </form>
                    </dialog>
                    <script>
                        (function(){
                            const ul = document.getElementById('lista-podcasts');
                            const q = document.getElementById('busca-podcasts');
                            function cardTemplate(i){
                                return `
                                    <li class="card" style="padding:.7rem .8rem; border:1px solid #e1e7ef; border-radius:10px; background:#fff; display:flex; flex-direction:column; gap:.5rem;">
                                        <div style="font-weight:700; font-size:.85rem;">${i.titulo}</div>
                                        <div class="small-muted">${i.topic || ''}</div>
                                        <div class="podcast-player" data-id="${i.id}" style="border:1px dashed #cfd7e2; border-radius:10px; padding:.5rem; background:#f9fbfd;"></div>
                                        <div style="display:flex; gap:.4rem;">
                                            <button class="action-btn" data-edit="${i.id}">Editar</button>
                                            <form method="POST" action="/admin/edu/content/${i.id}/delete" onsubmit="return confirm('Excluir este podcast?');">
                                                <button type="submit" class="action-btn danger">Excluir</button>
                                            </form>
                                        </div>
                                    </li>
                                `;
                            }
                            function render(items){
                                if(!ul) return;
                                if(!items.length){ ul.innerHTML = '<li class="muted">Nenhum resultado.</li>'; return; }
                                ul.innerHTML = items.map(cardTemplate).join('');
                                // Carrega players
                                const nodes = ul.querySelectorAll('.podcast-player');
                                nodes.forEach(async (node)=>{
                                    const id = node.getAttribute('data-id');
                                    try{
                                        const data = await fetch(`/admin/edu/content/${id}.json`).then(r=>r.json());
                                        let html = '';
                                        const embed = data.extra && data.extra.spotify_embed;
                                        if(embed){
                                            html = `<iframe data-testid="embed-iframe" style="border-radius:12px; width:100%;" src="${embed}" width="100%" height="352" frameBorder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>`;
                                        } else if(data.url && /\.mp3($|\?)/i.test(data.url)){
                                            html = `<audio controls preload="none" style="width:100%"><source src="${data.url}" type="audio/mpeg" />Seu navegador não suporta áudio.</audio>`;
                                        } else {
                                            html = '<div class="small-muted">Sem player disponível</div>';
                                        }
                                        node.innerHTML = html;
                                    }catch(e){ node.innerHTML = '<div class="small-muted">Erro ao carregar</div>'; }
                                });
                            }
                            async function buscar(term=''){
                                try{
                                    const url = new URL("/admin/edu_buscar", location.origin);
                                    url.searchParams.set('area','podcasts'); if(term) url.searchParams.set('q',term);
                                    const r = await fetch(url); const j = await r.json(); render(j.results||[]);
                                }catch(e){ render([]); }
                            }
                            document.getElementById('btn-buscar-podcasts')?.addEventListener('click', ()=>buscar(q.value.trim()));
                            q?.addEventListener('keydown', e=>{ if(e.key==='Enter'){ e.preventDefault(); buscar(q.value.trim()); } });
                            buscar('');

                            // Edição de podcast
                            const dlg = document.getElementById('podcastEditDialog');
                            const form = document.getElementById('podcastEditForm');
                            const pe_id = document.getElementById('pe_id');
                            const pe_titulo = document.getElementById('pe_titulo');
                            const pe_resumo = document.getElementById('pe_resumo');
                            const pe_url = document.getElementById('pe_url');
                            const pe_topic = document.getElementById('pe_topic');
                            const pe_cancel = document.getElementById('pe_cancel');
                            const pe_autor = document.getElementById('pe_autor');

                            ul.addEventListener('click', async (e)=>{
                                const btn = e.target.closest('button[data-edit]');
                                if(!btn) return;
                                const id = btn.getAttribute('data-edit');
                                try{
                                    const data = await fetch(`/admin/edu/content/${id}.json`).then(r=>r.json());
                                    pe_id.value = data.id;
                                    pe_titulo.value = data.titulo||'';
                                    pe_resumo.value = data.resumo||'';
                                    pe_autor.value = (data.extra && data.extra.author) ? data.extra.author : '';
                                    pe_url.value = data.url||'';
                                    pe_topic.innerHTML = '';
                                    const srcSelect = document.querySelector('#area-podcasts select[name="topic_id"]');
                                    if(srcSelect){
                                        for(const opt of srcSelect.options){
                                            const o = document.createElement('option'); o.value = opt.value; o.textContent = opt.textContent;
                                            if(String(opt.value) === String(data.topic_id||'')) o.selected = true;
                                            pe_topic.appendChild(o);
                                        }
                                    }
                                    dlg.showModal();
                                }catch(err){ alert('Falha ao carregar dados'); }
                            });
                            pe_cancel.addEventListener('click', ()=> dlg.close());
                            form.addEventListener('submit', async (e)=>{
                                e.preventDefault();
                                const id = pe_id.value;
                                const fd = new FormData(form);
                                try{
                                    const res = await fetch(`/admin/edu/content/${id}/update`, { method:'POST', body: fd, credentials: 'same-origin' });
                                    if(res.ok){ dlg.close(); buscar(q.value.trim()); } else { alert('Falha ao salvar'); }
                                }catch(err){ alert('Erro de rede'); }
                            });
                        })();
                    </script>
                </div>
            </div>
            <!-- Redação -->
            <div class="edu-area-section" id="area-redacao">
                <div class="edu-two-col">
                    <div class="edu-box">
                        <h3>Novo Tema de Redação</h3>
                        <form method="POST" action="/admin/edu_publicar">
                            <input type="hidden" name="tipo" value="redacao_tema" />
                            <input name="titulo" placeholder="Tema" required />
                            <textarea name="corpo" placeholder="Texto orientador / proposta"></textarea>
                            <button type="submit">Adicionar Tema</button>
                        </form>
                    </div>
                    <div class="edu-box">
                        <h3>Criar Tópico</h3>
                        <form method="POST" action="/admin/edu_topic_create">
                            <input type="hidden" name="area" value="redacao" />
                            <input name="nome" placeholder="Nome" required />
                            <textarea name="descricao" placeholder="Descrição"></textarea>
                            <button type="submit">Criar</button>
                        </form>
                    </div>
                </div>
                <!-- Gerenciar Tópicos de Redação -->
                <div class="edu-box" style="margin-top:1rem;">
                    <h3>Gerenciar Tópicos de Redação</h3>
                    <!-- IF edu_topics:
    END_html = f"""
{% set redacao_topics = edu_topics | selectattr('area', 'equalto', 'redacao') | list %}
                        <!-- IF redacao_topics START -->
                            <div style="display:grid; gap:.8rem; grid-template-columns:1fr;">
                                
redacao_topics_html = ""
for topic in redacao_topics:
    redacao_topics_html += f"""
<div style="background:#f9fbfd; border:1px solid #e3e9f0; border-radius:12px; padding:.9rem;">
                                    <div style="display:flex; justify-content:space-between; align-items:start; gap:.8rem;">
                                        <div style="flex:1;">
                                            <div style="font-weight:700; font-size:.85rem; color:#333; margin-bottom:.3rem;">{topic.nome}</div>
                                            <!-- IF topic.descricao START -->
                                                <div style="font-size:.7rem; color:#666; margin-bottom:.5rem;">{topic.descricao}</div>
    """
{END_html}

                                        </div>
                                        <button onclick="toggleTopicEdit('redacao-{topic.id}')" class="action-btn" style="font-size:.6rem; padding:4px 10px;">
                                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:middle;">
                                                <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
                                            </svg>
                                            Editar
                                        </button>
                                    </div>
                                    <div id="topic-edit-redacao-{topic.id}" style="display:none; margin-top:.8rem; padding-top:.8rem; border-top:1px solid #e3e9f0;">
                                        <form method="POST" action="/admin/edu_topic_update/{topic.id}" style="display:flex; flex-direction:column; gap:.5rem;">
                                            
                                            <label style="font-size:.7rem; font-weight:600; color:#666;">Nome</label>
                                            <input name="nome" value="{topic.nome}" placeholder="Nome" style="padding:.5rem; border:1px solid #cfd7e2; border-radius:8px; font-size:.72rem;" required />
                                            <label style="font-size:.7rem; font-weight:600; color:#666;">Descrição</label>
                                            <textarea name="descricao" placeholder="Descrição" style="padding:.5rem; border:1px solid #cfd7e2; border-radius:8px; font-size:.72rem; min-height:60px;">{{ topic.descricao or '' }}</textarea>
                                            <div style="display:flex; gap:.5rem; margin-top:.3rem;">
                                                <button type="submit" class="action-btn" style="background:var(--accent); color:#fff; border:none; font-size:.65rem; padding:.5rem .9rem;">Salvar</button>
                                                <button type="button" onclick="toggleTopicEdit('redacao-{topic.id}')" class="action-btn" style="font-size:.65rem; padding:.5rem .9rem;">Cancelar</button>
                                            </div>
                                        </form>
                                    </div>
                                </div>
    """
{redacao_topics_html}

                            </div>
                        <!-- ELSE -->
                            <p class="muted-inline">Nenhum tópico criado ainda.</p>
                        
END_html = ""
if END -->
                    <!-- IF END -->
                </div>
            </div>
            <!-- Exercícios -->
            <div class="edu-area-section" id="area-exercicios">
                <div class="edu-two-col">
                    <div class="edu-box" style="grid-column: span 2;">
                        <h3>Publicar Exercício</h3>
                        <form id="form-exercicio" method="POST" action="/admin/edu_create_question" style="display:flex; flex-direction:column; gap:.6rem;">
                            
                            <div style="display:flex; gap:.5rem; flex-wrap:wrap; align-items:flex-start;">
                                <select name="topic_id" id="ex-topic" required style="flex:1; min-width:180px;">
                                    <option value="">Tópico (Exercício)</option>
                                    
topics_html = ""
for t in topics:
    topics_html += f"""
<option value="{t.id}">{t.nome}</option>
    """
{topics_html}

                                </select>
                                <select name="section_id" id="ex-section" style="flex:1; min-width:180px; display:none;">
                                    <option value="">Sessão</option>
                                </select>
                                <select name="tipo" id="ex-tipo" required style="flex:1; min-width:180px;">
                                    <option value="">Modelo...</option>
                                    <option value="multipla_escolha">Múltipla escolha</option>
                                    <option value="arrastar_palavras">Arrastar palavras</option>
                                    <option value="discursiva">Discursiva</option>
                                    <option value="verdadeiro_falso">Verdadeiro ou Falso</option>
                                    <option value="lacunas">Lacunas</option>
                                    <option value="correspondencia">Correspondência</option>
                                </select>
                                <select name="dificuldade" style="flex:0 0 140px;">
                                    <option value="">Dificuldade</option>
                                    <option value="facil">Fácil</option>
                                    <option value="media">Média</option>
                                    <option value="dificil">Difícil</option>
                                </select>
                            </div>
                            <textarea name="enunciado" placeholder="Enunciado" required></textarea>
                            <!-- Campos dinâmicos -->
                            <div id="ex-campos" style="display:flex; flex-direction:column; gap:.55rem;"></div>
                            <!-- Campos ocultos finais -->
                            <textarea name="resposta" id="ex-resposta" hidden></textarea>
                            <textarea name="opcoes" id="ex-opcoes" hidden></textarea>
                            <button type="submit">Adicionar Exercício</button>
                        </form>
                                                                        <script id="sections-data" type="application/json">{{ sections_map|tojson }}</script>
                                                                        <script>
                                                                        // Parse dos dados de sessões por tópico
                                                                        let sectionsData = {};
                                                                        try { sectionsData = JSON.parse(document.getElementById('sections-data').textContent); } catch(e){ sectionsData = {}; }
                                                                        </script>
                        <script>
                        (function(){
                            const tipoSel = document.getElementById('ex-tipo');
                            const cont = document.getElementById('ex-campos');
                            const opcoesHidden = document.getElementById('ex-opcoes');
                            const respostaHidden = document.getElementById('ex-resposta');
                                                        const topicSel = document.getElementById('ex-topic');
                                                        const sectionSel = document.getElementById('ex-section');
                                                        function updateSections(){
                                                                if(!topicSel) return;
                                                                const tid = topicSel.value;
                                                                const list = sectionsData[tid] || [];
                                                                sectionSel.innerHTML = '<option value="">Sessão</option>' + list.map(s=>`<option value="${s.id}">${s.nome}</option>`).join('');
                                                                sectionSel.style.display = list.length ? 'block' : 'none';
                                                        }
                                                        topicSel?.addEventListener('change', updateSections);
                                                        updateSections();
                            function field(label, html, extra=''){
                                return `<div class='ex-field' style=\"display:flex; flex-direction:column; gap:.35rem;\" ${extra}>`+
                                       `<label style='font-size:.62rem; font-weight:600; text-transform:uppercase; letter-spacing:.55px; color:#48515c;'>${label}</label>`+
                                       `${html}</div>`;
                            }
                            // UI helpers para múltipla escolha
                            function renderMultipleChoice(){
                                cont.innerHTML = '';
                                cont.insertAdjacentHTML('beforeend', field('Alternativas', `
                                    <div id='mc-list' style='display:flex; flex-direction:column; gap:.4rem;'></div>
                                    <button type='button' id='mc-add' style='align-self:flex-start; background:#eef2ff; color:#334; padding:6px 10px; font-size:.65rem; border-radius:6px; border:1px solid #c5d0f5;'>+ Adicionar alternativa</button>
                                    <small style='font-size:.6rem; color:#667;'>Marque a correta no círculo. Use o ícone ☰ para arrastar. Tecle Enter no último campo para adicionar outra.</small>
                                `));
                                const list = document.getElementById('mc-list');
                                const addBtn = document.getElementById('mc-add');
                                let counter = 0;
                                function addOption(text=''){ 
                                    const id = 'opt_'+(counter++); 
                                    const row = document.createElement('div');
                                    row.className='mc-row';
                                    row.style.cssText='display:flex; align-items:center; gap:.5rem; background:#f7f9fd; padding:6px 8px; border:1px solid #d5dde8; border-radius:8px;';
                                    row.style.display='grid';
                                    row.style.gridTemplateColumns='24px 1fr 40px 40px';
                                    row.style.alignItems='center';
                                    row.style.columnGap='8px';
                                    row.innerHTML = `
                                        <span class='drag-handle' draggable='true' title='Arrastar' style='cursor:grab; font-size:.95rem; color:#53606d;'>☰</span>
                                        <input type='text' class='mc-text' placeholder='Digite a alternativa' value="${text.replace(/"/g,'&quot;')}" style='width:100%; padding:.55rem .65rem; border:1px solid #7d94aa; background:#fff; color:#1d2b38; border-radius:7px; font-size:.8rem; line-height:1.25; font-family:inherit; letter-spacing:.15px;' />
                                        <input type='radio' name='mc-correta' style='margin:0 auto; transform:scale(1.15); cursor:pointer;' aria-label='Marcar correta' />
                                        <button type='button' class='mc-del' title='Excluir' aria-label='Excluir alternativa' style='background:#fff; border:1px solid #d3dbe3; border-radius:7px; width:34px; height:34px; display:flex; align-items:center; justify-content:center; font-size:.8rem; cursor:pointer; color:#c62828; font-weight:600;'>×</button>`;
                                    list.appendChild(row);
                                    // Ao pressionar Enter neste input e for o último, cria nova opção
                                    const input = row.querySelector('.mc-text');
                                    input.addEventListener('keydown', ev=>{
                                        if(ev.key==='Enter'){
                                            ev.preventDefault();
                                            const rows=[...list.querySelectorAll('.mc-row .mc-text')];
                                            if(rows[rows.length-1]===input){ addOption(); setTimeout(()=>list.querySelector('.mc-row:last-child .mc-text').focus(),10); }
                                        }
                                    });
                                }
                                addBtn.addEventListener('click',()=>addOption());
                                // iniciar com 3
                                addOption(); addOption(); addOption();
                                // Delegação delete
                                list.addEventListener('click', e=>{
                                    if(e.target.classList.contains('mc-del')){
                                        const row = e.target.closest('.mc-row');
                                        row.remove();
                                    }
                                });
                                // Drag & drop reorder
                                let dragSrc;
                                list.addEventListener('dragstart', e=>{
                                    if(e.target.classList.contains('drag-handle')){ dragSrc=e.target.closest('.mc-row'); e.dataTransfer.effectAllowed='move'; }
                                });
                                list.addEventListener('dragover', e=>{ e.preventDefault(); });
                                list.addEventListener('drop', e=>{
                                    e.preventDefault();
                                    const tgt = e.target.closest('.mc-row');
                                    if(dragSrc && tgt && dragSrc!==tgt){
                                        const children=[...list.children];
                                        const srcIndex=children.indexOf(dragSrc);
                                        const tgtIndex=children.indexOf(tgt);
                                        if(srcIndex < tgtIndex) list.insertBefore(dragSrc, tgt.nextSibling); else list.insertBefore(dragSrc, tgt);
                                    }
                                });
                            }
                            function renderVerdadeiroFalso(){
                                cont.innerHTML = field('Resposta Correta', `
                                    <div style='display:flex; gap:1rem; font-size:.7rem;'>
                                        <label style='display:flex; align-items:center; gap:.35rem;'><input type='radio' name='vf' value='verdadeiro' required />Verdadeiro</label>
                                        <label style='display:flex; align-items:center; gap:.35rem;'><input type='radio' name='vf' value='falso' required />Falso</label>
                                    </div>
                                `);
                            }
                            function renderLacunas(){
                                cont.innerHTML = field('Frase com lacunas (use ___ para cada lacuna)', `<textarea id='lac-frase' placeholder='Ex.: O gato ___ no ___.'></textarea>`) +
                                                 field('Respostas (uma por linha, na ordem das lacunas)', `<textarea id='lac-resps' placeholder='corre\njardim'></textarea>`);
                            }
                            function renderCorrespondencia(){
                                cont.innerHTML = field('Pares (lado A ; lado B por linha)', `<textarea id='corr-pares' placeholder='Substantivo ; Palavra que nomeia\nVerbo ; Palavra que indica ação'></textarea>`)+
                                    `<small style='font-size:.6rem; color:#667;'>Os pares serão embaralhados ao exibir.</small>`;
                            }
                            function renderDiscursiva(){
                                cont.innerHTML =
                                    field('Palavras-chave esperadas (opcional, vírgulas)', '<input id="disc-keywords" placeholder="feliz,alegre" />')+
                                    field('Resposta orientadora (opcional)', '<textarea id="disc-orientacao" placeholder="Sugestão de elementos esperados..."></textarea>');
                            }
                            function renderArrastar(){
                                cont.innerHTML =
                                    field('Palavras (separadas por vírgula)', '<input id="drag-palavras" placeholder="Maria,gosta,de,ler" />')+
                                    field('Ordem correta (separada por vírgula)', '<input id="drag-ordem" placeholder="Maria,gosta,de,ler" />');
                            }
                            function render(){
                                const t = tipoSel.value;
                                opcoesHidden.value=''; respostaHidden.value='';
                                if(t==='multipla_escolha') renderMultipleChoice();
                                else if(t==='arrastar_palavras') renderArrastar();
                                else if(t==='discursiva') renderDiscursiva();
                                else if(t==='verdadeiro_falso') renderVerdadeiroFalso();
                                else if(t==='lacunas') renderLacunas();
                                else if(t==='correspondencia') renderCorrespondencia();
                                else cont.innerHTML='';
                            }
                            tipoSel.addEventListener('change', render);
                            document.getElementById('form-exercicio').addEventListener('submit', function(){
                                const t = tipoSel.value;
                                let data={};
                                if(t==='multipla_escolha'){
                                    const rows=[...document.querySelectorAll('#mc-list .mc-row')];
                                    const alternativas = rows.map(r=>r.querySelector('.mc-text').value.trim()).filter(v=>v);
                                    const radios = rows.map(r=>r.querySelector('input[type=radio]'));
                                    const idx = radios.findIndex(r=>r.checked);
                                    data.alternativas = alternativas;
                                    if(idx>=0) data.correta = idx;
                                    opcoesHidden.value = JSON.stringify(data);
                                    respostaHidden.value = idx>=0 ? alternativas[idx] : '';
                                } else if(t==='arrastar_palavras'){
                                    const palavras = (document.getElementById('drag-palavras').value||'').split(',').map(s=>s.trim()).filter(Boolean);
                                    const ordem = (document.getElementById('drag-ordem').value||'').split(',').map(s=>s.trim()).filter(Boolean);
                                    data.palavras = palavras; if(ordem.length) data.ordem = ordem; opcoesHidden.value=JSON.stringify(data); respostaHidden.value=ordem.join(' ');
                                } else if(t==='discursiva'){
                                    const keys=(document.getElementById('disc-keywords').value||'').split(',').map(s=>s.trim()).filter(Boolean);
                                    if(keys.length) data.keywords=keys; const orient=document.getElementById('disc-orientacao').value.trim(); if(Object.keys(data).length) opcoesHidden.value=JSON.stringify(data); if(orient) respostaHidden.value=orient;
                                } else if(t==='verdadeiro_falso'){
                                    const val = document.querySelector('input[name=vf]:checked'); if(val){ respostaHidden.value = val.value; opcoesHidden.value=JSON.stringify({alternativas:['verdadeiro','falso'], correta: val.value}); }
                                } else if(t==='lacunas'){
                                    const frase = document.getElementById('lac-frase').value; const respostas = (document.getElementById('lac-resps').value||'').split(/\n+/).map(s=>s.trim()).filter(Boolean); data.frase=frase; data.respostas=respostas; opcoesHidden.value=JSON.stringify(data); respostaHidden.value=respostas.join('|');
                                } else if(t==='correspondencia'){
                                    const linhas = (document.getElementById('corr-pares').value||'').split(/\n+/).map(l=>l.trim()).filter(Boolean); const pares = linhas.map(l=>{ const parts=l.split(';'); return {a:(parts[0]||'').trim(), b:(parts[1]||'').trim()}; }).filter(p=>p.a && p.b); data.pares=pares; opcoesHidden.value=JSON.stringify(data); respostaHidden.value='';
                                }
                            });
                        })();
                        </script>
                    </div>
                    <div class="edu-box">
                        <h3>Criar Tópico de Exercício</h3>
                        <form method="POST" action="/admin/edu_create_topic">
                            
                            <input name="nome" placeholder="Nome" required />
                            <textarea name="descricao" placeholder="Descrição"></textarea>
                            <button type="submit">Criar</button>
                        </form>
                    </div>
                    <div class="edu-box">
                        <h3>Criar Sessão de Exercício</h3>
                        <form method="POST" action="/admin/exercicios_create_section">
                            
                            <select name="topic_id" required>
                                <option value="">(Tópico)</option>
                                
topics_html = ""
for t in topics:
    topics_html += f"""
<option value="{t.id}">{t.nome}</option>
    """
{topics_html}

                            </select>
                            <input name="nome" placeholder="Nome da sessão" required />
                            <textarea name="descricao" placeholder="Descrição"></textarea>
                            <input name="ordem" type="number" placeholder="Ordem" />
                            <button type="submit">Criar Sessão</button>
                        </form>
                    </div>
                </div>
                <!-- Gerenciar Tópicos de Exercícios -->
                <div class="edu-box" style="margin-top:1rem;">
                    <h3>Gerenciar Tópicos de Exercícios</h3>
                    <!-- IF topics:
    END_html = f"""
<div style="display:grid; gap:.8rem; grid-template-columns:1fr;">
                            
topics_html = ""
for topic in topics:
    topics_html += f"""
<div style="background:#f9fbfd; border:1px solid #e3e9f0; border-radius:12px; padding:.9rem;">
                                <div style="display:flex; justify-content:space-between; align-items:start; gap:.8rem;">
                                    <div style="flex:1;">
                                        <div style="font-weight:700; font-size:.85rem; color:#333; margin-bottom:.3rem;">{topic.nome}</div>
                                        <!-- IF topic.descricao START -->
                                            <div style="font-size:.7rem; color:#666; margin-bottom:.5rem;">{topic.descricao}</div>
    """
{END_html}

                                    </div>
                                    <button onclick="toggleTopicEdit('exercicio-{topic.id}')" class="action-btn" style="font-size:.6rem; padding:4px 10px;">
                                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:middle;">
                                            <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
                                        </svg>
                                        Editar
                                    </button>
                                </div>
                                <div id="topic-edit-exercicio-{topic.id}" style="display:none; margin-top:.8rem; padding-top:.8rem; border-top:1px solid #e3e9f0;">
                                    <form method="POST" action="/admin/exercicios_topic_update/{topic.id}" style="display:flex; flex-direction:column; gap:.5rem;">
                                        
                                        <label style="font-size:.7rem; font-weight:600; color:#666;">Nome</label>
                                        <input name="nome" value="{topic.nome}" placeholder="Nome" style="padding:.5rem; border:1px solid #cfd7e2; border-radius:8px; font-size:.72rem;" required />
                                        <label style="font-size:.7rem; font-weight:600; color:#666;">Descrição</label>
                                        <textarea name="descricao" placeholder="Descrição" style="padding:.5rem; border:1px solid #cfd7e2; border-radius:8px; font-size:.72rem; min-height:60px;">{{ topic.descricao or '' }}</textarea>
                                        <div style="display:flex; gap:.5rem; margin-top:.3rem;">
                                            <button type="submit" class="action-btn" style="background:var(--accent); color:#fff; border:none; font-size:.65rem; padding:.5rem .9rem;">Salvar</button>
                                            <button type="button" onclick="toggleTopicEdit('exercicio-{topic.id}')" class="action-btn" style="font-size:.65rem; padding:.5rem .9rem;">Cancelar</button>
                                        </div>
                                    </form>
                                </div>
                                <!-- Gerenciar Sessões deste Tópico -->
                                {% set topic_sections = sections | selectattr('topic_id', 'equalto', topic.id) | list %}
                                
topic_sections_html = ""
if topic_sections:
    topic_sections_html = f"""
<div style="margin-top:.8rem; padding-top:.8rem; border-top:1px solid #e3e9f0;">
                                    <div style="font-size:.75rem; font-weight:600; color:#666; margin-bottom:.5rem;">Sessões deste Tópico:</div>
                                    <div style="display:flex; flex-direction:column; gap:.5rem;">
                                        <!-- FOR section IN topic_sections START -->
                                        <div style="background:#fff; border:1px solid #e3e9f0; border-radius:8px; padding:.6rem;">
                                            <div style="display:flex; justify-content:space-between; align-items:start; gap:.5rem;">
                                                <div style="flex:1;">
                                                    <div style="font-weight:600; font-size:.75rem; color:#333;">{section.nome}</div>
                                                    <!-- IF section.descricao START -->
                                                        <div style="font-size:.65rem; color:#666; margin-top:.2rem;">{section.descricao}</div>
    """
{topic_sections_html}

                                                    <div style="font-size:.6rem; color:#999; margin-top:.2rem;">Ordem: {section.ordem}</div>
                                                </div>
                                                <button onclick="toggleTopicEdit('section-{section.id}')" class="action-btn" style="font-size:.55rem; padding:3px 8px;">
                                                    Editar
                                                </button>
                                            </div>
                                            <div id="topic-edit-section-{section.id}" style="display:none; margin-top:.6rem; padding-top:.6rem; border-top:1px solid #e3e9f0;">
                                                <form method="POST" action="/admin/exercicios_section_update/{section.id}" style="display:flex; flex-direction:column; gap:.4rem;">
                                                    
                                                    <label style="font-size:.65rem; font-weight:600; color:#666;">Nome</label>
                                                    <input name="nome" value="{section.nome}" placeholder="Nome" style="padding:.4rem; border:1px solid #cfd7e2; border-radius:6px; font-size:.68rem;" required />
                                                    <label style="font-size:.65rem; font-weight:600; color:#666;">Descrição</label>
                                                    <textarea name="descricao" placeholder="Descrição" style="padding:.4rem; border:1px solid #cfd7e2; border-radius:6px; font-size:.68rem; min-height:50px;">{{ section.descricao or '' }}</textarea>
                                                    <label style="font-size:.65rem; font-weight:600; color:#666;">Ordem</label>
                                                    <input name="ordem" type="number" value="{section.ordem}" placeholder="Ordem" style="padding:.4rem; border:1px solid #cfd7e2; border-radius:6px; font-size:.68rem;" />
                                                    <div style="display:flex; gap:.4rem; margin-top:.2rem;">
                                                        <button type="submit" class="action-btn" style="background:var(--accent); color:#fff; border:none; font-size:.6rem; padding:.4rem .7rem;">Salvar</button>
                                                        <button type="button" onclick="toggleTopicEdit('section-{section.id}')" class="action-btn" style="font-size:.6rem; padding:.4rem .7rem;">Cancelar</button>
                                                    </div>
                                                </form>
                                            </div>
                                        </div>
    """
{topics_html}

                                    </div>
                                </div>
                                
if END -->
                            </div>
                            <!-- FOR END -->
                        </div>
                    <!-- ELSE -->
                        <p class="muted-inline">Nenhum tópico criado ainda.</p>
                    <!-- IF END -->
                </div>
            </div>
            <!-- Vídeos -->
            <div class="edu-area-section" id="area-videos">
                <div class="edu-two-col">
                    <div class="edu-box">
                        <h3>Publicar Vídeo</h3>
                        <form method="POST" action="/admin/edu_publicar" enctype="multipart/form-data">
                            <input type="hidden" name="tipo" value="video" />
                            <input name="titulo" placeholder="Título" required />
                            <input name="autor" placeholder="Autore (opcional)" />
                            <select name="topic_id">
                                <option value="">(Tópico)</option>
                                {% for t in edu_topics if t.area=='video' %}<option value="{t.id}">{t.nome}</option><!-- FOR END -->
                            </select>
                            <input name="url" id="video-url" placeholder="Link do vídeo (YouTube, Vimeo, TikTok...)" required />
                            <div id="video-preview" style="margin-top:.6rem; padding:.6rem; border:1px dashed #cfd7e2; border-radius:10px; background:#f9fbfd; display:none;"></div>
                            <label style="font-size:.62rem; font-weight:600; text-transform:uppercase; letter-spacing:.55px; color:#48515c; margin-top:.5rem;">Thumb (opcional)</label>
                            <input type="file" name="thumb" id="video-thumb" accept="image/png,image/jpeg,image/webp,image/gif" />
                            <div id="video-thumb-preview" style="display:none; margin-top:.4rem;"></div>
                            <textarea name="resumo" placeholder="Descrição (opcional)"></textarea>
                            <button type="submit">Publicar</button>
                        </form>
                        <script>
                        (function(){
                            const input = document.getElementById('video-url');
                            const box = document.getElementById('video-preview');
                            if(!input || !box) return;
                            function ensureTikTokScript(){
                                if(document.querySelector('script[src="https://www.tiktok.com/embed.js"]')) return;
                                const s = document.createElement('script'); s.src='https://www.tiktok.com/embed.js'; s.async=true; document.body.appendChild(s);
                            }
                            function extractYouTube(val){
                                // iframe src
                                let m = val.match(/src=\"https?:\/\/(?:www\.)?youtube\.com\/(?:embed|shorts)\/([A-Za-z0-9_-]{6,})/);
                                if(m) return m[1];
                                // watch?v=
                                m = val.match(/youtube\.com\/watch\?[^\s]*v=([A-Za-z0-9_-]{6,})/);
                                if(m) return m[1];
                                // youtu.be/
                                m = val.match(/youtu\.be\/([A-Za-z0-9_-]{6,})/);
                                if(m) return m[1];
                                // embed/
                                m = val.match(/youtube\.com\/embed\/([A-Za-z0-9_-]{6,})/);
                                if(m) return m[1];
                                // shorts/
                                m = val.match(/youtube\.com\/shorts\/([A-Za-z0-9_-]{6,})/);
                                if(m) return m[1];
                                return null;
                            }
                            function extractVimeo(val){
                                // player.vimeo.com/video/12345
                                let m = val.match(/player\.vimeo\.com\/video\/(\d+)/);
                                if(m) return m[1];
                                // vimeo.com/12345
                                m = val.match(/vimeo\.com\/(?:video\/)?(\d+)/);
                                if(m) return m[1];
                                return null;
                            }
                            function extractTikTok(val){
                                const m = val.match(/tiktok\.com\/@[\w\.-]+\/video\/(\d+)/);
                                if(m) return val; // retorna a URL inteira
                                // iframe src? (TikTok geralmente usa blockquote, mas se vier src direto, mantém a URL)
                                const m2 = val.match(/src=\"(https?:\/\/www\.tiktok\.com\/[^"]+)\"/);
                                if(m2) return m2[1];
                                return null;
                            }
                            function render(){
                                const val = (input.value||'').trim();
                                if(!val){ box.style.display='none'; box.innerHTML=''; return; }
                                const yt = extractYouTube(val);
                                if(yt){
                                    const src = `https://www.youtube.com/embed/${yt}`;
                                    box.innerHTML = `<iframe style="width:100%; aspect-ratio:16/9; border:0; border-radius:12px; background:#000;" src="${src}" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen loading="lazy"></iframe>`;
                                    box.style.display='block'; return;
                                }
                                const vm = extractVimeo(val);
                                if(vm){
                                    const src = `https://player.vimeo.com/video/${vm}`;
                                    box.innerHTML = `<iframe style="width:100%; aspect-ratio:16/9; border:0; border-radius:12px; background:#000;" src="${src}" allow="autoplay; fullscreen; picture-in-picture" allowfullscreen loading="lazy"></iframe>`;
                                    box.style.display='block'; return;
                                }
                                const tk = extractTikTok(val);
                                if(tk){
                                    ensureTikTokScript();
                                    box.innerHTML = `<blockquote class="tiktok-embed" cite="${tk}" style="max-width: 605px;min-width: 325px;"><section>Veja no TikTok: <a href="${tk}" target="_blank" rel="noopener">Abrir</a>
"""

GRAMATIKE_TAB_HTML = f"""
<h2 style="margin-top:0;">Gramátike</h2>
            <div class="cards-grid">
                <div class="card" id="card-suporte" style="position:relative;">
                    <h4 style="display:flex;align-items:center;gap:.5rem;">Suporte <span id="badge-suporte" style="display:none;background:#ff9800;color:#fff;font-size:.6rem;padding:.2rem .45rem;border-radius:40px;letter-spacing:.5px;">0</span></h4>
                    <p class="small-muted">Tickets enviados peles usuáries.</p>
                    <a href="/admin/suporte" class="action-btn" style="margin-top:.4rem;display:inline-block;">Abrir painel</a>
                    <script>
                    // Fetch rápido para contar tickets (limite 1 requisição simples)
                    fetch('/admin/suporte').then(r=>r.text()).then(html=>{
                        const matches = html.match(/class=\"ticket\"/g) || [];
                        const count = matches.length;
                        if(count>0){
                            const b=document.getElementById('badge-suporte');
                            if(b){ b.textContent=count; b.style.display='inline-block'; }
                        }
                    }).catch(()=>{});
                    </script>
                </div>
                <div class="card" style="grid-column:1/-1;">
                    <h4>Denúncias</h4>
                    <table class="admin-usuaries" style="font-size:.7rem;">
                        <thead>
                            <tr><th>ID</th><th>Post</th><th>Autor</th><th>Denunciante</th><th>Motivo</th><th>Categoria</th><th>Data</th><th>Status</th><th>Ações</th></tr>
                        </thead>
                        <tbody>
                        
reports_html = ""
for r in reports:
    reports_html += f"""
<tr>
                                <td>{r.id}</td>
                                <td>#{r.post_id}</td>
                                <td>{{ r.post.usuarie if r.post else '?' }}</td>
                                <td>{{ r.usuarie.username if r.usuario else '?' }}</td>
                                <td>{r.motivo}</td>
                                <td>
                                    <!-- IF r.category:
    END_html = f"""
{% set cat = r.category.lower() %}
                                        <!-- IF cat in ['odio','ódio'] START -->
                                            <span class="badge" style="background:#8b0000;color:#fff;">Ódio</span>
                                        <!-- ELIF cat == 'violencia' or cat == 'violência' -->
                                            <span class="badge" style="background:#b23a48;color:#fff;">Violência</span>
                                        <!-- ELIF cat == 'assedio' or cat == 'assédio' -->
                                            <span class="badge" style="background:#a66bbe;color:#fff;">Assédio</span>
                                        <!-- ELIF cat == 'nudez' -->
                                            <span class="badge" style="background:#d97706;color:#fff;">Nudez</span>
                                        <!-- ELIF cat == 'spam' -->
                                            <span class="badge" style="background:#0ea5e9;color:#fff;">Spam</span>
                                        <!-- ELIF cat == 'suicidio' or cat == 'suicídio' -->
                                            <span class="badge" style="background:#374151;color:#fff;">Autoextermínio</span>
    """
else:
    END_html = f"""
<span class="badge">{r.category}</span>
    """
{END_html}

                                    <!-- ELSE -->—
if END -->
                                </td>
                                <td>{{ r.data.strftime('%d/%m %H:%M') }}</td>
                                <td><!-- IF r.resolved:
    END_html = f"""
<span class="badge" style="background:#4caf50;color:#fff;">Resolvida</span>
    """
else:
    END_html = f"""
<span class="badge" style="background:#ff9800;color:#fff;">Aberta</span>
    """
{END_html}
</td>
                                <td>
                                    
not_html = ""
if not r.resolved:
    not_html = f"""
<form class="inline" method="POST" action="/admin/resolve_report/{r.id}">
                                            
                                            <button type="submit" class="action-btn">Resolver</button>
                                        </form>
                                        <form class="inline" method="POST" action="/admin/delete_report_post/{r.id}" onsubmit="return confirm('Excluir post #{r.post_id}?');">
                                            
                                            <button type="submit" class="action-btn danger">Excluir Post</button>
                                        </form>
                                        <!-- IF r.post and r.post.usuario_id START -->
                                        <form class="inline" method="POST" action="/admin/ban_user/{r.post.usuario_id}" onsubmit="return confirm('Banir autore do post #{r.post_id}?');">
                                            
                                            <input type="hidden" name="reason" value="Denúncia: {{ r.category or 'violação' }}" />
                                            <button type="submit" class="action-btn danger">Banir Autor</button>
                                        </form>
                                        <form class="inline" method="POST" action="/admin/suspend_user/{r.post.usuario_id}">
                                            
                                            <input type="hidden" name="hours" value="24" />
                                            <button type="submit" class="action-btn">Suspender 24h</button>
                                        </form>
    """
{not_html}

                                    <!-- ELSE --><span class="muted">—</span>
END_html = ""
if END -->
                                </td>
                            </tr>
                        <!-- ELSE -->
                            <tr><td colspan="9" class="muted">Nenhuma denúncia.</td></tr>
    """
{reports_html}

                        </tbody>
                    </table>
                    <!-- IF reports_pagination:
    END_html = f"""
<div style="margin-top:1rem; display:flex; gap:0.5rem; justify-content:center; align-items:center;">
                        <!-- IF reports_pagination.has_prev START -->
                        <a href="/admin/dashboard/{reports_pagination.prev_num, _anchor='gramatike'}" class="action-btn">← Anterior</a>
    """
{END_html}

                        <span style="font-size:0.75rem; color:var(--text-soft);">Página {reports_pagination.page} de {reports_pagination.pages}</span>
                        
reports_pagination_html = ""
if reports_pagination.has_next:
    reports_pagination_html = f"""
<a href="/admin/dashboard/{reports_pagination.next_num, _anchor='gramatike'}" class="action-btn">Próxima →</a>
    """
{reports_pagination_html}

                    </div>
                    <!-- IF END -->
                </div>
            </div>
"""

ADMIN_JAVASCRIPT = """
// Placeholder simples em memória para avisos até existir backend
            (function(){
                const store = [];
                const listEl = document.getElementById('publiAvisos');
                function render(){
                    if(!listEl) return;
                    if(store.length===0){
                        listEl.className='lista-avisos-vazia';
                        listEl.innerHTML = `<span class='muted' style="font-size:.62rem;">${listEl.getAttribute('data-empty-msg')}</span>`;
                        return;
                    }
                    listEl.className='lista-avisos';
                    listEl.innerHTML = store.map(a=>{
                        return `<div class=\"aviso-item\" role=\"listitem\"><div class=\"aviso-head\"><strong>${a.titulo}</strong><time>${a.ts.toLocaleString('pt-BR')}</time></div><p>${a.mensagem}</p></div>`;
                    }).join('');
                }
                window.addPubliAviso = function(form){
                    const titulo = form.titulo.value.trim();
                    const mensagem = form.mensagem.value.trim();
                    if(!titulo || !mensagem) return;
                    store.unshift({titulo, mensagem, ts:new Date()});
                    form.reset();
                    render();
                };
                render();
            })();

// Initialize Quill editor for Novidade
                var novidadeQuill = new Quill('#novidade-editor-container', {
                    theme: 'snow',
                    modules: {
                        toolbar: [
                            [{ 'header': [1, 2, 3, false] }],
                            ['bold', 'italic', 'underline'],
                            [{ 'list': 'ordered'}, { 'list': 'bullet' }],
                            ['link'],
                            ['clean']
                        ]
                    },
                    placeholder: 'Escreva a descrição da novidade...'
                });
                
                // Update hidden input on form submit
                document.getElementById('formNovidadeGmtk').addEventListener('submit', function() {
                    document.getElementById('novidade-descricao-input').value = novidadeQuill.root.innerHTML;
                });
                
                // Palavra do Dia - Listar
                async function carregarPalavrasDoDia() {
                    const container = document.getElementById('lista-palavras-do-dia');
                    if (!container) return;
                    
                    try {
                        const res = await fetch('/admin/palavra-do-dia/list');
                        const palavras = await res.json();
                        
                        if (!palavras.length) {
                            container.innerHTML = '<div style="text-align:center; color:#999; font-size:.7rem;">Nenhuma palavra cadastrada</div>';
                            return;
                        }
                        
                        container.innerHTML = palavras.map(p => `
                            <div style="border:1px solid #e3e9f0; border-radius:10px; padding:.7rem; background:#f9fbfd; display:flex; justify-content:space-between; align-items:center;">
                                <div style="flex:1;">
                                    <div style="font-weight:700; font-size:.85rem;">${p.palavra}</div>
                                    <div style="font-size:.65rem; color:#666; margin-top:.2rem;">${p.significado}</div>
                                    <div style="font-size:.6rem; color:#999; margin-top:.3rem;">
                                        Ordem: ${p.ordem} | ${p.ativo ? '✅ Ativa' : '❌ Inativa'} | Interações: ${p.interacoes_count || 0}
                                    </div>
                                </div>
                                <div style="display:flex; gap:.4rem;">
                                    <form method="POST" action="/admin/palavra-do-dia/${p.id}/toggle" style="display:inline;">
                                        <input type="hidden" name="csrf_token" value="{{ csrf_token() if csrf_token is defined else '' }}" />
                                        <button type="submit" class="action-btn" style="font-size:.6rem;">
                                            ${p.ativo ? 'Desativar' : 'Ativar'}
                                        </button>
                                    </form>
                                    <form method="POST" action="/admin/palavra-do-dia/${p.id}/delete" onsubmit="return confirm('Excluir esta palavra?');" style="display:inline;">
                                        <input type="hidden" name="csrf_token" value="{{ csrf_token() if csrf_token is defined else '' }}" />
                                        <button type="submit" class="action-btn danger" style="font-size:.6rem;">Excluir</button>
                                    </form>
                                </div>
                            </div>
                        `).join('');
                    } catch (e) {
                        container.innerHTML = '<div style="text-align:center; color:#f44; font-size:.7rem;">Erro ao carregar</div>';
                    }
                }
                
                // Palavra do Dia - Respostas
                window.carregarRespostasPalavras = async function() {
                    const container = document.getElementById('lista-respostas-palavras');
                    const palavraId = document.getElementById('filtro-palavra-id').value.trim();
                    if (!container) return;
                    
                    container.innerHTML = '<div style="text-align:center; color:#999; font-size:.7rem;">Carregando...</div>';
                    
                    try {
                        const url = '/admin/palavra-do-dia/respostas' + (palavraId ? `?palavra_id=${palavraId}` : '');
                        const res = await fetch(url);
                        const respostas = await res.json();
                        
                        if (!respostas.length) {
                            container.innerHTML = '<div style="text-align:center; color:#999; font-size:.7rem;">Nenhuma resposta encontrada</div>';
                            return;
                        }
                        
                        container.innerHTML = respostas.map(r => `
                            <div style="border:1px solid #e3e9f0; border-radius:10px; padding:.7rem; background:#fff;">
                                <div style="display:flex; justify-content:space-between; margin-bottom:.4rem;">
                                    <div style="font-weight:700; font-size:.75rem;">${r.palavra}</div>
                                    <div style="font-size:.65rem; color:#999;">${r.data}</div>
                                </div>
                                <div style="font-size:.7rem; color:#666; margin-bottom:.3rem;">
                                    <strong>Usuárie:</strong> ${r.usuario} | <strong>Tipo:</strong> ${r.tipo === 'frase' ? 'Frase' : 'Significado'}
                                </div>
                                ${r.frase ? `<div style="font-size:.7rem; color:#333; background:#f1edff; padding:.5rem; border-radius:8px; margin-top:.4rem;">"${r.frase}"</div>` : ''}
                            </div>
                        `).join('');
                    } catch (e) {
                        container.innerHTML = '<div style="text-align:center; color:#f44; font-size:.7rem;">Erro ao carregar</div>';
                    }
                }
                
                // Carregar palavras ao mostrar a seção
                document.addEventListener('DOMContentLoaded', () => {
                    const btns = document.querySelectorAll('.edu-area-btn');
                    btns.forEach(btn => {
                        btn.addEventListener('click', () => {
                            if (btn.dataset.area === 'gramatike') {
                                setTimeout(carregarPalavrasDoDia, 100);
                            }
                        });
                    });
                });

(function(){
                            const input = document.getElementById('podcast-url');
                            const box = document.getElementById('podcast-preview');
                            if(!input || !box) return;
                            function extractSpotifyId(val){
                                // Se for iframe, extrai src
                                const mIframe = val.match(/src=\"https?:\/\/open\.spotify\.com\/embed\/(episode|show)\/([A-Za-z0-9]+)[^\"]*\"/);
                                if(mIframe) return { kind: mIframe[1], id: mIframe[2] };
                                // Se for link comum
                                const mLink = val.match(/spotify\.com\/(episode|show)\/([A-Za-z0-9]+)/);
                                if(mLink) return { kind: mLink[1], id: mLink[2] };
                                return null;
                            }
                            function render(){
                                const val = (input.value||'').trim();
                                if(!val){ box.style.display='none'; box.innerHTML=''; return; }
                                // Spotify
                                const sp = extractSpotifyId(val);
                                if(sp){
                                    const embed = `https://open.spotify.com/embed/${sp.kind}/${sp.id}?utm_source=generator`;
                                    box.innerHTML = `<iframe data-testid="embed-iframe" style="border-radius:12px; width:100%;" src="${embed}" width="100%" height="352" frameBorder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>`;
                                    box.style.display='block';
                                    return;
                                }
                                // MP3
                                if(/\.mp3($|\?)/i.test(val)){
                                    box.innerHTML = `<audio controls preload="none" style="width:100%"><source src="${val}" type="audio/mpeg" />Seu navegador não suporta áudio.</audio>`;
                                    box.style.display='block';
                                    return;
                                }
                                // Outro: limpa preview
                                box.style.display='none';
                                box.innerHTML='';
                            }
                            input.addEventListener('input', render);
                            input.addEventListener('change', render);
                            input.addEventListener('paste', ()=>setTimeout(render, 0));
                        })();

(function(){
                            const ul = document.getElementById('lista-podcasts');
                            const q = document.getElementById('busca-podcasts');
                            function cardTemplate(i){
                                return `
                                    <li class="card" style="padding:.7rem .8rem; border:1px solid #e1e7ef; border-radius:10px; background:#fff; display:flex; flex-direction:column; gap:.5rem;">
                                        <div style="font-weight:700; font-size:.85rem;">${i.titulo}</div>
                                        <div class="small-muted">${i.topic || ''}</div>
                                        <div class="podcast-player" data-id="${i.id}" style="border:1px dashed #cfd7e2; border-radius:10px; padding:.5rem; background:#f9fbfd;"></div>
                                        <div style="display:flex; gap:.4rem;">
                                            <button class="action-btn" data-edit="${i.id}">Editar</button>
                                            <form method="POST" action="/admin/edu/content/${i.id}/delete" onsubmit="return confirm('Excluir este podcast?');">
                                                <button type="submit" class="action-btn danger">Excluir</button>
                                            </form>
                                        </div>
                                    </li>
                                `;
                            }
                            function render(items){
                                if(!ul) return;
                                if(!items.length){ ul.innerHTML = '<li class="muted">Nenhum resultado.</li>'; return; }
                                ul.innerHTML = items.map(cardTemplate).join('');
                                // Carrega players
                                const nodes = ul.querySelectorAll('.podcast-player');
                                nodes.forEach(async (node)=>{
                                    const id = node.getAttribute('data-id');
                                    try{
                                        const data = await fetch(`/admin/edu/content/${id}.json`).then(r=>r.json());
                                        let html = '';
                                        const embed = data.extra && data.extra.spotify_embed;
                                        if(embed){
                                            html = `<iframe data-testid="embed-iframe" style="border-radius:12px; width:100%;" src="${embed}" width="100%" height="352" frameBorder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>`;
                                        } else if(data.url && /\.mp3($|\?)/i.test(data.url)){
                                            html = `<audio controls preload="none" style="width:100%"><source src="${data.url}" type="audio/mpeg" />Seu navegador não suporta áudio.</audio>`;
                                        } else {
                                            html = '<div class="small-muted">Sem player disponível</div>';
                                        }
                                        node.innerHTML = html;
                                    }catch(e){ node.innerHTML = '<div class="small-muted">Erro ao carregar</div>'; }
                                });
                            }
                            async function buscar(term=''){
                                try{
                                    const url = new URL("{{ url_for('admin.edu_buscar') }}", location.origin);
                                    url.searchParams.set('area','podcasts'); if(term) url.searchParams.set('q',term);
                                    const r = await fetch(url); const j = await r.json(); render(j.results||[]);
                                }catch(e){ render([]); }
                            }
                            document.getElementById('btn-buscar-podcasts')?.addEventListener('click', ()=>buscar(q.value.trim()));
                            q?.addEventListener('keydown', e=>{ if(e.key==='Enter'){ e.preventDefault(); buscar(q.value.trim()); } });
                            buscar('');

                            // Edição de podcast
                            const dlg = document.getElementById('podcastEditDialog');
                            const form = document.getElementById('podcastEditForm');
                            const pe_id = document.getElementById('pe_id');
                            const pe_titulo = document.getElementById('pe_titulo');
                            const pe_resumo = document.getElementById('pe_resumo');
                            const pe_url = document.getElementById('pe_url');
                            const pe_topic = document.getElementById('pe_topic');
                            const pe_cancel = document.getElementById('pe_cancel');
                            const pe_autor = document.getElementById('pe_autor');

                            ul.addEventListener('click', async (e)=>{
                                const btn = e.target.closest('button[data-edit]');
                                if(!btn) return;
                                const id = btn.getAttribute('data-edit');
                                try{
                                    const data = await fetch(`/admin/edu/content/${id}.json`).then(r=>r.json());
                                    pe_id.value = data.id;
                                    pe_titulo.value = data.titulo||'';
                                    pe_resumo.value = data.resumo||'';
                                    pe_autor.value = (data.extra && data.extra.author) ? data.extra.author : '';
                                    pe_url.value = data.url||'';
                                    pe_topic.innerHTML = '';
                                    const srcSelect = document.querySelector('#area-podcasts select[name="topic_id"]');
                                    if(srcSelect){
                                        for(const opt of srcSelect.options){
                                            const o = document.createElement('option'); o.value = opt.value; o.textContent = opt.textContent;
                                            if(String(opt.value) === String(data.topic_id||'')) o.selected = true;
                                            pe_topic.appendChild(o);
                                        }
                                    }
                                    dlg.showModal();
                                }catch(err){ alert('Falha ao carregar dados'); }
                            });
                            pe_cancel.addEventListener('click', ()=> dlg.close());
                            form.addEventListener('submit', async (e)=>{
                                e.preventDefault();
                                const id = pe_id.value;
                                const fd = new FormData(form);
                                try{
                                    const res = await fetch(`/admin/edu/content/${id}/update`, { method:'POST', body: fd, credentials: 'same-origin' });
                                    if(res.ok){ dlg.close(); buscar(q.value.trim()); } else { alert('Falha ao salvar'); }
                                }catch(err){ alert('Erro de rede'); }
                            });
                        })();

{{ sections_map|tojson }}

// Parse dos dados de sessões por tópico
                                                                        let sectionsData = {};
                                                                        try { sectionsData = JSON.parse(document.getElementById('sections-data').textContent); } catch(e){ sectionsData = {}; }

(function(){
                            const tipoSel = document.getElementById('ex-tipo');
                            const cont = document.getElementById('ex-campos');
                            const opcoesHidden = document.getElementById('ex-opcoes');
                            const respostaHidden = document.getElementById('ex-resposta');
                                                        const topicSel = document.getElementById('ex-topic');
                                                        const sectionSel = document.getElementById('ex-section');
                                                        function updateSections(){
                                                                if(!topicSel) return;
                                                                const tid = topicSel.value;
                                                                const list = sectionsData[tid] || [];
                                                                sectionSel.innerHTML = '<option value="">Sessão</option>' + list.map(s=>`<option value="${s.id}">${s.nome}</option>`).join('');
                                                                sectionSel.style.display = list.length ? 'block' : 'none';
                                                        }
                                                        topicSel?.addEventListener('change', updateSections);
                                                        updateSections();
                            function field(label, html, extra=''){
                                return `<div class='ex-field' style=\"display:flex; flex-direction:column; gap:.35rem;\" ${extra}>`+
                                       `<label style='font-size:.62rem; font-weight:600; text-transform:uppercase; letter-spacing:.55px; color:#48515c;'>${label}</label>`+
                                       `${html}</div>`;
                            }
                            // UI helpers para múltipla escolha
                            function renderMultipleChoice(){
                                cont.innerHTML = '';
                                cont.insertAdjacentHTML('beforeend', field('Alternativas', `
                                    <div id='mc-list' style='display:flex; flex-direction:column; gap:.4rem;'></div>
                                    <button type='button' id='mc-add' style='align-self:flex-start; background:#eef2ff; color:#334; padding:6px 10px; font-size:.65rem; border-radius:6px; border:1px solid #c5d0f5;'>+ Adicionar alternativa</button>
                                    <small style='font-size:.6rem; color:#667;'>Marque a correta no círculo. Use o ícone ☰ para arrastar. Tecle Enter no último campo para adicionar outra.</small>
                                `));
                                const list = document.getElementById('mc-list');
                                const addBtn = document.getElementById('mc-add');
                                let counter = 0;
                                function addOption(text=''){ 
                                    const id = 'opt_'+(counter++); 
                                    const row = document.createElement('div');
                                    row.className='mc-row';
                                    row.style.cssText='display:flex; align-items:center; gap:.5rem; background:#f7f9fd; padding:6px 8px; border:1px solid #d5dde8; border-radius:8px;';
                                    row.style.display='grid';
                                    row.style.gridTemplateColumns='24px 1fr 40px 40px';
                                    row.style.alignItems='center';
                                    row.style.columnGap='8px';
                                    row.innerHTML = `
                                        <span class='drag-handle' draggable='true' title='Arrastar' style='cursor:grab; font-size:.95rem; color:#53606d;'>☰</span>
                                        <input type='text' class='mc-text' placeholder='Digite a alternativa' value="${text.replace(/"/g,'&quot;')}" style='width:100%; padding:.55rem .65rem; border:1px solid #7d94aa; background:#fff; color:#1d2b38; border-radius:7px; font-size:.8rem; line-height:1.25; font-family:inherit; letter-spacing:.15px;' />
                                        <input type='radio' name='mc-correta' style='margin:0 auto; transform:scale(1.15); cursor:pointer;' aria-label='Marcar correta' />
                                        <button type='button' class='mc-del' title='Excluir' aria-label='Excluir alternativa' style='background:#fff; border:1px solid #d3dbe3; border-radius:7px; width:34px; height:34px; display:flex; align-items:center; justify-content:center; font-size:.8rem; cursor:pointer; color:#c62828; font-weight:600;'>×</button>`;
                                    list.appendChild(row);
                                    // Ao pressionar Enter neste input e for o último, cria nova opção
                                    const input = row.querySelector('.mc-text');
                                    input.addEventListener('keydown', ev=>{
                                        if(ev.key==='Enter'){
                                            ev.preventDefault();
                                            const rows=[...list.querySelectorAll('.mc-row .mc-text')];
                                            if(rows[rows.length-1]===input){ addOption(); setTimeout(()=>list.querySelector('.mc-row:last-child .mc-text').focus(),10); }
                                        }
                                    });
                                }
                                addBtn.addEventListener('click',()=>addOption());
                                // iniciar com 3
                                addOption(); addOption(); addOption();
                                // Delegação delete
                                list.addEventListener('click', e=>{
                                    if(e.target.classList.contains('mc-del')){
                                        const row = e.target.closest('.mc-row');
                                        row.remove();
                                    }
                                });
                                // Drag & drop reorder
                                let dragSrc;
                                list.addEventListener('dragstart', e=>{
                                    if(e.target.classList.contains('drag-handle')){ dragSrc=e.target.closest('.mc-row'); e.dataTransfer.effectAllowed='move'; }
                                });
                                list.addEventListener('dragover', e=>{ e.preventDefault(); });
                                list.addEventListener('drop', e=>{
                                    e.preventDefault();
                                    const tgt = e.target.closest('.mc-row');
                                    if(dragSrc && tgt && dragSrc!==tgt){
                                        const children=[...list.children];
                                        const srcIndex=children.indexOf(dragSrc);
                                        const tgtIndex=children.indexOf(tgt);
                                        if(srcIndex < tgtIndex) list.insertBefore(dragSrc, tgt.nextSibling); else list.insertBefore(dragSrc, tgt);
                                    }
                                });
                            }
                            function renderVerdadeiroFalso(){
                                cont.innerHTML = field('Resposta Correta', `
                                    <div style='display:flex; gap:1rem; font-size:.7rem;'>
                                        <label style='display:flex; align-items:center; gap:.35rem;'><input type='radio' name='vf' value='verdadeiro' required />Verdadeiro</label>
                                        <label style='display:flex; align-items:center; gap:.35rem;'><input type='radio' name='vf' value='falso' required />Falso</label>
                                    </div>
                                `);
                            }
                            function renderLacunas(){
                                cont.innerHTML = field('Frase com lacunas (use ___ para cada lacuna)', `<textarea id='lac-frase' placeholder='Ex.: O gato ___ no ___.'></textarea>`) +
                                                 field('Respostas (uma por linha, na ordem das lacunas)', `<textarea id='lac-resps' placeholder='corre\njardim'></textarea>`);
                            }
                            function renderCorrespondencia(){
                                cont.innerHTML = field('Pares (lado A ; lado B por linha)', `<textarea id='corr-pares' placeholder='Substantivo ; Palavra que nomeia\nVerbo ; Palavra que indica ação'></textarea>`)+
                                    `<small style='font-size:.6rem; color:#667;'>Os pares serão embaralhados ao exibir.</small>`;
                            }
                            function renderDiscursiva(){
                                cont.innerHTML =
                                    field('Palavras-chave esperadas (opcional, vírgulas)', '<input id="disc-keywords" placeholder="feliz,alegre" />')+
                                    field('Resposta orientadora (opcional)', '<textarea id="disc-orientacao" placeholder="Sugestão de elementos esperados..."></textarea>');
                            }
                            function renderArrastar(){
                                cont.innerHTML =
                                    field('Palavras (separadas por vírgula)', '<input id="drag-palavras" placeholder="Maria,gosta,de,ler" />')+
                                    field('Ordem correta (separada por vírgula)', '<input id="drag-ordem" placeholder="Maria,gosta,de,ler" />');
                            }
                            function render(){
                                const t = tipoSel.value;
                                opcoesHidden.value=''; respostaHidden.value='';
                                if(t==='multipla_escolha') renderMultipleChoice();
                                else if(t==='arrastar_palavras') renderArrastar();
                                else if(t==='discursiva') renderDiscursiva();
                                else if(t==='verdadeiro_falso') renderVerdadeiroFalso();
                                else if(t==='lacunas') renderLacunas();
                                else if(t==='correspondencia') renderCorrespondencia();
                                else cont.innerHTML='';
                            }
                            tipoSel.addEventListener('change', render);
                            document.getElementById('form-exercicio').addEventListener('submit', function(){
                                const t = tipoSel.value;
                                let data={};
                                if(t==='multipla_escolha'){
                                    const rows=[...document.querySelectorAll('#mc-list .mc-row')];
                                    const alternativas = rows.map(r=>r.querySelector('.mc-text').value.trim()).filter(v=>v);
                                    const radios = rows.map(r=>r.querySelector('input[type=radio]'));
                                    const idx = radios.findIndex(r=>r.checked);
                                    data.alternativas = alternativas;
                                    if(idx>=0) data.correta = idx;
                                    opcoesHidden.value = JSON.stringify(data);
                                    respostaHidden.value = idx>=0 ? alternativas[idx] : '';
                                } else if(t==='arrastar_palavras'){
                                    const palavras = (document.getElementById('drag-palavras').value||'').split(',').map(s=>s.trim()).filter(Boolean);
                                    const ordem = (document.getElementById('drag-ordem').value||'').split(',').map(s=>s.trim()).filter(Boolean);
                                    data.palavras = palavras; if(ordem.length) data.ordem = ordem; opcoesHidden.value=JSON.stringify(data); respostaHidden.value=ordem.join(' ');
                                } else if(t==='discursiva'){
                                    const keys=(document.getElementById('disc-keywords').value||'').split(',').map(s=>s.trim()).filter(Boolean);
                                    if(keys.length) data.keywords=keys; const orient=document.getElementById('disc-orientacao').value.trim(); if(Object.keys(data).length) opcoesHidden.value=JSON.stringify(data); if(orient) respostaHidden.value=orient;
                                } else if(t==='verdadeiro_falso'){
                                    const val = document.querySelector('input[name=vf]:checked'); if(val){ respostaHidden.value = val.value; opcoesHidden.value=JSON.stringify({alternativas:['verdadeiro','falso'], correta: val.value}); }
                                } else if(t==='lacunas'){
                                    const frase = document.getElementById('lac-frase').value; const respostas = (document.getElementById('lac-resps').value||'').split(/\n+/).map(s=>s.trim()).filter(Boolean); data.frase=frase; data.respostas=respostas; opcoesHidden.value=JSON.stringify(data); respostaHidden.value=respostas.join('|');
                                } else if(t==='correspondencia'){
                                    const linhas = (document.getElementById('corr-pares').value||'').split(/\n+/).map(l=>l.trim()).filter(Boolean); const pares = linhas.map(l=>{ const parts=l.split(';'); return {a:(parts[0]||'').trim(), b:(parts[1]||'').trim()}; }).filter(p=>p.a && p.b); data.pares=pares; opcoesHidden.value=JSON.stringify(data); respostaHidden.value='';
                                }
                            });
                        })();

(function(){
                            const input = document.getElementById('video-url');
                            const box = document.getElementById('video-preview');
                            if(!input || !box) return;
                            function ensureTikTokScript(){
                                if(document.querySelector('script[src="https://www.tiktok.com/embed.js"]')) return;
                                const s = document.createElement('script'); s.src='https://www.tiktok.com/embed.js'; s.async=true; document.body.appendChild(s);
                            }
                            function extractYouTube(val){
                                // iframe src
                                let m = val.match(/src=\"https?:\/\/(?:www\.)?youtube\.com\/(?:embed|shorts)\/([A-Za-z0-9_-]{6,})/);
                                if(m) return m[1];
                                // watch?v=
                                m = val.match(/youtube\.com\/watch\?[^\s]*v=([A-Za-z0-9_-]{6,})/);
                                if(m) return m[1];
                                // youtu.be/
                                m = val.match(/youtu\.be\/([A-Za-z0-9_-]{6,})/);
                                if(m) return m[1];
                                // embed/
                                m = val.match(/youtube\.com\/embed\/([A-Za-z0-9_-]{6,})/);
                                if(m) return m[1];
                                // shorts/
                                m = val.match(/youtube\.com\/shorts\/([A-Za-z0-9_-]{6,})/);
                                if(m) return m[1];
                                return null;
                            }
                            function extractVimeo(val){
                                // player.vimeo.com/video/12345
                                let m = val.match(/player\.vimeo\.com\/video\/(\d+)/);
                                if(m) return m[1];
                                // vimeo.com/12345
                                m = val.match(/vimeo\.com\/(?:video\/)?(\d+)/);
                                if(m) return m[1];
                                return null;
                            }
                            function extractTikTok(val){
                                const m = val.match(/tiktok\.com\/@[\w\.-]+\/video\/(\d+)/);
                                if(m) return val; // retorna a URL inteira
                                // iframe src? (TikTok geralmente usa blockquote, mas se vier src direto, mantém a URL)
                                const m2 = val.match(/src=\"(https?:\/\/www\.tiktok\.com\/[^"]+)\"/);
                                if(m2) return m2[1];
                                return null;
                            }
                            function render(){
                                const val = (input.value||'').trim();
                                if(!val){ box.style.display='none'; box.innerHTML=''; return; }
                                const yt = extractYouTube(val);
                                if(yt){
                                    const src = `https://www.youtube.com/embed/${yt}`;
                                    box.innerHTML = `<iframe style="width:100%; aspect-ratio:16/9; border:0; border-radius:12px; background:#000;" src="${src}" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen loading="lazy"></iframe>`;
                                    box.style.display='block'; return;
                                }
                                const vm = extractVimeo(val);
                                if(vm){
                                    const src = `https://player.vimeo.com/video/${vm}`;
                                    box.innerHTML = `<iframe style="width:100%; aspect-ratio:16/9; border:0; border-radius:12px; background:#000;" src="${src}" allow="autoplay; fullscreen; picture-in-picture" allowfullscreen loading="lazy"></iframe>`;
                                    box.style.display='block'; return;
                                }
                                const tk = extractTikTok(val);
                                if(tk){
                                    ensureTikTokScript();
                                    box.innerHTML = `<blockquote class="tiktok-embed" cite="${tk}" style="max-width: 605px;min-width: 325px;"><section>Veja no TikTok: <a href="${tk}" target="_blank" rel="noopener">Abrir</a></section></blockquote>`;
                                    box.style.display='block'; return;
                                }
                                // Se colou um iframe de outra plataforma, tenta exibir direto
                                if(/<iframe[\s\S]*<\/iframe>/.test(val)){
                                    box.innerHTML = val; box.style.display='block'; return;
                                }
                                box.style.display='none'; box.innerHTML='';
                            }
                            input.addEventListener('input', render);
                            input.addEventListener('change', render);
                            input.addEventListener('paste', ()=>setTimeout(render, 0));
                            const tinput = document.getElementById('video-thumb');
                            const tprev = document.getElementById('video-thumb-preview');
                            tinput?.addEventListener('change', ()=>{
                                const f = tinput.files?.[0];
                                if(!f){ tprev.style.display='none'; tprev.innerHTML=''; return; }
                                const reader = new FileReader();
                                reader.onload = ()=>{ tprev.innerHTML = `<img src="${reader.result}" alt="Thumb" style="max-width:100%; border-radius:10px; border:1px solid #e0e6ee;" />`; tprev.style.display='block'; };
                                reader.readAsDataURL(f);
                            });
                        })();

(function(){
                    const btns=[...document.querySelectorAll('.edu-area-btn')];
                    const secs=[...document.querySelectorAll('.edu-area-section')];
                    function show(area){
                        btns.forEach(b=>b.classList.toggle('active', b.dataset.area===area));
                        secs.forEach(s=>s.classList.toggle('active', s.id==='area-'+area));
                        localStorage.setItem('edu-area', area);
                    }
                    btns.forEach(b=>b.addEventListener('click',()=>show(b.dataset.area)));
                    const saved=localStorage.getItem('edu-area')||'artigos';
                    if(saved!=='artigos') show(saved);
                })();

// Fetch rápido para contar tickets (limite 1 requisição simples)
                    fetch('/admin/suporte').then(r=>r.text()).then(html=>{
                        const matches = html.match(/class=\"ticket\"/g) || [];
                        const count = matches.length;
                        if(count>0){
                            const b=document.getElementById('badge-suporte');
                            if(b){ b.textContent=count; b.style.display='inline-block'; }
                        }
                    }).catch(()=>{});

// Tabs
            const links = document.querySelectorAll('.tab-link');
            const panels = document.querySelectorAll('.tab-panel');
            let chartsLoaded = false;
            
            function activate(tab, push=true){
                links.forEach(a=>a.classList.toggle('active', a.dataset.tab===tab));
                panels.forEach(p=>p.classList.toggle('active', p.id==='tab-'+tab));
                if(push) history.replaceState({},'', '#'+tab);
                
                // Load charts when Analytics tab is activated for the first time
                if(tab === 'analytics' && !chartsLoaded){
                    chartsLoaded = true;
                    loadAnalyticsCharts();
                }
            }
            links.forEach(l=>{
                l.addEventListener('click', e=>{ e.preventDefault(); activate(l.dataset.tab); });
            });
            const hash = location.hash.replace('#','');
            if(hash){ activate(hash,false); }
            if(!hash){
                const params = new URLSearchParams(location.search);
                const anchor = params.get('_anchor');
                if(anchor) activate(anchor,false);
            }
            // Suporte a tema removido
            // Gráfico de usuários - now wrapped in function
            function loadAnalyticsCharts() {
                // First, load Chart.js library from local static files
                const script = document.createElement('script');
                script.src = "{{ url_for('static', filename='js/chart.min.js') }}";
                script.onload = () => {
                    // Once Chart.js is loaded, fetch data and create all charts
                    
                    // 1. Crescimento de Usuáries (User Growth)
                    fetch("{{ url_for('admin.stats_users') }}")
                        .then(r => r.json())
                        .then(d => {
                            if(!d || !d.hasOwnProperty('labels') || !d.hasOwnProperty('data')) {
                                console.error('Dados de usuários inválidos:', d);
                                return;
                            }
                            const ctx = document.getElementById('usersChart').getContext('2d');
                            new Chart(ctx, {
                                type: 'line',
                                data: {
                                    labels: d.labels,
                                    datasets: [{
                                        label: 'Total de Usuáries',
                                        data: d.data,
                                        fill: true,
                                        backgroundColor: 'rgba(155,93,229,0.1)',
                                        borderColor: '#9B5DE5',
                                        tension: 0.25,
                                        pointRadius: 3
                                    }]
                                },
                                options: {
                                    plugins: {
                                        legend: {
                                            display: true,
                                            labels: {
                                                color: 'var(--text-soft)',
                                                font: { size: 11 }
                                            }
                                        }
                                    },
                                    scales: {
                                        x: {
                                            ticks: {
                                                color: 'var(--text-soft)',
                                                font: { size: 10 }
                                            }
                                        },
                                        y: {
                                            grid: { color: 'rgba(0,0,0,.06)' },
                                            ticks: {
                                                color: 'var(--text-soft)',
                                                font: { size: 10 },
                                                precision: 0
                                            }
                                        }
                                    }
                                }
                            });
                        })
                        .catch(err => console.error('Erro ao carregar dados de usuários:', err));
                    
                    // 2. Criação de Conteúdo Edu (Edu Content Creation)
                    fetch("{{ url_for('admin.stats_content') }}")
                        .then(r => r.json())
                        .then(d => {
                            const ctx = document.getElementById('contentChart').getContext('2d');
                            new Chart(ctx, {
                                type: 'bar',
                                data: {
                                    labels: d.labels,
                                    datasets: [{
                                        label: 'Conteúdos Criados',
                                        data: d.data,
                                        backgroundColor: 'rgba(72,187,120,0.7)',
                                        borderColor: '#48bb78',
                                        borderWidth: 1
                                    }]
                                },
                                options: {
                                    plugins: {
                                        legend: {
                                            display: true,
                                            labels: {
                                                color: 'var(--text-soft)',
                                                font: { size: 11 }
                                            }
                                        }
                                    },
                                    scales: {
                                        x: {
                                            ticks: {
                                                color: 'var(--text-soft)',
                                                font: { size: 10 }
                                            }
                                        },
                                        y: {
                                            grid: { color: 'rgba(0,0,0,.06)' },
                                            ticks: {
                                                color: 'var(--text-soft)',
                                                font: { size: 10 },
                                                precision: 0
                                            }
                                        }
                                    }
                                }
                            });
                        })
                        .catch(err => console.error('Erro ao carregar dados de conteúdo:', err));
                    
                    // 3. Posts Criados (últimos 7 dias) (Posts Created - Last 7 days)
                    fetch("{{ url_for('admin.stats_posts') }}")
                        .then(r => r.json())
                        .then(d => {
                            const ctx = document.getElementById('postsChart').getContext('2d');
                            new Chart(ctx, {
                                type: 'line',
                                data: {
                                    labels: d.labels,
                                    datasets: [{
                                        label: 'Posts',
                                        data: d.data,
                                        fill: true,
                                        backgroundColor: 'rgba(246,173,85,0.2)',
                                        borderColor: '#f6ad55',
                                        tension: 0.3,
                                        pointRadius: 2
                                    }]
                                },
                                options: {
                                    plugins: {
                                        legend: {
                                            display: true,
                                            labels: {
                                                color: 'var(--text-soft)',
                                                font: { size: 11 }
                                            }
                                        }
                                    },
                                    scales: {
                                        x: {
                                            ticks: {
                                                color: 'var(--text-soft)',
                                                font: { size: 9 }
                                            }
                                        },
                                        y: {
                                            grid: { color: 'rgba(0,0,0,.06)' },
                                            ticks: {
                                                color: 'var(--text-soft)',
                                                font: { size: 9 },
                                                precision: 0
                                            }
                                        }
                                    }
                                }
                            });
                        })
                        .catch(err => console.error('Erro ao carregar dados de posts:', err));
                    
                    // 4. Atividade por Tipo (Activity by Type)
                    fetch("{{ url_for('admin.stats_activity') }}")
                        .then(r => r.json())
                        .then(d => {
                            const ctx = document.getElementById('activityChart').getContext('2d');
                            new Chart(ctx, {
                                type: 'doughnut',
                                data: {
                                    labels: d.labels,
                                    datasets: [{
                                        data: d.data,
                                        backgroundColor: ['#9B5DE5', '#48bb78', '#f6ad55', '#fc8181', '#63b3ed'],
                                        borderWidth: 0
                                    }]
                                },
                                options: {
                                    plugins: {
                                        legend: {
                                            display: true,
                                            position: 'bottom',
                                            labels: {
                                                color: 'var(--text-soft)',
                                                font: { size: 10 },
                                                padding: 8
                                            }
                                        }
                                    }
                                }
                            });
                        })
                        .catch(err => console.error('Erro ao carregar dados de atividade:', err));
                };
                script.onerror = () => {
                    console.error('Falha ao carregar Chart.js');
                };
                document.head.appendChild(script);
            }
            // (Busca removida do painel; agora nas páginas públicas)

// Menu de 3 pontinhos
            const menuTrigger = document.querySelector('.ellipsis-nav .menu-trigger');
            const menuDropdown = document.querySelector('.ellipsis-nav .menu-dropdown');
            if(menuTrigger && menuDropdown){
                menuTrigger.addEventListener('click', e=>{
                    e.stopPropagation();
                    const expanded = menuTrigger.getAttribute('aria-expanded') === 'true';
                    menuTrigger.setAttribute('aria-expanded', String(!expanded));
                    menuDropdown.classList.toggle('show', !expanded);
                    menuDropdown.setAttribute('aria-hidden', String(expanded));
                });
                document.addEventListener('click', ()=>{
                    if(menuDropdown.classList.contains('show')){
                        menuDropdown.classList.remove('show');
                        menuTrigger.setAttribute('aria-expanded','false');
                        menuDropdown.setAttribute('aria-hidden','true');
                    }
                });
                window.addEventListener('keydown', e=>{
                    if(e.key==='Escape' && menuDropdown.classList.contains('show')){
                        menuDropdown.classList.remove('show');
                        menuTrigger.setAttribute('aria-expanded','false');
                        menuDropdown.setAttribute('aria-hidden','true');
                        menuTrigger.focus();
                    }
                });
            }

// Toggle topic edit form
    function toggleTopicEdit(topicId) {
        const editDiv = document.getElementById('topic-edit-' + topicId);
        if (editDiv) {
            editDiv.style.display = editDiv.style.display === 'none' ? 'block' : 'none';
        }
    }
"""

async def _admin_page(self, db, current_user):
    """Admin Dashboard - VERSÃO AUTO-GERADA"""
    
    # Check admin
    if not current_user:
        return redirect('/login')
    
    is_admin = current_user.get('is_admin', False) or current_user.get('is_superadmin', False)
    if not is_admin:
        return html_response("<h1>Acesso Negado</h1>")
    
    # Get data
    stats = await get_admin_stats(db) if db else {}
    all_users = await get_all_usuaries(db) if db else []
    edu_topics = []  # TODO: implementar get_edu_topics
    divulgacoes = []  # TODO: implementar get_divulgacoes
    
    # Build HTML
    return f"""{page_head("Painel de Controle — Gramátike", ADMIN_CSS)}
<header class="site-head">
    <div class="admin-badge">ADMIN</div>
    <h1 class="logo">Gramátike</h1>
    <nav class="tabs">
        <a href="javascript:void(0)" data-tab="geral" class="tab-link active" role="tab">📊 Geral</a>
        <a href="javascript:void(0)" data-tab="analytics" class="tab-link" role="tab">📈 Analytics</a>
        <a href="javascript:void(0)" data-tab="publi" class="tab-link" role="tab">📢 Publi</a>
        <a href="javascript:void(0)" data-tab="edu" class="tab-link" role="tab">📚 Edu</a>
        <a href="javascript:void(0)" data-tab="gramatike" class="tab-link" role="tab">✏️ Gramatike</a>
    </nav>
</header>

<main>
    <section class="tab-panel active" id="tab-geral" role="tabpanel">
        {GERAL_TAB_HTML}
    </section>

    <section class="tab-panel" id="tab-analytics" role="tabpanel">
        {ANALYTICS_TAB_HTML}
    </section>

    <section class="tab-panel" id="tab-publi" role="tabpanel">
        {PUBLI_TAB_HTML}
    </section>

    <section class="tab-panel" id="tab-edu" role="tabpanel">
        {EDU_TAB_HTML}
    </section>

    <section class="tab-panel" id="tab-gramatike" role="tabpanel">
        {GRAMATIKE_TAB_HTML}
    </section>

</main>

<script>
{ADMIN_JAVASCRIPT}
</script>

{page_footer(False)}
"""
