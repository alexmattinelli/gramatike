import csv, json, sys, os
from typing import List, Dict
from gramatike_app import create_app
from gramatike_app.models import db, EduContent
from gramatike_app.utils.rag_embeddings import ingest_docs

# Uso:
#   python -m scripts.import_rag --jsonl caminho\dados.jsonl --tipo artigo --tag corpusA
#   python -m scripts.import_rag --csv caminho\dados.csv --text-col texto --title-col titulo --url-col url --tipo artigo --tag corpusB


def load_jsonl(path: str) -> List[Dict]:
    items = []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            items.append(json.loads(line))
    return items


def load_csv(path: str, text_col: str, title_col: str = None, url_col: str = None) -> List[Dict]:
    out = []
    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            out.append({
                'text': row.get(text_col) or '',
                'title': (row.get(title_col) or '') if title_col else '',
                'url': (row.get(url_col) or '') if url_col else ''
            })
    return out


def main(argv):
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--jsonl')
    ap.add_argument('--csv')
    ap.add_argument('--text-col')
    ap.add_argument('--title-col')
    ap.add_argument('--url-col')
    ap.add_argument('--tipo', default='artigo')
    ap.add_argument('--tag', default='')
    ap.add_argument('--no-db', action='store_true', help='Não salvar no DB, só indexar embeddings')
    args = ap.parse_args(argv)

    docs: List[Dict] = []
    items: List[Dict] = []
    if args.jsonl:
        items = load_jsonl(args.jsonl)
    elif args.csv:
        if not args.text_col:
            print('CSV exige --text-col')
            return 2
        items = load_csv(args.csv, args.text_col, args.title_col, args.url_col)
    else:
        print('Informe --jsonl ou --csv')
        return 2

    app = create_app()
    with app.app_context():
        created = 0
        batch_docs = []
        for it in items:
            t = (it.get('text') or it.get('corpo') or it.get('resumo') or '').strip()
            if not t:
                continue
            title = (it.get('title') or it.get('titulo') or t[:60]+'…')[:220]
            url = (it.get('url') or '')[:500]
            if not args.no_db:
                ec = EduContent(tipo=args.tipo, titulo=title, corpo=t, url=url)
                db.session.add(ec)
                created += 1
            batch_docs.append({'source':'ext','id': None, 'title': title, 'url': url, 'text': t, 'tag': args.tag})
        if not args.no_db and created:
            db.session.commit()
        # Indexar embeddings em lotes para economizar memória
        B = 512
        total = 0
        for i in range(0, len(batch_docs), B):
            total += ingest_docs(batch_docs[i:i+B])
        print(f'Criados no DB: {created}; Indexados: {total}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
