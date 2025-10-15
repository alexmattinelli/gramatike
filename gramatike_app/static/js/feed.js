// Feed principal (renomeado de delu.js)
// Nota: elementos opcionais (filtros/form) só executam se existirem no DOM.

window.currentUser = window.currentUser || '';
window.currentUserId = window.currentUserId || null;
window.FOLLOWING = window.FOLLOWING || new Set();

// Preload seguindo do usuário atual para esconder botões "Seguir" logo de início
if(window.currentUserId){
  fetch(`/api/seguindo/${window.currentUserId}`)
    .then(r=>r.json())
    .then(list=>{ try{ (list||[]).forEach(u=>{ if(u && u.username) window.FOLLOWING.add(u.username); }); }catch(e){} })
    .catch(()=>{});
}

function safeGet(id){ return document.getElementById(id); }

// Envio de nova postagem (se form existir)
(function initPostForm(){
  const form = safeGet('post-form');
  if(!form) return;
  form.addEventListener('submit', e => {
    e.preventDefault();
    const conteudoEl = safeGet('post-content');
    const conteudo = conteudoEl ? conteudoEl.value : '';
    if(!conteudo.trim()) return;
    fetch('/api/posts', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({conteudo}) })
      .then(r=>{ if(r.ok){ if(conteudoEl) conteudoEl.value=''; loadPosts(); } else alert('Erro ao publicar'); });
  });
})();

function parseTextWithLinks(text) {
  const esc = s => (s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
  let out = esc(text||'');
  out = out.replace(/@([\wÁ-Úá-ú0-9_]+)/g, (m,u)=>`<a href="#" class="mention" data-username="${u}" style="color:#2563eb;text-decoration:none;font-weight:700;">@${u}</a>`);
  out = out.replace(/#([\wÁ-Úá-ú0-9_]+)/g, (m,t)=>`<a href="/hashtag/${t}" class="hashtag" style="color:#7c3aed;text-decoration:none;">#${t}</a>`);
  return out;
}

function loadPosts(params={}) {
  const usp = new URLSearchParams(params);
  
  // Fetch both posts and divulgacao items
  Promise.all([
    fetch('/api/posts'+(usp.toString()?`?${usp.toString()}`:'')).then(r=>r.json()),
    fetch('/api/divulgacao').then(r=>r.json()).catch(()=>({items:[]}))
  ])
    .then(([posts, divulgacaoData]) => {
      const feed = safeGet('feed-list');
      if(!feed) return;
      feed.innerHTML='';
      
      if(!posts || !posts.length){
        const msg = document.createElement('p');
        msg.textContent='Nenhum post encontrado.';
        msg.style.cssText='text-align:center;color:#666;padding:2rem;';
        feed.appendChild(msg); return;
      }
      
      const divulgacaoItems = divulgacaoData.items || [];
      const isMobile = window.innerWidth < 980;
      
      // Render posts with divulgacao items inserted every 12 posts (mobile only)
      posts.forEach((post, index) => {
        renderPost(post, feed);
        
        // Insert divulgacao card every 12 posts on mobile
        if(isMobile && divulgacaoItems.length > 0 && (index + 1) % 12 === 0) {
          const divIndex = Math.floor(index / 12) % divulgacaoItems.length;
          const divItem = divulgacaoItems[divIndex];
          renderDivulgacaoCard(divItem, feed);
        }
      });
    })
    .catch(err => console.error('Erro feed', err));
}

function renderDivulgacaoCard(divItem, feed) {
  const card = document.createElement('div');
  card.className = 'divulgacao-feed-card';
  card.style.cssText = 'background:#fff; border:1px solid #e5e7eb; border-radius:22px; padding:1rem 1.1rem 1.05rem; margin-bottom:2rem; box-shadow:0 8px 22px rgba(0,0,0,.1);';
  
  let imageHtml = '';
  if(divItem.imagem) {
    const imgsrc = divItem.imagem.startsWith('http') ? divItem.imagem : `/static/${divItem.imagem}`;
    imageHtml = `<img src="${imgsrc}" alt="${divItem.titulo}" style="width:100%; border-radius:14px; margin:0 0 .65rem; box-shadow:0 4px 12px rgba(0,0,0,.12);" loading="lazy" />`;
  }
  
  let linkHtml = '';
  if(divItem.link) {
    linkHtml = `<a href="${divItem.link}" target="_blank" rel="noopener" style="display:inline-block; font-size:.68rem; font-weight:700; background:#9B5DE5; color:#fff; padding:.5rem .9rem .45rem; border-radius:14px; text-decoration:none; letter-spacing:.5px; margin-top:.35rem;">Abrir →</a>`;
  }
  
  card.innerHTML = `
    <div style="display:flex; align-items:center; gap:.5rem; margin-bottom:.6rem;">
      <span style="font-size:1.1rem;">📣</span>
      <strong style="font-size:.8rem; letter-spacing:.5px; color:#6233B5; font-weight:800;">Novidade</strong>
    </div>
    <strong style="display:block; font-size:.78rem; letter-spacing:.4px; color:#333; margin:0 0 .45rem; font-weight:800;">${divItem.titulo}</strong>
    ${imageHtml}
    ${divItem.texto ? `<p style="margin:0 0 .4rem; font-size:.7rem; line-height:1.4; color:#555; font-weight:600;">${divItem.texto}</p>` : ''}
    ${linkHtml}
  `;
  
  feed.appendChild(card);
}

// Renderiza imagens (uma ou múltiplas) separadas por '|'
function renderPostImages(raw){
  if(!raw) return '';
  const parts = raw.split('|').filter(Boolean);
  if(!parts.length) return '';
  // Helper: determinar src correto (URL ou path local)
  const getSrc = (path) => /^https?:\/\//i.test(path) ? path : `/static/${path}`;
  if(parts.length === 1){
    const src = getSrc(parts[0]);
    return `<div class="post-media"><img src="${src}" alt="Imagem do post" onclick="openImageModal('${src}')" onerror="this.style.display='none'"/></div>`;
  }
  // Grid simples para múltiplas
  const cls = parts.length===2? 'grid-2' : (parts.length===3? 'grid-3':'grid-4');
  const imgs = parts.map(p=>{
    const src = getSrc(p);
    return `<div class="pm-item"><img src="${src}" alt="Imagem do post" onclick="openImageModal('${src}')" onerror="this.style.display='none'"/></div>`;
  }).join('');
  return `<div class="post-media multi ${cls}">${imgs}</div>`;
}

function renderPost(post, feed){
  const article = document.createElement('article');
  article.className='post';
  article.dataset.postId = post.id;
  const fotoPerfil = post.foto_perfil ? post.foto_perfil : 'img/perfil.png';
  const likeLabel = post.liked ? '❤️ Curtido' : '❤️ Curtir';
  const likeClass = post.liked ? 'like-btn liked' : 'like-btn';
  let btnSeguir = '';
  if(window.currentUser && post.usuario !== window.currentUser && !(window.FOLLOWING && window.FOLLOWING.has(post.usuario))){
    btnSeguir = `<button class="seguir-btn" data-usuario="${post.usuario}" onclick="seguirOuDeixarUsuario(this)">Seguir</button>`;
  }
  article.innerHTML = `
    <div class="post-header" style="display:flex;align-items:center;justify-content:space-between;">
      <div style="display:flex;align-items:center;gap:0.7rem;">
        <img src="/static/${fotoPerfil}" alt="Foto de perfil" class="post-avatar" data-username="${post.usuario}" style="width:40px;height:40px;border-radius:50%;object-fit:cover;border:2px solid #eee;cursor:pointer;">
        <span style="cursor:pointer;" class="post-username" data-username="${post.usuario}"><strong>@${post.usuario}</strong> <span style="color:#888;">${post.data}</span></span>
      </div>
      <div style="display:flex;align-items:center;gap:0.5rem;">
        ${btnSeguir}
        <div class="post-menu-container" style="position:relative;">
          <button class="post-menu-btn" onclick="togglePostMenu(this)">⋯</button>
          <div class="post-menu" style="display:none;position:absolute;right:0;top:28px;background:#fff;border:1px solid #ccc;border-radius:8px;box-shadow:0 2px 8px #0002;z-index:10;min-width:160px;">
            <button onclick="compartilharPost(${post.id})">Compartilhar</button>
            <button onclick="relatarPost(${post.id})" style="color:#e67e22;">Relatar</button>
            ${window.currentUser===post.usuario?`<button style="color:#c0392b;" onclick="deletarPost(${post.id})">Excluir</button>`:''}
          </div>
        </div>
      </div>
    </div>
    <p class="post-content">${parseTextWithLinks(post.conteudo)}</p>
    ${ (post.images && post.images.length) ? renderPostImages(post.images.join('|')) : (post.imagem ? renderPostImages(post.imagem) : '') }
    <div class="likes-list"></div>
    <div class="post-actions">
      <button class="${likeClass}" onclick="likePost(${post.id}, this)">${likeLabel}</button>
      <button class="comment-btn" onclick="showCommentBox(this)">💬 Comentar</button>
    </div>`;
  feed.appendChild(article);
  loadComments(post.id, article);
  updateLikesDisplay(post.id, article);
  if(btnSeguir) atualizarBotaoSeguir(article, post.usuario);
}

function atualizarBotaoSeguir(article, username){
  try{
    const btn = article.querySelector('.seguir-btn');
    if(!btn) return;
    if(window.FOLLOWING && window.FOLLOWING.has(username)){
      btn.remove();
    }
  }catch(e){}
}

function seguirOuDeixarUsuario(btn){
  const username = btn.getAttribute('data-usuario');
  fetch(`/api/usuarios/username/${username}`).then(r=>r.json()).then(user=>{
    if(!user.id) return;
    const jaSegue = btn.classList.contains('seguindo');
    fetch(`/api/seguir/${user.id}`, {method: jaSegue?'DELETE':'POST'}).then(()=>{
      if(jaSegue){
        // deixou de seguir: remover do set e re-exibir botões no feed
        try{ window.FOLLOWING && window.FOLLOWING.delete(username); }catch(e){}
        document.querySelectorAll(`.seguir-btn[data-usuario="${username}"]`).forEach(b=>{
          b.textContent = 'Seguir'; b.className = 'seguir-btn'; b.style.display='';
        });
      } else {
        // passou a seguir: adicionar ao set e remover botões do feed
        try{ window.FOLLOWING && window.FOLLOWING.add(username); }catch(e){}
        document.querySelectorAll(`.seguir-btn[data-usuario="${username}"]`).forEach(b=> b.remove());
      }
    });
  });
}

function togglePostMenu(btn){
  const menu = btn.parentElement.querySelector('.post-menu');
  if(menu.style.display==='block') menu.style.display='none';
  else { document.querySelectorAll('.post-menu').forEach(m=>m.style.display='none'); menu.style.display='block'; }
  event.stopPropagation();
}

document.addEventListener('click', ()=> document.querySelectorAll('.post-menu').forEach(m=>m.style.display='none'));

function likePost(postId, btn){
  fetch(`/api/posts/${postId}/like`, {method:'POST'}).then(r=>r.json()).then(data=>{
    if(data.liked){ btn.classList.add('liked'); btn.textContent='❤️ Curtido'; }
    else { btn.classList.remove('liked'); btn.textContent='❤️ Curtir'; }
    updateLikesDisplay(postId, btn.closest('.post'));
  });
}

function updateLikesDisplay(postId, postElem){
  fetch(`/api/posts/${postId}/likes`).then(r=>r.json()).then(users=>{
    let likesDiv = postElem.querySelector('.likes-list');
    if(!likesDiv){ likesDiv = document.createElement('div'); likesDiv.className='likes-list'; postElem.insertBefore(likesDiv, postElem.querySelector('.post-actions')); }
    if(!users.length){ likesDiv.innerHTML=''; return; }
    const curtiu = users.includes(window.currentUser);
    likesDiv.innerHTML = `<span class="likes-line" data-post="${postId}" style="cursor:pointer;">`+
      (curtiu?'<strong style="color:#7c3aed;">Você</strong>':'')+
      (curtiu && users.length>1?' e ':'')+
      users.filter(u=>u!==window.currentUser).slice(0,2).map(u=>`<span class="like-user">${u}</span>`).join(', ')+
      (users.length>3?` e <span class="like-user">mais ${users.length-3}</span>`:'')+
      ' curtiram</span>';
  });
}

function loadComments(postId, postElem){
  fetch(`/api/posts/${postId}/comentarios`).then(r=>r.json()).then(comments=>{
    let commentsDiv = postElem.querySelector('.comments-list');
    if(!commentsDiv){ commentsDiv = document.createElement('div'); commentsDiv.className='comments-list'; postElem.appendChild(commentsDiv); }
    commentsDiv.innerHTML = comments.map(c=>`<div class="comment"><strong>${c.usuario}</strong>: ${parseTextWithLinks(c.conteudo)}</div>`).join('');
  });
}

function showCommentBox(btn){
  const postElem = btn.closest('.post');
  let box = postElem.querySelector('.comment-box');
  if(box){ box.remove(); return; }
  box = document.createElement('div'); box.className='comment-box';
  box.innerHTML = `<textarea class="comment-input" placeholder="Escreva um comentário..."></textarea><button onclick="submitComment(this)">Enviar</button>`;
  postElem.insertBefore(box, btn.parentElement.nextSibling);
}

function submitComment(btn){
  const postElem = btn.closest('.post');
  const postId = postElem.dataset.postId;
  const textarea = postElem.querySelector('.comment-input');
  fetch(`/api/posts/${postId}/comentarios`, {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({conteudo: textarea.value})})
    .then(()=>{ textarea.value=''; loadComments(postId, postElem); });
}

function compartilharPost(postId){
  const url = `${window.location.origin}/post/${postId}`;
  navigator.clipboard.writeText(url).then(()=> alert('Link copiado!'));
}

function relatarPost(postId){ alert('Relatar post '+postId+' (modal simplificado)'); }
function deletarPost(postId){ if(!confirm('Excluir este post?')) return; fetch(`/api/posts/${postId}`, {method:'DELETE'}).then(()=> loadPosts()); }

function executarBusca(){ const termo = (safeGet('search-input')?.value||'').trim(); loadPosts(termo?{q:termo}:{}) }

document.addEventListener('click', e=>{
  const a = e.target.closest('a.hashtag');
  if(a){ e.preventDefault(); const tag = a.textContent.trim(); const sinput = safeGet('search-input'); if(sinput) sinput.value = tag; loadPosts({q:tag}); }
  const m = e.target.closest('a.mention');
  if(m){ e.preventDefault(); const uname = m.getAttribute('data-username'); if(!uname) return; if(window.currentUser && uname===window.currentUser){ window.location.href='/perfil'; return; } fetch(`/api/usuarios/username/${uname}`).then(r=>r.json()).then(u=>{ if(u.id) window.location.href='/perfil/'+u.id; }); }
});

document.addEventListener('DOMContentLoaded', ()=> loadPosts());

// Expor algumas funções no escopo global usadas por onclick inline
window.executarBusca = executarBusca;
window.likePost = likePost;
window.showCommentBox = showCommentBox;
window.submitComment = submitComment;
window.compartilharPost = compartilharPost;
window.relatarPost = relatarPost;
window.deletarPost = deletarPost;
window.togglePostMenu = togglePostMenu;
window.seguirOuDeixarUsuario = seguirOuDeixarUsuario;

