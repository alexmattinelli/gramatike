import sys
from gramatike_app import create_app
from gramatike_app.utils.ingest_local import build_docs_from_folder
from gramatike_app.utils.rag_embeddings import ingest_docs, index_exists, build_index_from_db

def main():
    if len(sys.argv) < 2:
        print('Uso: python ingest_folder.py <caminho_da_pasta> [tag]')
        sys.exit(1)
    folder = sys.argv[1]
    tag = sys.argv[2] if len(sys.argv) > 2 else 'local'
    app = create_app()
    with app.app_context():
        docs = build_docs_from_folder(folder, tag=tag)
        if not docs:
            print('Nenhum documento legível encontrado.')
            return
        n = ingest_docs(docs)
        print(f'Ingeridos {n} chunks do diretório {folder}.')
        if not index_exists():
            try:
                total, dim = build_index_from_db()
                print(f'Índice criado com {total} chunks, dim={dim}.')
            except Exception as e:
                print('Falha ao criar índice:', e)

if __name__ == '__main__':
    main()
