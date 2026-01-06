// Feed page template
import { renderBase } from '../base';
import { renderNovidades } from '../components/novidades';
import { escapeHtml, getAssetUrl } from '../utils';
import type { User, PostWithUser } from '../../types';

interface Divulgacao {
  id: number;
  titulo: string;
  texto?: string;
  imagem?: string;
  link?: string;
}

interface FeedPageProps {
  user: User | null;
  posts: PostWithUser[];
  divulgacoes: Divulgacao[];
}

/**
 * Render the feed page with posts and announcements
 */
export function renderFeed({ user, posts, divulgacoes }: FeedPageProps): string {
  const content = `
    <div class="feed-container">
      ${renderNovidades(divulgacoes)}
      
      <section class="feed">
        <h2>Feed</h2>
        ${posts.length > 0 ? posts.map(p => `
          <article class="post" data-post-id="${p.id}">
            <div class="post-header">
              <img src="${getAssetUrl(p.foto_perfil)}" alt="Avatar" class="avatar">
              <strong>${escapeHtml(p.username || 'Anônimo')}</strong>
            </div>
            <div class="post-content">
              <p>${escapeHtml(p.conteudo || '')}</p>
              ${p.imagem ? `<img src="${getAssetUrl(p.imagem)}" alt="Post image" class="post-image">` : ''}
            </div>
            <div class="post-actions">
              <button class="like-btn" data-post-id="${p.id}">
                ❤️ ${p.like_count || 0}
              </button>
              <span class="comment-count">💬 ${p.comment_count || 0}</span>
            </div>
          </article>
        `).join('') : '<p class="no-posts">Nenhum post ainda. Seja o primeiro a postar!</p>'}
      </section>
    </div>
  `;
  
  return renderBase({ content, pageTitle: 'Feed', user });
}
