import type { PagesFunction } from '@cloudflare/workers-types';
import type { Env } from './types';

export const onRequestGet: PagesFunction<Env> = async ({ env, request }) => {
  try {
    const html = await env.ASSETS.fetch(new URL('/suporte.html', request.url));
    return html;
  } catch (e) {
    return new Response(`
      <!DOCTYPE html>
      <html lang="pt-BR">
      <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Suporte - Gramátike</title>
        <style>
          body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: #f6f5fa;
            color: #32264c;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
            padding: 20px;
          }
          .container {
            background: white;
            padding: 40px;
            border-radius: 18px;
            box-shadow: 0 4px 20px rgba(155, 93, 229, 0.15);
            max-width: 500px;
            width: 100%;
          }
          h1 { color: #9B5DE5; margin-bottom: 20px; }
          a {
            background: #9B5DE5;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 14px;
            cursor: pointer;
            font-size: 16px;
            margin-top: 20px;
            text-decoration: none;
            display: inline-block;
          }
        </style>
      </head>
      <body>
        <div class="container">
          <h1>Suporte</h1>
          <p>Entre em contato: suporte@gramatike.com.br</p>
          <a href="/feed">Voltar ao Feed</a>
        </div>
      </body>
      </html>
    `, { headers: { 'Content-Type': 'text/html' } });
  }
};
