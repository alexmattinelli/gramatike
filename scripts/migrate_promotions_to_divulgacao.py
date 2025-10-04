from gramatike_app import create_app
from gramatike_app.models import db, Promotion, Divulgacao
from datetime import datetime

def migrate():
    app = create_app()
    with app.app_context():
        created = 0
        skipped = 0
        missing = 0
        promos = Promotion.query.order_by(Promotion.created_at.asc()).all()
        for p in promos:
            # Área padrão: 'edu' (ajuste se necessário)
            area = 'edu'
            # Regra simples: só migra imagens; vídeos/embeds ficam como link
            imagem = p.media_path if (p.media_type == 'image' and p.media_path) else None
            texto = (p.descricao or '').strip() or None
            link = (p.link_destino or '').strip() or None
            # Evitar duplicar por título+imagem (heurística leve)
            exists = (Divulgacao.query
                        .filter(Divulgacao.titulo == p.titulo)
                        .filter((Divulgacao.imagem == imagem) | ((Divulgacao.imagem.is_(None)) & (imagem is None)))
                        .first())
            if exists:
                skipped += 1
                continue
            d = Divulgacao(
                area=area,
                titulo=p.titulo,
                texto=texto,
                link=link,
                imagem=imagem,
                ordem=p.ordem or 0,
                ativo=bool(p.ativo),
                show_on_index=True,
                show_on_edu=True,
                created_at=p.created_at or datetime.utcnow(),
            )
            db.session.add(d)
            created += 1
        if created:
            db.session.commit()
        print(f"Migrate Promotions -> Divulgacao: created={created}, skipped={skipped}, total_promotions={len(promos)}")

if __name__ == '__main__':
    migrate()
