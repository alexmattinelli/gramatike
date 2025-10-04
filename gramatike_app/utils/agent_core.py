from dataclasses import dataclass
from typing import List, Optional


@dataclass
class AgentStep:
    thought: str
    suggestion: Optional[str] = None


def plan_and_reflect(user_msg: str, draft: str) -> List[AgentStep]:
    steps: List[AgentStep] = []
    low = (draft or '').strip().lower()
    # Plano: garantir resposta direta, sem preâmbulo e com exemplo quando fizer sentido
    steps.append(AgentStep(thought="Verificar diretividade e cortar preâmbulos."))
    if any(low.startswith(s) for s in [
        'vamos lá', 'vamos la', 'certo', 'beleza', 'ok', 'entendi', 'posso ', 'me diga', 'vou te explicar'
    ]):
        steps.append(AgentStep(thought="Cortar abertura meta.", suggestion="Remova a primeira frase de abertura/meta."))
    # Se o usuário perguntou "como" ou pediu "passo a passo", garantir bullets curtos
    msg_low = (user_msg or '').lower()
    if 'como ' in msg_low or 'passo a passo' in msg_low:
        steps.append(AgentStep(thought="Garantir passos numerados curtos."))
    # Se a resposta é muito curta e sem exemplo, sugerir 1 exemplo
    if len(draft or '') < 140 and ('\n' not in draft):
        steps.append(AgentStep(thought="Adicionar exemplo curto.", suggestion="Inclua 1 exemplo curto e concreto."))
    return steps


def apply_suggestions(draft: str, steps: List[AgentStep]) -> str:
    s = (draft or '').strip()
    for st in steps:
        if st.suggestion == "Remova a primeira frase de abertura/meta.":
            # Remove a primeira sentença
            import re
            s = re.sub(r"^.*?[\.!?]\s+", "", s, count=1)
        elif st.suggestion == "Inclua 1 exemplo curto e concreto.":
            s += "\n\nExemplo: use o procedimento no seu contexto e valide o resultado em 1 passo simples."
    return s
