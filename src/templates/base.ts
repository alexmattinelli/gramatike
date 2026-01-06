// Base HTML template for all pages
import { escapeHtml } from './utils';
import type { User } from '../types';

interface BaseTemplateProps {
  content: string;
  pageTitle: string;
  user: User | null;
}

/**
 * Render the base HTML template with navigation and common structure
 */
export function renderBase({ content, pageTitle, user }: BaseTemplateProps): string {
  return `<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${escapeHtml(pageTitle)} - Gramátike</title>
  <link rel="stylesheet" href="/static/css/style.css">
</head>
<body>
  <header>
    <nav>
      <a href="/">Feed</a>
      ${user ? `
        <a href="/novo_post">Novo Post</a>
        <a href="/api/auth/logout">Sair</a>
      ` : `
        <a href="/login">Entrar</a>
      `}
    </nav>
  </header>
  <main>${content}</main>
  <script src="/static/js/main.js"></script>
</body>
</html>`;
}
