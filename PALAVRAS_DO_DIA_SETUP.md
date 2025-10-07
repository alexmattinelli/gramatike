# Palavras do Dia - Setup Guide

## Descrição

Feature educacional que substitui o card de "Informações" por "Palavras do Dia" no Gramátike Edu. A cada dia, uma nova palavra ou expressão relacionada à linguagem neutra é exibida, com opções para o usuário aprender seu significado ou criar uma frase usando a palavra.

## Setup Inicial

### 1. Executar Migração do Banco de Dados

```bash
flask db upgrade
```

Ou, se você criou o banco com `db.create_all()`, as tabelas já foram criadas automaticamente:
- `palavra_do_dia`
- `palavra_do_dia_interacao`

### 2. Popular com Palavras Iniciais

Execute o script de seed para adicionar as 5 palavras iniciais:

```bash
python3 scripts/seed_palavras_do_dia.py
```

Este script adiciona as seguintes palavras:
1. **elu** - Pronome neutro
2. **todes** - Forma neutra de todos/todas
3. **amigue** - Forma neutra de amigo/amiga
4. **pessoa não binárie** - Identidade não binária
5. **linguagem neutra** - Conceito de linguagem inclusiva

## Como Funciona

### Rotação Diária

A palavra exibida muda automaticamente a cada dia, baseada no dia do ano:
- Dia 1 do ano → palavra 1 (elu)
- Dia 2 do ano → palavra 2 (todes)
- Dia 3 do ano → palavra 3 (amigue)
- Dia 4 do ano → palavra 4 (pessoa não binárie)
- Dia 5 do ano → palavra 5 (linguagem neutra)
- Dia 6 do ano → palavra 1 (elu) novamente...

### Interações do Usuário

Cada usuário pode interagir **uma vez por dia** com a palavra, escolhendo uma das opções:

1. **✍️ Quero criar uma frase**
   - Abre um formulário para escrever uma frase
   - Salva a frase no banco de dados
   - Mostra mensagem de sucesso

2. **🔍 Quero saber o significado**
   - Exibe a explicação da palavra
   - Registra que o usuário visualizou
   - Mostra mensagem de sucesso

### Mensagem de Incentivo

Após qualquer interação, o usuário vê:
> "Incrível! Hoje tu aprendeu uma nova forma de incluir todes 💜"

## API Endpoints

### GET `/api/palavra-do-dia`

Retorna a palavra do dia atual.

**Resposta:**
```json
{
  "id": 1,
  "palavra": "elu",
  "significado": "Elu é um pronome neutro usado por pessoas que não se identificam nem com o masculino nem com o feminino.",
  "ja_interagiu": false
}
```

### POST `/api/palavra-do-dia/interagir`

Registra uma interação do usuário (requer autenticação).

**Body:**
```json
{
  "palavra_id": 1,
  "tipo": "frase",
  "frase": "Elu é uma pessoa incrível!"
}
```

ou

```json
{
  "palavra_id": 1,
  "tipo": "significado"
}
```

**Resposta:**
```json
{
  "success": true,
  "mensagem": "Incrível! Hoje tu aprendeu uma nova forma de incluir todes 💜"
}
```

## Gerenciamento

### Adicionar Nova Palavra

```python
from gramatike_app import create_app
from gramatike_app.models import db, PalavraDoDia

app = create_app()
with app.app_context():
    palavra = PalavraDoDia(
        palavra='delu',
        significado='Delu é uma variação de "dele/dela", usada de forma neutra.',
        ordem=6,  # próxima na sequência
        ativo=True,
        created_by=1  # ID do admin
    )
    db.session.add(palavra)
    db.session.commit()
```

### Desativar uma Palavra

```python
palavra = PalavraDoDia.query.get(1)
palavra.ativo = False
db.session.commit()
```

### Ver Interações dos Usuários

```python
from gramatike_app.models import PalavraDoDiaInteracao

interacoes = PalavraDoDiaInteracao.query.filter_by(palavra_id=1).all()
for i in interacoes:
    print(f"Usuário {i.usuario.username}: {i.tipo}")
    if i.frase:
        print(f"  Frase: {i.frase}")
```

## Estrutura do Banco de Dados

### Tabela `palavra_do_dia`

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | Integer | Chave primária |
| palavra | String(200) | A palavra ou expressão |
| significado | Text | Explicação inclusiva |
| ordem | Integer | Ordem para rotação (indexed) |
| ativo | Boolean | Se está ativa (indexed) |
| created_at | DateTime | Data de criação (indexed) |
| created_by | Integer | FK para User |

### Tabela `palavra_do_dia_interacao`

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | Integer | Chave primária |
| palavra_id | Integer | FK para palavra_do_dia (indexed) |
| usuario_id | Integer | FK para User (indexed) |
| tipo | String(20) | 'frase' ou 'significado' |
| frase | Text | Frase criada (se tipo='frase') |
| created_at | DateTime | Data da interação (indexed) |

## Testes

Para testar a feature:

1. Acesse `/educacao` estando logado
2. Veja a palavra do dia no card "💜 Palavras do Dia"
3. Clique em uma das opções de interação
4. Verifique a mensagem de sucesso
5. Recarregue a página - deve mostrar que você já interagiu hoje
