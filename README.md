<<<<<<< HEAD
# gramatike
=======
# Gramatike

>>>>>>> d54191b (Primeiro commit - adicionando arquivos do projeto)
### Vercel (via GitHub)
1. Tenha este repositório no GitHub (já está em `main`).
2. No painel da Vercel, importe o projeto a partir deste repositório.
3. Build & Output Settings:
	- Framework: Other
	- Python Runtime: conforme `vercel.json` (python3.12)
	- Output: não precisa especificar, `api/index.py` expõe o Flask.
4. Variáveis de ambiente (Project Settings > Environment Variables):
	- `SECRET_KEY`: uma string segura
	- (Opcional) `DATABASE_URL`: use Postgres gerenciado se precisar de persistência real no edge (recomendado para produção). Caso contrário, o SQLite em `instance/app.db` pode não ser persistente no ambiente serverless da Vercel.

### Executar local
Ver seção “Development”.
