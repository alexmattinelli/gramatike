// Novidades (announcements/news) component
import { escapeHtml, getAssetUrl } from '../utils';

interface Divulgacao {
  id: number;
  titulo: string;
  texto?: string;
  imagem?: string;
  link?: string;
}

/**
 * Render the Novidades section with announcements
 */
export function renderNovidades(divulgacoes: Divulgacao[]): string {
  if (!divulgacoes?.length) return '';
  
  return `
    <section class="novidades">
      <h2>Novidades</h2>
      ${divulgacoes.map(d => `
        <div class="divulgacao">
          <h3>${escapeHtml(d.titulo)}</h3>
          ${d.imagem ? `<img src="${getAssetUrl(d.imagem)}" alt="${escapeHtml(d.titulo)}">` : ''}
          ${d.texto ? `<p>${escapeHtml(d.texto)}</p>` : ''}
          ${d.link ? `<a href="${escapeHtml(d.link)}" target="_blank">Saiba mais</a>` : ''}
        </div>
      `).join('')}
    </section>
  `;
}
