#!/bin/bash
# 🔄 Conversor em Lote - Todas as Páginas Educacionais

echo "🚀 Convertendo todas as páginas Flask → Workers..."
echo ""

# 1. Exercícios
echo "📝 1/5 - Convertendo Exercícios..."
python flask_to_workers.py gramatike_app/templates/exercicios.html > codigo_exercicios.py
echo "   ✅ codigo_exercicios.py gerado"
echo ""

# 2. Artigos
echo "📝 2/5 - Convertendo Artigos..."
python flask_to_workers.py gramatike_app/templates/artigos.html > codigo_artigos.py
echo "   ✅ codigo_artigos.py gerado"
echo ""

# 3. Apostilas
echo "📝 3/5 - Convertendo Apostilas..."
python flask_to_workers.py gramatike_app/templates/apostilas.html > codigo_apostilas.py
echo "   ✅ codigo_apostilas.py gerado"
echo ""

# 4. Podcasts
echo "📝 4/5 - Convertendo Podcasts..."
python flask_to_workers.py gramatike_app/templates/podcasts.html > codigo_podcisos.py
echo "   ✅ codigo_podcasts.py gerado"
echo ""

# 5. Dinâmicas
echo "📝 5/5 - Convertendo Dinâmicas..."
python flask_to_workers.py gramatike_app/templates/dinamicas.html > codigo_dinamicas.py
echo "   ✅ codigo_dinamicas.py gerado"
echo ""

echo "════════════════════════════════════════════════════════"
echo "✅ CONVERSÃO COMPLETA!"
echo "════════════════════════════════════════════════════════"
echo ""
echo "📁 Arquivos gerados:"
echo "   - codigo_exercicios.py"
echo "   - codigo_artigos.py"
echo "   - codigo_apostilas.py"
echo "   - codigo_podcasts.py"
echo "   - codigo_dinamicas.py"
echo ""
echo "⚠️  PRÓXIMO PASSO:"
echo "   1. Revise cada arquivo gerado"
echo "   2. Ajuste loops FOR e condicionais IF"
echo "   3. Substitua em index.py as funções correspondentes:"
echo "      - _exercicios_page (~linha 3160)"
echo "      - _artigos_page (~linha 3209)"
echo "      - _apostilas_page (~linha 3254)"
echo "      - _podcasts_page (~linha 3300)"
echo "      - _dinamicas_page (~linha 3124)"
echo "   4. Deploy: npx wrangler deploy"
echo ""
