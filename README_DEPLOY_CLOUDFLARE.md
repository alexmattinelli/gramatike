# Deploy Gramátike no Cloudflare Pages Functions

## Passos para Deploy

1. **Remova qualquer comando de build personalizado do painel do Cloudflare Pages.**
   - Se necessário, use apenas:
     ```
     pip install -r requirements.txt
     ```
   - Ou deixe o campo de build vazio.

2. **Garanta que o diretório `functions/` está presente**
   - Todos os handlers Python devem estar em `functions/`.

3. **Garanta que as dependências estão em `requirements.txt`**
   - Exemplo: `jinja2`, `starlette`, etc.

4. **Se quiser, use o script de build automático:**
   - No campo de build do painel, coloque:
     ```
     bash build.sh
     ```

5. **Output directory:**
   - Deixe vazio ou use `public` se tiver assets estáticos.

6. **Variáveis de ambiente:**
   - Configure o binding do D1 normalmente no `wrangler.toml`.
   - Não precisa de `DATABASE_URL`.

7. **Deploy!**

Se aparecer erro de build, envie a mensagem completa para diagnóstico.
