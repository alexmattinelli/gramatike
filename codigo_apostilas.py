# Convertendo: gramatike_app/templates/apostilas.html
# ATENÇÃO: Este código é uma base. REVISE e ajuste:
#    - Busca de dados do banco
#    - Filtros e paginação
#    - Loops Jinja para lógica Python
#    - Condicionais Jinja para lógica Python

async def _apostilas_page(self, db, current_user):
    """Página gerada automaticamente - REVISE antes de usar!"""
    
    # TODO: Buscar dados do banco
    # conteudos = await get_conteudos(db, tipo="...")
    # topics = await get_topics(db)
    
    # TODO: Implementar filtros de busca
    q = ""  # request.args.get('q', '')
    
    return f"""{page_head("Título da Página", """

        :root {{ --primary:#9B5DE5; --primary-dark:#7d3dc9; --bg:#f7f8ff; --card:#ffffff; --border:#e5e7eb; --text:#222; --text-dim:#666; }}
        * {{ box-sizing:border-box; }}
        html, body {{ margin:0; padding:0; overflow-x:hidden; width:100%; max-width:100vw; }}
        body {{ font-family:'Nunito',system-ui,-apple-system,'Segoe UI',Roboto,Arial,sans-serif; background:var(--bg); color:var(--text); line-height:1.55; display:flex; flex-direction:column; min-height:100vh; }}
        h1,h2,h3 {{ font-weight:800; margin:0 0 .9rem; line-height:1.12; }}
        header.site-head {{ background:#9B5DE5; padding:28px clamp(16px,4vw,40px) 46px; border-bottom-left-radius:40px; border-bottom-right-radius:40px; position:relative; display:flex; flex-direction:column; align-items:center; }}
        .logo {{ font-family:'Mansalva', cursive; font-size:2.6rem; color:#fff; letter-spacing:1px; font-weight:400; margin:0; }}
        .edu-nav {{ margin-top:1.1rem; display:flex; flex-wrap:wrap; gap:.65rem; justify-content:center; }}
    .edu-nav a {{ text-decoration:none; font-weight:700; font-size:.7rem; letter-spacing:.55px; padding:.65rem 1.05rem .62rem; background:#ffffff18; color:#fff; border:1px solid #ffffff30; backdrop-filter:blur(4px); -webkit-backdrop-filter:blur(4px); border-radius:22px; display:inline-flex; align-items:center; gap:.35rem; box-shadow:0 4px 12px rgba(0,0,0,.18); transition:.25s; font-family:'Nunito',system-ui,-apple-system,'Segoe UI',Roboto,Arial,sans-serif; }}
        .edu-nav a:hover, .edu-nav a.active {{ background:#fff; color:#7d3dc9; }}
    main {{ width:100%; max-width:1400px; margin:2rem auto 4rem; padding:0 clamp(28px,5vw,90px); flex:1; }}
        .page-title {{ text-align:center; font-size:2.1rem; color:#9B5DE5; margin:0 0 1.8rem; }}
        /* Barra de tópicos unificada */
        .topics-bar {{ display:flex; flex-wrap:wrap; gap:.55rem; justify-content:center; margin:0 0 2rem; }}
        .topics-bar a {{ text-decoration:none; font-size:.6rem; font-weight:800; letter-spacing:.6px; padding:.55rem .85rem .5rem; background:#f1edff; color:#9B5DE5; border:1px solid #e3daf9; border-radius:18px; box-shadow:0 2px 6px rgba(155,93,229,.18); transition:.25s; }}
        .topics-bar a:hover {{ background:#9B5DE5; color:#fff; border-color:#9B5DE5; }}
        .topics-bar a.active {{ background:#9B5DE5; color:#fff; border-color:#9B5DE5; }}
        .search-box form {{ display:flex; gap:.55rem; flex-wrap:nowrap; align-items:stretch; width:100%; max-width:860px; margin:0 auto 2rem; }}
        .search-box input {{ flex:1; height:50px; border:1px solid var(--border); border-radius:20px; padding:0 1.15rem; font-size:.85rem; background:var(--card); font-weight:600; }}
    .search-box button {{ height:50px; border:none; background:#9B5DE5; color:#fff; font-weight:700; font-size:.78rem; padding:0 1.4rem; border-radius:20px; cursor:pointer; letter-spacing:.4px; box-shadow:0 6px 20px rgba(155,93,229,.4); display:inline-flex; align-items:center; gap:.45rem; }}
    .search-box button.icon-btn {{ width:50px; padding:0; justify-content:center; }}
        .search-box button:hover {{ filter:brightness(1.07); }}
        .pdf-list {{ list-style:none; margin:0 auto; padding:0; max-width:1400px; }}
    .pdf-list li {{ position:relative; padding:1rem .9rem; margin:0; }}
        .pdf-item {{ display:flex; gap:14px; align-items:flex-start; background:var(--card); border:1px solid var(--border); border-radius:26px; padding:1rem 1.15rem; box-shadow:0 10px 24px -6px rgba(0,0,0,.10); transition:.3s; }}
        .pdf-item:hover {{ box-shadow:0 18px 46px -10px rgba(0,0,0,.28); transform:translateY(-3px); }}
        .pdf-thumb {{ width:auto; height:150px; border:1px solid #d6dee8; border-radius:10px; background:#fff; box-shadow:0 4px 10px rgba(0,0,0,.08); }}
        .pdf-thumb-wrap {{ position:relative; }}
        .thumb-view-btn {{ position:absolute; right:8px; bottom:8px; width:38px; height:38px; display:flex; align-items:center; justify-content:center; border-radius:50%; border:1px solid #cfd7e2; background:#ffffffdd; color:#334155; font-size:18px; cursor:pointer; box-shadow:0 4px 14px rgba(0,0,0,.18); opacity:0; transition:.2s; }}
        .pdf-thumb-wrap:hover .thumb-view-btn {{ opacity:1; }}
        @media (hover:none){{ .thumb-view-btn{{ opacity:1; }} }}
        .pdf-list a {{ color:#9B5DE5; font-weight:700; text-decoration:none; }}
        .pdf-list a:hover {{ text-decoration:underline; }}
    .item-menu-trigger {{ position:absolute; top:12px; right:18px; background:#f1edff; border:1px solid #d6c9f2; border-radius:18px; width:34px; height:34px; display:flex; align-items:center; justify-content:center; cursor:pointer; box-shadow:0 4px 10px rgba(155,93,229,.25); transition:.25s; z-index:40; }}
    .item-menu-trigger:hover {{ background:#e3daf9; box-shadow:0 6px 16px -3px rgba(155,93,229,.35); }}
    .item-menu-trigger:focus-visible {{ outline:2px solid #caa9f6; outline-offset:2px; }}
    .item-menu {{ position:absolute; top:50px; right:18px; background:#fff; border:1px solid var(--border); border-radius:14px; box-shadow:0 14px 40px -8px rgba(0,0,0,.25); padding:.35rem 0; min-width:170px; display:none; z-index:9999; }}
        .item-menu.show {{ display:block; }}
        .item-menu button {{ all:unset; display:block; width:100%; font-size:.7rem; font-weight:700; letter-spacing:.4px; padding:.55rem .85rem .5rem; cursor:pointer; color:#444; }}
        .item-menu button:hover {{ background:#f1edff; color:#9B5DE5; }}
        .item-menu form button.danger {{ color:#b42318; }}
        .item-menu form button.danger:hover {{ background:#ffe4e1; }}
    footer {{ margin-top:4rem; background:#9B5DE5; color:#fff; text-align:center; padding:1.4rem 1rem 1.6rem; font-size:.75rem; letter-spacing:.5px; font-weight:700; border-top-left-radius:38px; border-top-right-radius:38px; }}
    @media (max-width: 980px){{ 
      footer {{ display:none !important; }}
      /* Esconder navegação de educação no mobile */
      .edu-nav {{ display:none !important; }}
    }}
    .pag-btn {{ padding:.55rem .9rem; border-radius:18px; background:#9B5DE5; color:#fff; text-decoration:none; display:inline-block; }}
    .pag-btn.disabled {{ pointer-events:none; opacity:.45; }}
        /* Modal */
        #pdfPreviewDialog{{ width:min(98vw,1400px); border:0; border-radius:26px; padding:0; box-shadow:0 30px 70px -10px rgba(0,0,0,.45); background:linear-gradient(140deg,#fff,#f5efff); }}
        #pdfPreviewDialog::backdrop{{ background:rgba(13,20,33,.55); backdrop-filter: blur(4px); }}
        .pdf-modal-head{{ background:#faf7ff; }}
        .pdf-modal-head h3{{ font-weight:800; letter-spacing:.4px; color:#9B5DE5; }}
        #pdf_iframe{{ background:#fff; }}
        @media (max-width:720px){{ header.site-head {{ padding:12px 18px 18px; }} .logo {{ font-size:1.5rem; }} .pdf-item {{ flex-direction:column; align-items:flex-start; }} .pdf-thumb{{ height:120px; }} }}
    /* Evitar que o card "suba" quando o menu está aberto */
    li.menu-open .pdf-item:hover {{ transform:none; box-shadow:0 10px 24px -6px rgba(0,0,0,.10); }}
    /* Chamada para usuáries */
    .callout-usuaries {{ background:linear-gradient(135deg,#9B5DE5,#7d3dc9 55%, #b88bf2); color:#fff; padding:1.15rem 1.4rem 1.2rem; border-radius:30px; box-shadow:0 14px 34px -10px rgba(123,60,200,.45); position:relative; overflow:hidden; margin:0 auto 2.2rem; max-width:1180px; }}
    .callout-usuaries:before {{ content:""; position:absolute; inset:0; background:radial-gradient(circle at 78% 24%,rgba(255,255,255,.22),transparent 60%); pointer-events:none; }}
    .callout-usuaries h2 {{ margin:0 0 .55rem; font-size:1.55rem; letter-spacing:.5px; line-height:1.05; }}
    .callout-usuaries p {{ margin:.2rem 0 0; font-size:.9rem; font-weight:600; letter-spacing:.35px; max-width:900px; }}
    .callout-tags {{ margin-top:.85rem; display:flex; flex-wrap:wrap; gap:.45rem; }}
    .callout-tags span {{ background:#ffffff18; border:1px solid #ffffff30; padding:.35rem .7rem .33rem; font-size:.6rem; font-weight:800; letter-spacing:.6px; border-radius:18px; text-transform:uppercase; }}
    @media (max-width:780px){{ .callout-usuaries {{ padding:1.05rem 1.1rem 1.15rem; border-radius:26px; }} .callout-usuaries h2 {{ font-size:1.32rem; }} .callout-usuaries p {{ font-size:.82rem; }} }}
    
    """)}

    <header class="site-head">
        <h1 class="logo">Gramátike Edu</h1>
        {{% if current_user.is_authenticated and (current_user.is_admin or current_user.is_superadmin) %}}
        <!-- Menu Dropdown (mobile) / Painel button (desktop) -->
        <div style="position:absolute; top:14px; right:16px;">
          <button id="menu-toggle" onclick="toggleMenu()" style="background:#ffffff22; border:1px solid #ffffff42; color:#fff; padding:6px 10px; font-size:11px; font-weight:700; border-radius:8px; cursor:pointer; letter-spacing:.5px; display:flex; align-items:center; gap:6px;">
            <svg id="menu-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <line x1="3" y1="12" x2="21" y2="12"></line>
              <line x1="3" y1="6" x2="21" y2="6"></line>
              <line x1="3" y1="18" x2="21" y2="18"></line>
            </svg>
            <svg id="painel-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="display:none;">
              <rect x="3" y="3" width="7" height="7"></rect>
              <rect x="14" y="3" width="7" height="7"></rect>
              <rect x="14" y="14" width="7" height="7"></rect>
              <rect x="3" y="14" width="7" height="7"></rect>
            </svg>
            <span id="menu-text">Menu</span>
          </button>
          <div id="menu-dropdown" style="display:none; position:absolute; right:0; top:calc(100% + 8px); background:#fff; border:1px solid #e5e7eb; border-radius:12px; box-shadow:0 8px 24px rgba(0,0,0,.18); min-width:200px; z-index:100;">
            <a href="{{{{ url_for('main.educacao') }}}}" style="display:flex; align-items:center; gap:10px; padding:10px 14px; text-decoration:none; color:#333; font-size:.75rem; font-weight:600; border-bottom:1px solid #f0f0f0; transition:background .2s;" onmouseover="this.style.background='#f7f2ff'" onmouseout="this.style.background='transparent'">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#9B5DE5" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
                <polyline points="9 22 9 12 15 12 15 22"></polyline>
              </svg>
              Início
            </a>
            <a href="{{{{ url_for('main.artigos') }}}}" style="display:flex; align-items:center; gap:10px; padding:10px 14px; text-decoration:none; color:#333; font-size:.75rem; font-weight:600; border-bottom:1px solid #f0f0f0; transition:background .2s;" onmouseover="this.style.background='#f7f2ff'" onmouseout="this.style.background='transparent'">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#9B5DE5" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                <polyline points="14 2 14 8 20 8"></polyline>
                <line x1="16" y1="13" x2="8" y2="13"></line>
                <line x1="16" y1="17" x2="8" y2="17"></line>
                <polyline points="10 9 9 9 8 9"></polyline>
              </svg>
              Artigos
            </a>
            <a href="{{{{ url_for('main.exercicios') }}}}" style="display:flex; align-items:center; gap:10px; padding:10px 14px; text-decoration:none; color:#333; font-size:.75rem; font-weight:600; border-bottom:1px solid #f0f0f0; transition:background .2s;" onmouseover="this.style.background='#f7f2ff'" onmouseout="this.style.background='transparent'">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#9B5DE5" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10"></circle>
                <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"></path>
                <line x1="12" y1="17" x2="12.01" y2="17"></line>
              </svg>
              Exercícios
            </a>
            <a href="{{{{ url_for('main.apostilas') }}}}" style="display:flex; align-items:center; gap:10px; padding:10px 14px; text-decoration:none; color:#333; font-size:.75rem; font-weight:600; border-bottom:1px solid #f0f0f0; transition:background .2s;" onmouseover="this.style.background='#f7f2ff'" onmouseout="this.style.background='transparent'">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#9B5DE5" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path>
                <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path>
              </svg>
              Apostilas
            </a>
            <a href="{{{{ url_for('main.dinamicas_home') }}}}" style="display:flex; align-items:center; gap:10px; padding:10px 14px; text-decoration:none; color:#333; font-size:.75rem; font-weight:600; border-bottom:1px solid #f0f0f0; transition:background .2s;" onmouseover="this.style.background='#f7f2ff'" onmouseout="this.style.background='transparent'">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#9B5DE5" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M19.439 15.439c.389-.389.586-.585.638-.866a1 1 0 0 0 0-.414c-.052-.281-.249-.477-.638-.866l-1.88-1.88c-.389-.389-.585-.586-.866-.638a1 1 0 0 0-.414 0c-.281.052-.477.249-.866.638l-1.88 1.88c-.389.389-.586.585-.638.866a1 1 0 0 0 0 .414c.052.281.249.477.638.866l1.88 1.88c.389.389.585.586.866.638a1 1 0 0 0 .414 0c.281-.052.477-.249.866-.638l1.88-1.88z"></path>
                <path d="M11.5 8.5c.833-.833 1.25-1.25 1.5-1.768a3 3 0 0 0 0-2.464C12.75 3.75 12.333 3.333 11.5 2.5 10.667 1.667 10.25 1.25 9.732 1c-.784-.378-1.68-.378-2.464 0C6.75 1.25 6.333 1.667 5.5 2.5s-1.25 1.167-1.5 1.768a3 3 0 0 0 0 2.464c.25.601.667 1.018 1.5 1.768.833.75 1.25 1.167 1.768 1.5a3 3 0 0 0 2.464 0c.601-.333 1.018-.75 1.768-1.5z"></path>
                <path d="M5.5 21.5c.833.833 1.25 1.25 1.768 1.5a3 3 0 0 0 2.464 0c.601-.25 1.018-.667 1.768-1.5.75-.833 1.167-1.25 1.5-1.768a3 3 0 0 0 0-2.464c-.333-.601-.75-1.018-1.5-1.768-.75-.75-1.167-1.167-1.768-1.5a3 3 0 0 0-2.464 0C6.75 13.25 6.333 13.667 5.5 14.5c-.833.833-1.25 1.25-1.5 1.768a3 3 0 0 0 0 2.464c.25.601.667 1.018 1.5 1.768z"></path>
              </svg>
              Dinâmicas
            </a>
            <a href="{{{{ url_for('admin.dashboard') }}}}" style="display:flex; align-items:center; gap:10px; padding:10px 14px; text-decoration:none; color:#333; font-size:.75rem; font-weight:600; transition:background .2s;" onmouseover="this.style.background='#f7f2ff'" onmouseout="this.style.background='transparent'">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#9B5DE5" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"></path>
              </svg>
              Painel
            </a>
          </div>
        </div>
        {{% endif %}}
        <nav class="edu-nav" aria-label="Seções educacionais">
            <a href="{{{{ url_for('main.educacao') }}}}">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
                    <polyline points="9 22 9 12 15 12 15 22"></polyline>
                </svg>
                Início
            </a>
            <a href="{{{{ url_for('main.apostilas') }}}}" class="active">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path>
                    <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path>
                </svg>
                Apostilas
            </a>
            <a href="{{{{ url_for('main.exercicios') }}}}">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="12" cy="12" r="10"></circle>
                    <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"></path>
                    <line x1="12" y1="17" x2="12.01" y2="17"></line>
                </svg>
                Exercícios
            </a>
            {{# Temporariamente desabilitados: Podcasts, Redação e Vídeos
            <a href="{{{{ url_for('main.podcasts') }}}}"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="display:inline-block;vertical-align:middle;margin-right:4px;"><path d="M3 18v-6a9 9 0 0 1 18 0v6"/><path d="M21 19a2 2 0 0 1-2 2h-1a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2h3zM3 19a2 2 0 0 0 2 2h1a2 2 0 0 0 2-2v-3a2 2 0 0 0-2-2H3z"/></svg>Podcasts</a>
            <a href="{{{{ url_for('main.redacao') }}}}"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="display:inline-block;vertical-align:middle;margin-right:4px;"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>Redação</a>
            <a href="{{{{ url_for('main.videos') }}}}"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="display:inline-block;vertical-align:middle;margin-right:4px;"><polygon points="23 7 16 12 23 17 23 7"/><rect x="1" y="5" width="15" height="14" rx="2" ry="2"/></svg>Vídeos</a>
            #}}
            <a href="{{{{ url_for('main.artigos') }}}}">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                    <polyline points="14 2 14 8 20 8"></polyline>
                    <line x1="16" y1="13" x2="8" y2="13"></line>
                    <line x1="16" y1="17" x2="8" y2="17"></line>
                    <polyline points="10 9 9 9 8 9"></polyline>
                </svg>
                Artigos
            </a>
        </nav>
    </header>
    <main>
    <!-- Seção de chamada removida a pedido -->
    <!-- Título removido a pedido -->
        <div class="search-box">
            <form method="get" action="">
                <input type="text" name="q" placeholder="Pesquisar título ou descrição..." value="{{{{ q }}}}" />
                <button type="submit" class="icon-btn" aria-label="Buscar" title="Buscar">
                    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                        <circle cx="11" cy="11" r="7"></circle>
                        <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                    </svg>
                </button>
            </form>
        </div>
        {{% if topics %}}
        <div class="topics-bar">
                {{% for topico in topics %}}
                    <a href="?topic_id={{{{ topico.id }}}}{{% if q %}}&q={{{{ q }}}}{{% endif %}}" class="{{% if topic_id and topic_id|string == topico.id|string %}}active{{% endif %}}">{{{{ topico.nome }}}}</a>
                {{% endfor %}}
                {{% if topic_id or q %}}
                <a href="?" class="clear-filters" style="background:#ffe4e1; color:#b42318; border-color:#ffb8b1; display:inline-flex; align-items:center; gap:.35rem;">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                        <line x1="18" y1="6" x2="6" y2="18"></line>
                        <line x1="6" y1="6" x2="18" y2="18"></line>
                    </svg>
                    Limpar Filtros
                </a>
                {{% endif %}}
        </div>
        {{% endif %}}

    {{# Removido agrupamento por tópicos para visualizar por mais recentes #}}

    <!-- Barra de pesquisa duplicada removida -->

        <!-- Lista plana por mais recentes -->
                        {{% if conteudos %}}
            <ul class="pdf-list" style="max-width:1400px; margin:0 auto;">
                {{% for c in conteudos %}}
                    {{% set extra = (c.extra | fromjson) if c.extra else None %}}
                    <li style="position:relative; padding:.65rem .25rem;">
                        {{% set _pdf_src = None %}}
                        {{% if c.file_path %}}
                            {{% if c.file_path.startswith('http://') or c.file_path.startswith('https://') %}}
                                {{% set _pdf_src = c.file_path %}}
                            {{% else %}}
                                {{% set _pdf_src = url_for('static', filename=c.file_path) %}}
                            {{% endif %}}
                        {{% elif c.url and c.url.lower().endswith('.pdf') %}}
                            {{% set _pdf_src = c.url %}}
                        {{% endif %}}
                        {{% if current_user.is_authenticated and (current_user.is_admin or current_user.is_superadmin) %}}
                        <button class="item-menu-trigger" aria-label="Menu">
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                                <circle cx="12" cy="12" r="1"></circle>
                                <circle cx="12" cy="5" r="1"></circle>
                                <circle cx="12" cy="19" r="1"></circle>
                            </svg>
                        </button>
                        <div class="item-menu" role="menu">
                            <button type="button" data-edit="{{{{ c.id }}}}">Editar</button>
                            <button type="button" data-share="{{{{ c.id }}}}" data-title="{{{{ c.titulo }}}}">Compartilhar</button>
                            <form method="POST" action="/admin/edu/content/{{{{ c.id }}}}/delete" onsubmit="return confirm('Excluir esta apostila?');">
                                
                                <input type="hidden" name="next" value="{{{{ request.url }}}}" />
                                <button type="submit" class="danger">Excluir</button>
                            </form>
                        </div>
                        {{% endif %}}
                        <div class="pdf-item">
                            {{% if extra and extra.thumb %}}
                                <div class="pdf-thumb-wrap">
                                    {{% if extra.thumb.startswith('http://') or extra.thumb.startswith('https://') %}}
                                        <img class="pdf-thumb" src="{{{{ extra.thumb }}}}" alt="Miniatura da apostila {{{{ c.titulo }}}}" loading="lazy" />
                                    {{% else %}}
                                        <img class="pdf-thumb" src="{{{{ url_for('static', filename=extra.thumb) }}}}" alt="Miniatura da apostila {{{{ c.titulo }}}}" loading="lazy" />
                                    {{% endif %}}
                                    {{% if _pdf_src %}}<button type="button" class="thumb-view-btn thumb-visualizar" data-src="{{{{ _pdf_src }}}}" title="Visualizar PDF">
                                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                            <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                                            <circle cx="12" cy="12" r="3"></circle>
                                        </svg>
                                    </button>{{% endif %}}
                                </div>
                            {{% endif %}}
                            <div class="pdf-meta">
                                {{% if c.file_path %}}
                                    {{% if c.file_path.startswith('http://') or c.file_path.startswith('https://') %}}
                                        <a href="{{{{ c.file_path }}}}" target="_blank" rel="noopener">{{{{ c.titulo }}}}</a>
                                    {{% else %}}
                                        {{% set pdf_src = url_for('static', filename=c.file_path) %}}
                                        <a href="{{{{ pdf_src }}}}" target="_blank" rel="noopener">{{{{ c.titulo }}}}</a>
                                    {{% endif %}}
                                {{% elif c.url %}}
                                    <a href="{{{{ c.url }}}}" target="_blank" rel="noopener">{{{{ c.titulo }}}}</a>
                                {{% else %}}
                                    {{{{ c.titulo }}}}
                                {{% endif %}}
                                {{% if extra and extra.author %}}
                                    <div style="font-size:.7rem; color:#5b6a7c;">Autore: {{{{ extra.author }}}}</div>
                                {{% endif %}}
                                {{% if c.resumo %}}<div style="font-size:.65rem; color:#555; margin-top:2px;">{{{{ c.resumo }}}}</div>{{% endif %}}
                            </div>
                        </div>
                    </li>
                {{% endfor %}}
            </ul>
        {{% else %}}
            <p style="text-align:center; color:#888;">Nenhuma apostila encontrada{{% if q %}} para a busca '{{{{ q }}}}'{{% endif %}}.</p>
        {{% endif %}}
        {{% if last_page and last_page > 1 %}}
        <div class="pagination" style="margin:2rem 0 0; display:flex; gap:.6rem; justify-content:center; align-items:center; flex-wrap:wrap; font-size:.7rem; font-weight:700; letter-spacing:.4px;">
            {{% set base_params = '' %}}
            {{% if q %}}{{% set base_params = base_params + '&q=' + q %}}{{% endif %}}
            {{% if topic_id %}}{{% set base_params = base_params + '&topic_id=' + topic_id %}}{{% endif %}}
            <a href="?page=1{{{{ base_params }}}}" class="pag-btn {{% if page == 1 %}}disabled{{% endif %}}">« Primeiro</a>
            <a href="?page={{{{ page-1 }}}}{{{{ base_params }}}}" class="pag-btn {{% if page == 1 %}}disabled{{% endif %}}">‹ Anterior</a>
            <span style="color:#9B5DE5;">Página {{{{ page }}}} de {{{{ last_page }}}}</span>
            <a href="?page={{{{ page+1 }}}}{{{{ base_params }}}}" class="pag-btn {{% if page == last_page %}}disabled{{% endif %}}">Próxima ›</a>
            <a href="?page={{{{ last_page }}}}{{{{ base_params }}}}" class="pag-btn {{% if page == last_page %}}disabled{{% endif %}}">Última »</a>
        </div>
        {{% endif %}}
  </main>
  
  <!-- Barra de navegação inferior mobile (tipo app/rede social) -->
  
  
  <nav class="mobile-bottom-nav" aria-label="Navegação principal mobile">
    <a href="{{{{ url_for('main.index') }}}}" aria-label="Feed" title="Feed">
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
        <polyline points="9 22 9 12 15 12 15 22"></polyline>
      </svg>
      <span>Início</span>
    </a>
    
    <a href="{{{{ url_for('main.educacao') }}}}" aria-label="Educação" title="Educação" style="opacity: 1;">
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"></path>
        <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"></path>
      </svg>
      <span>Educação</span>
    </a>
    
    <a href="{{{{ url_for('main.novo_post') }}}}" aria-label="Criar post" title="Criar post" style="background: #ffffff; color: #9B5DE5; border-radius: 50%; width: 48px; height: 48px; margin: -10px 0; padding: 0; display: flex; align-items: center; justify-content: center; flex-direction: row; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
      <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="#9B5DE5" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
        <line x1="12" y1="5" x2="12" y2="19"></line>
        <line x1="5" y1="12" x2="19" y2="12"></line>
      </svg>
    </a>
    
    <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 4px; padding: 6px 12px; color: #ffffff; opacity: 0.7; font-size: 0.65rem; font-weight: 600; letter-spacing: 0.3px; text-decoration: none;">
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="12" cy="12" r="10"></circle>
        <polyline points="12 6 12 12 16 14"></polyline>
      </svg>
      <span>Em breve</span>
    </div>
    
    {{% if current_user.is_authenticated %}}
    <a href="{{{{ url_for('main.meu_perfil') }}}}" aria-label="Perfil" title="Perfil">
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
        <circle cx="12" cy="7" r="4"></circle>
      </svg>
      <span>Perfil</span>
    </a>
    {{% else %}}
    <a href="{{{{ url_for('main.login') }}}}" aria-label="Entrar" title="Entrar">
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"></path>
        <polyline points="10 17 15 12 10 7"></polyline>
        <line x1="15" y1="12" x2="3" y2="12"></line>
      </svg>
      <span>Entrar</span>
    </a>
    {{% endif %}}
  </nav>

    <footer>© 2025 Gramátike • Linguagem Viva e de Todes</footer>
    <!-- Modal de Visualização de PDF -->
    <dialog id="pdfPreviewDialog">
        <div class="pdf-modal-wrap">
            <div class="pdf-modal-head">
                <h3>Visualização da Apostila</h3>
                <div class="actions">
                    <a id="pdf_open_new" href="#" target="_blank" rel="noopener" class="nav-button" style="padding:.35rem .7rem; border-radius:10px; text-decoration:none;">Abrir em nova aba</a>
                    <button type="button" id="pdf_close" class="nav-button" style="padding:.35rem .7rem; border-radius:10px; background:#6b7aa8; border:1px solid #4b5a88;">Fechar</button>
                </div>
            </div>
            <div class="pdf-modal-body">
                <iframe id="pdf_iframe" src="about:blank" title="Visualização do PDF"></iframe>
            </div>
        </div>
    </dialog>
    {{% if current_user.is_authenticated and (current_user.is_admin or current_user.is_superadmin) %}}
    <dialog id="editApostilaDialog" style="border:none; border-radius:20px; padding:0; max-width:600px; width:90%;">
        <form id="editApostilaForm" method="post" style="display:grid; gap:.9rem; padding:1.5rem;">
            <h3 style="margin:0; font-size:1.3rem; color:#9B5DE5;">Editar Apostila</h3>
            
            <input type="hidden" name="content_id" id="ap_id" />
            
            <label style="display:grid; gap:.3rem;">
                <span style="font-size:.75rem; font-weight:700; color:#666;">Título</span>
                <input name="titulo" id="ap_titulo" required style="border:1px solid #cfd7e2; border-radius:10px; padding:.65rem .75rem; font-size:.85rem;" />
            </label>
            
            <label style="display:grid; gap:.3rem;">
                <span style="font-size:.75rem; font-weight:700; color:#666;">Autore</span>
                <input name="autor" id="ap_autor" style="border:1px solid #cfd7e2; border-radius:10px; padding:.65rem .75rem; font-size:.85rem;" />
            </label>
            
            <label style="display:grid; gap:.3rem;">
                <span style="font-size:.75rem; font-weight:700; color:#666;">Resumo</span>
                <textarea name="resumo" id="ap_resumo" rows="8" style="min-height:200px; resize:vertical; border:1px solid #cfd7e2; border-radius:10px; padding:.65rem .75rem; font-size:.85rem;"></textarea>
            </label>
            
            <label style="display:grid; gap:.3rem;">
                <span style="font-size:.75rem; font-weight:700; color:#666;">URL (opcional)</span>
                <input name="url" id="ap_url" style="border:1px solid #cfd7e2; border-radius:10px; padding:.65rem .75rem; font-size:.85rem;" />
            </label>
            
            <label style="display:grid; gap:.3rem;">
                <span style="font-size:.75rem; font-weight:700; color:#666;">Tópico</span>
                <select name="topic_id" id="ap_topic" style="border:1px solid #cfd7e2; border-radius:10px; padding:.65rem .75rem; font-size:.85rem;">
                    <option value="">(Tópico)</option>
                    {{% for t in topics %}}<option value="{{{{ t.id }}}}">{{{{ t.nome }}}}</option>{{% endfor %}}
                </select>
            </label>
            
            <p style="font-size:.7rem; color:#999; margin:.2rem 0 0;">Obs.: Troca de arquivo PDF não é suportada aqui; use o painel admin para reenviar se necessário.</p>
            
            <menu style="display:flex; gap:.6rem; justify-content:flex-end; margin:0; padding-top:.6rem;">
                <button type="button" id="ap_cancel" style="padding:.65rem 1.2rem; border:1px solid #cfd7e2; background:#f9f9f9; border-radius:12px; font-weight:700; cursor:pointer;">Cancelar</button>
                <button type="submit" style="padding:.65rem 1.2rem; border:none; background:#9B5DE5; color:#fff; border-radius:12px; font-weight:700; cursor:pointer;">Salvar</button>
            </menu>
        </form>
    </dialog>
    
    <script>
    (function(){{
            // Preview de PDF
            const pdfDlg = document.getElementById('pdfPreviewDialog');
            const pdfFrame = document.getElementById('pdf_iframe');
            const pdfClose = document.getElementById('pdf_close');
            const pdfOpenNew = document.getElementById('pdf_open_new');
            document.addEventListener('click', (e)=>{{
                const btn = e.target.closest('.btn-visualizar, .thumb-visualizar');
                if(!btn) return;
                e.preventDefault();
                const src = btn.getAttribute('data-src');
                if(src){{
                    pdfFrame.src = src;
                    pdfOpenNew.href = src;
                    try{{ pdfDlg.showModal(); }}catch(err){{ window.open(src,'_blank'); }}
                }}
            }});
            function closePdf(){{ pdfFrame.src='about:blank'; pdfDlg.close(); }}
            if(pdfClose){{ pdfClose.addEventListener('click', closePdf); }}
            if(pdfDlg){{ pdfDlg.addEventListener('close', ()=>{{ pdfFrame.src='about:blank'; }}); }}

        // Edit modal
        const dlg = document.getElementById('editApostilaDialog');
        const form = document.getElementById('editApostilaForm');
        const ap_id = document.getElementById('ap_id');
        const ap_titulo = document.getElementById('ap_titulo');
        const ap_resumo = document.getElementById('ap_resumo');
        const ap_url = document.getElementById('ap_url');
        const ap_topic = document.getElementById('ap_topic');
        const ap_cancel = document.getElementById('ap_cancel');
        const ap_autor = document.getElementById('ap_autor');
        
        // Unified click handler
        document.addEventListener('click', async (e)=>{{
            // Check for edit button first
            const editBtn = e.target.closest('[data-edit]');
            if(editBtn){{
                e.preventDefault();
                const id = editBtn.getAttribute('data-edit');
                try{{
                    const data = await fetch(`/admin/edu/content/${id}.json`, {{ credentials: 'same-origin' }}).then(r=>r.json());
                    ap_id.value = data.id;
                    ap_titulo.value = data.titulo||'';
                    ap_resumo.value = data.resumo||'';
                    ap_url.value = data.url||'';
                    ap_autor.value = (data.extra && data.extra.author) ? data.extra.author : '';
                    [...ap_topic.options].forEach(o=>{{ o.selected = String(o.value)===String(data.topic_id||''); }});
                    dlg.showModal();
                }}catch(err){{ alert('Falha ao carregar'); }}
                return;
            }}
            
            // Check for share button
            const shareBtn = e.target.closest('[data-share]');
            if(shareBtn){{
                e.preventDefault();
                const title = shareBtn.getAttribute('data-title') || 'Apostila';
                const url = window.location.href;
                navigator.clipboard.writeText(url).then(() => {{
                    alert('Link copiado!');
                }}).catch(() => {{
                    alert('Erro ao copiar link. URL: ' + url);
                }});
                return;
            }}
            
            // Toggle menu
            const trigger = e.target.closest('.item-menu-trigger');
            if(trigger){{
                e.preventDefault();
                const item = trigger.closest('li');
                const menu = item.querySelector('.item-menu');
                const open = menu.classList.contains('show');
                // fechar todos
                document.querySelectorAll('.item-menu.show').forEach(m=>{{
                    m.classList.remove('show');
                    const li = m.closest('li');
                    if(li) li.classList.remove('menu-open');
                }});
                if(!open){{
                    menu.classList.add('show');
                    item.classList.add('menu-open');
                }}
                return;
            }}
            
            if(!e.target.closest('.item-menu')){{
                document.querySelectorAll('.item-menu.show').forEach(m=>{{
                    m.classList.remove('show');
                    const li = m.closest('li');
                    if(li) li.classList.remove('menu-open');
                }});
            }}
        }});
        
        ap_cancel.addEventListener('click', ()=> dlg.close());
        form.addEventListener('submit', async (e)=>{{
            e.preventDefault();
            const id = ap_id.value;
            const fd = new FormData(form);
            try{{
                const res = await fetch(`/admin/edu/content/${id}/update`, {{ method:'POST', body: fd, credentials: 'same-origin' }});
                if(res.ok){{ dlg.close(); location.reload(); }} else {{ alert('Falha ao salvar'); }}
            }}catch(err){{ alert('Erro de rede'); }}
        }});
    }})();
    </script>
    {{% endif %}}
    
    <!-- Menu dropdown toggle script -->
    <script>
    function toggleMenu() {{
      const isMobile = window.innerWidth <= 980;
      
      if (isMobile) {{
        // Mobile: Toggle dropdown
        const dropdown = document.getElementById('menu-dropdown');
        if (dropdown) {{
          dropdown.style.display = dropdown.style.display === 'none' ? 'block' : 'none';
        }}
      }} else {{
        // Desktop: Go directly to Painel
        {{% if current_user.is_authenticated and (current_user.is_admin or current_user.is_superadmin) %}}
        window.location.href = "{{{{ url_for('admin.dashboard') }}}}";
        {{% endif %}}
      }}
    }}
    
    function updateMenuButton() {{
      const isMobile = window.innerWidth <= 980;
      const menuText = document.getElementById('menu-text');
      const menuIcon = document.getElementById('menu-icon');
      const painelIcon = document.getElementById('painel-icon');
      const dropdown = document.getElementById('menu-dropdown');
      
      if (isMobile) {{
        // Mobile: Show "Menu" with hamburger icon and enable dropdown
        if (menuText) menuText.textContent = 'Menu';
        if (menuIcon) menuIcon.style.display = 'block';
        if (painelIcon) painelIcon.style.display = 'none';
      }} else {{
        // Desktop: Show "Painel" with dashboard icon, no dropdown
        if (menuText) menuText.textContent = 'Painel';
        if (menuIcon) menuIcon.style.display = 'none';
        if (painelIcon) painelIcon.style.display = 'block';
        if (dropdown) dropdown.style.display = 'none';
      }}
    }}
    
    // Initialize on load
    if (window.innerWidth <= 980) {{
      updateMenuButton();
    }} else {{
      updateMenuButton();
    }}
    
    window.addEventListener('resize', updateMenuButton);
    
    // Close menu when clicking outside
    document.addEventListener('click', function(e) {{
      const menuToggle = document.getElementById('menu-toggle');
      const dropdown = document.getElementById('menu-dropdown');
      if (dropdown && menuToggle && !menuToggle.contains(e.target) && !dropdown.contains(e.target)) {{
        dropdown.style.display = 'none';
      }}
    }});
    </script>

{page_footer(True)}"""
