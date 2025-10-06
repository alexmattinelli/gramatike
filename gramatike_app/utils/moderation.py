import re
import unicodedata
from functools import lru_cache

try:
    # A importação direta evita dependência circular quando create_app registra blueprints
    from gramatike_app.models import BlockedWord
    from gramatike_app.models import db  # para sessões contextuais
except Exception:
    BlockedWord = None
    db = None


def _strip_accents(s: str) -> str:
    try:
        return ''.join(c for c in unicodedata.normalize('NFD', s or '') if unicodedata.category(c) != 'Mn')
    except Exception:
        return s or ''


# Palavras/expressões alvo (listas não exaustivas, foco em reduzir abuso óbvio)
_PROFANITIES = [
    r"\b(porra|caralho|merda|pqp|vtnc|vsf|fdp|foda\s*-?se|arrombado|arrombada|otario|otária|otaria)\b",
]
_HATE = [
    r"\b(viado|bicha|traveco|sapat[ãa]o|preto\s*imundo|macaco|retardad[oa]|mongoloide)\b",
]
_SEXUAL_NUDITY = [
    r"\b(nude|nudes|nudez|pelad[oa]s?)\b",
    r"\b(penis|p[êe]nis|pau|piroca|pica|vagina|buceta|cl[íi]toris|mamilos?|seios?|peitos?)\b",
    r"\b(porn[oô]|pornografia|nsfw|sexo\s*expl[íi]cito)\b",
    r"\b(onlyfans|xvideos|pornhub|xnxx|redtube|rule34)\b",
    r"\b(pack\s*(do|da))\b",
    r"\b(18\+|\+18)\b",
]

_COMPILED_PROF = [re.compile(p, re.IGNORECASE) for p in _PROFANITIES]
_COMPILED_HATE = [re.compile(p, re.IGNORECASE) for p in _HATE]
_COMPILED_SEX = [re.compile(p, re.IGNORECASE) for p in _SEXUAL_NUDITY]


@lru_cache(maxsize=1)
def _compiled_custom_terms():
    patterns = []
    try:
        if BlockedWord is None:
            return patterns
        # Consulta simples: todas as palavras
        rows = BlockedWord.query.all()
        for r in rows:
            # Escapa termo e cria \b se for palavra simples; se contiver espaços, usa como substring
            term = _strip_accents((r.term or '').strip().lower())
            if not term:
                continue
            if ' ' in term:
                pat = re.compile(re.escape(term), re.IGNORECASE)
            else:
                pat = re.compile(r"\b" + re.escape(term) + r"\b", re.IGNORECASE)
            patterns.append((pat, (r.category or 'custom').lower()))
    except Exception:
        # Em casos de erro (ex.: sem contexto app), ignore
        return []
    return patterns

def refresh_custom_terms_cache():
    try:
        _compiled_custom_terms.cache_clear()
    except Exception:
        pass


def check_text(text: str):
    """Retorna (allowed: bool, category: str|None, match: str|None)."""
    t = _strip_accents((text or '').lower())
    if not t.strip():
        return True, None, None
    # Admin-defined terms primeiro (prioridade)
    for pat, cat in _compiled_custom_terms():
        m = pat.search(t)
        if m:
            return False, cat or 'custom', m.group(0)
    for pat in _COMPILED_HATE:
        m = pat.search(t)
        if m:
            return False, 'hate', m.group(0)
    for pat in _COMPILED_PROF:
        m = pat.search(t)
        if m:
            return False, 'profanity', m.group(0)
    for pat in _COMPILED_SEX:
        m = pat.search(t)
        if m:
            return False, 'nudity', m.group(0)
    return True, None, None


def check_image_hint(path_or_text: str):
    """Checagem simples baseada em pista textual (URL/domínio/nome do arquivo)."""
    return check_text(path_or_text)


def refusal_message_pt(category: str) -> str:
    return "Não posso ajudar com discurso de ódio, xingamentos ou conteúdo sexual/nudez. Vamos manter um espaço seguro e respeitoso."
