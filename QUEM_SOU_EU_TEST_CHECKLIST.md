# 🧪 Checklist de Testes: Dinâmica "Quem sou eu?"

## ✅ Testes Funcionais Básicos

### Criação de Dinâmica
- [ ] **TC01**: Abrir `/dinamicas` como admin
- [ ] **TC02**: Selecionar tipo "Quem sou eu?" no dropdown
- [ ] **TC03**: Preencher campo "O que a pessoa deve descobrir?"
- [ ] **TC04**: Preencher campo "Moral/Mensagem Final"
- [ ] **TC05**: Adicionar item do tipo "Frase"
- [ ] **TC06**: Adicionar item do tipo "Foto"
- [ ] **TC07**: Remover um item
- [ ] **TC08**: Criar dinâmica com sucesso
- [ ] **TC09**: Verificar que dinâmica aparece na lista "Minhas dinâmicas"

### Validações de Criação
- [ ] **TC10**: Tentar criar sem "questao_tipo" (deve falhar)
- [ ] **TC11**: Tentar criar sem "moral" (deve falhar)
- [ ] **TC12**: Tentar criar sem itens (deve falhar)
- [ ] **TC13**: Tentar criar com item sem conteúdo (deve falhar)
- [ ] **TC14**: Criar com apenas 1 item (deve funcionar)
- [ ] **TC15**: Criar com 10+ itens (deve funcionar)

### Participação na Dinâmica
- [ ] **TC16**: Abrir dinâmica criada como usuário comum
- [ ] **TC17**: Ver instruções com questao_tipo correto
- [ ] **TC18**: Clicar em "Começar"
- [ ] **TC19**: Ver primeiro item (frase ou foto)
- [ ] **TC20**: Digitar resposta no campo
- [ ] **TC21**: Clicar em "Próximo"
- [ ] **TC22**: Verificar que resposta foi preservada
- [ ] **TC23**: Clicar em "Anterior"
- [ ] **TC24**: Verificar que pode editar resposta anterior
- [ ] **TC25**: Navegar até último item
- [ ] **TC26**: Ver botão "Finalizar" (não "Próximo")
- [ ] **TC27**: Clicar em "Finalizar"
- [ ] **TC28**: Ver mensagem de confirmação

### Visualização de Respostas
- [ ] **TC29**: Ver badge "Você já completou"
- [ ] **TC30**: Clicar em "Ver Minhas Respostas"
- [ ] **TC31**: Ver todos os itens com respostas
- [ ] **TC32**: Ver moral/mensagem final
- [ ] **TC33**: Clicar novamente (deve ocultar)
- [ ] **TC34**: Tentar responder novamente (deve bloquear)

### Visualização Admin
- [ ] **TC35**: Abrir "Ver respostas" como admin
- [ ] **TC36**: Ver tabela com respostas de usuários
- [ ] **TC37**: Verificar formato "Item X: resposta"
- [ ] **TC38**: Ver username correto
- [ ] **TC39**: Ver timestamp correto

### Exportação CSV
- [ ] **TC40**: Clicar em "Baixar CSV"
- [ ] **TC41**: Verificar download do arquivo
- [ ] **TC42**: Abrir CSV e validar formato
- [ ] **TC43**: Verificar colunas: timestamp, dynamic_id, usuario_id, tipo, content
- [ ] **TC44**: Verificar conteúdo no formato "Item 1: resp1 | Item 2: resp2"

### Edição de Dinâmica
- [ ] **TC45**: Abrir "Editar" como admin criador
- [ ] **TC46**: Verificar campos pré-preenchidos
- [ ] **TC47**: Editar questao_tipo
- [ ] **TC48**: Editar moral
- [ ] **TC49**: Adicionar novo item
- [ ] **TC50**: Remover item existente
- [ ] **TC51**: Editar conteúdo de item
- [ ] **TC52**: Salvar alterações
- [ ] **TC53**: Verificar que mudanças foram aplicadas

## 🎨 Testes de Interface

### Layout Desktop
- [ ] **UI01**: Dropdown exibe "Quem sou eu?" corretamente
- [ ] **UI02**: Campos de criação bem alinhados
- [ ] **UI03**: Items cards com bordas e espaçamento corretos
- [ ] **UI04**: Botões com cores corretas (primários roxos)
- [ ] **UI05**: Quiz centralizado e legível

### Layout Mobile (< 640px)
- [ ] **UI06**: Instruções legíveis em tela pequena
- [ ] **UI07**: Campo de resposta com largura adequada
- [ ] **UI08**: Botões de navegação acessíveis
- [ ] **UI09**: Imagens redimensionam corretamente
- [ ] **UI10**: Moral exibida sem overflow

### Elementos Visuais
- [ ] **UI11**: Contador "Item X de Y" visível
- [ ] **UI12**: Emoji 📝 nas instruções
- [ ] **UI13**: Emoji 💡 na moral
- [ ] **UI14**: Checkmark ✓ na confirmação
- [ ] **UI15**: Setas ← → nos botões de navegação

### Feedback Visual
- [ ] **UI16**: Input focus tem borda destacada
- [ ] **UI17**: Botão hover muda cor
- [ ] **UI18**: Transição suave entre itens
- [ ] **UI19**: Card de moral com fundo destacado
- [ ] **UI20**: Badge "completado" com cor verde

## 🔐 Testes de Segurança

### Autenticação e Autorização
- [ ] **SEC01**: Usuário não-admin não vê botão "Criar"
- [ ] **SEC02**: POST em `/dinamicas/create` sem ser admin retorna 403
- [ ] **SEC03**: Não-admin não pode editar dinâmicas
- [ ] **SEC04**: Não-admin não pode ver `/admin` view
- [ ] **SEC05**: Não pode editar dinâmica de outro admin

### CSRF Protection
- [ ] **SEC06**: Formulário de criação tem csrf_token
- [ ] **SEC07**: Formulário de resposta tem csrf_token
- [ ] **SEC08**: Formulário de edição tem csrf_token
- [ ] **SEC09**: POST sem token é rejeitado

### Validação de Input
- [ ] **SEC10**: XSS em frase é sanitizado
- [ ] **SEC11**: XSS em moral é sanitizado
- [ ] **SEC12**: URL maliciosa em foto não executa script
- [ ] **SEC13**: SQL injection em resposta não afeta DB
- [ ] **SEC14**: Tamanho máximo de resposta é respeitado

### Prevenção de Abusos
- [ ] **SEC15**: Usuário não pode responder duas vezes
- [ ] **SEC16**: Não pode modificar payload via browser
- [ ] **SEC17**: Limites de itens são respeitados
- [ ] **SEC18**: Rate limiting funciona (se implementado)

## 🧩 Testes de Integração

### Fluxo Completo
- [ ] **INT01**: Admin cria → Usuário responde → Admin vê resposta
- [ ] **INT02**: Editar dinâmica ativa preserva respostas
- [ ] **INT03**: Finalizar dinâmica impede novas respostas
- [ ] **INT04**: Reativar dinâmica permite novas respostas
- [ ] **INT05**: Excluir dinâmica remove respostas

### Múltiplos Usuários
- [ ] **INT06**: Dois usuários respondem simultaneamente
- [ ] **INT07**: Respostas não se sobrepõem
- [ ] **INT08**: CSV contém todas as respostas
- [ ] **INT09**: Admin vê todas as respostas separadas

### Diferentes Tipos de Conteúdo
- [ ] **INT10**: Dinâmica só com frases
- [ ] **INT11**: Dinâmica só com fotos
- [ ] **INT12**: Dinâmica mista (frases + fotos)
- [ ] **INT13**: Frase muito longa (1000 caracteres)
- [ ] **INT14**: URL de foto muito longa

## 🚀 Testes de Performance

### Carregamento
- [ ] **PERF01**: Página de criação carrega em < 2s
- [ ] **PERF02**: Quiz carrega em < 1s
- [ ] **PERF03**: Navegação entre itens é instantânea
- [ ] **PERF04**: Submit de respostas em < 1s

### Escalabilidade
- [ ] **PERF05**: Dinâmica com 50 itens funciona
- [ ] **PERF06**: 100 respostas são exibidas no admin
- [ ] **PERF07**: CSV com 1000 linhas é gerado
- [ ] **PERF08**: Imagens grandes não travam navegação

## 🌐 Testes de Navegadores

### Desktop
- [ ] **BROWSER01**: Chrome/Chromium
- [ ] **BROWSER02**: Firefox
- [ ] **BROWSER03**: Safari
- [ ] **BROWSER04**: Edge

### Mobile
- [ ] **BROWSER05**: Chrome Android
- [ ] **BROWSER06**: Safari iOS
- [ ] **BROWSER07**: Firefox Mobile
- [ ] **BROWSER08**: Samsung Internet

## ♿ Testes de Acessibilidade

### Navegação por Teclado
- [ ] **A11Y01**: Tab navega pelos campos
- [ ] **A11Y02**: Enter submete formulário
- [ ] **A11Y03**: Esc fecha modais (se aplicável)
- [ ] **A11Y04**: Setas navegam entre items

### Leitores de Tela
- [ ] **A11Y05**: Labels são lidos corretamente
- [ ] **A11Y06**: Botões anunciam ação
- [ ] **A11Y07**: Progresso é anunciado
- [ ] **A11Y08**: Erros são comunicados

### Contraste e Legibilidade
- [ ] **A11Y09**: Contraste texto/fundo >= 4.5:1
- [ ] **A11Y10**: Texto legível em 200% zoom
- [ ] **A11Y11**: Cores não são único indicador
- [ ] **A11Y12**: Focus é sempre visível

## 📊 Testes de Dados

### Persistência
- [ ] **DATA01**: Respostas são salvas no DB
- [ ] **DATA02**: Respostas sobrevivem a reload
- [ ] **DATA03**: CSV reflete dados do DB
- [ ] **DATA04**: Edições atualizam DB corretamente

### Formato JSON
- [ ] **DATA05**: Config JSON é válido
- [ ] **DATA06**: Payload JSON é válido
- [ ] **DATA07**: Estrutura items é correta
- [ ] **DATA08**: Estrutura respostas é correta

### Migração e Compatibilidade
- [ ] **DATA09**: Dinâmicas antigas não quebram
- [ ] **DATA10**: Novo tipo não afeta outros tipos
- [ ] **DATA11**: CSV format é consistente
- [ ] **DATA12**: Admin view funciona para todos tipos

## 🐛 Testes de Edge Cases

### Casos Extremos
- [ ] **EDGE01**: Dinâmica com 0 caracteres em moral (após trim)
- [ ] **EDGE02**: Frase com emojis e caracteres especiais
- [ ] **EDGE03**: URL de foto inválida (404)
- [ ] **EDGE04**: URL de foto muito lenta (timeout)
- [ ] **EDGE05**: Usuário deleta conta após responder
- [ ] **EDGE06**: Admin deleta dinâmica enquanto usuário responde
- [ ] **EDGE07**: Navegação de volta no browser durante quiz
- [ ] **EDGE08**: Refresh durante submit
- [ ] **EDGE09**: Múltiplos submits (double click)
- [ ] **EDGE10**: Browser sem JavaScript

## 📝 Checklist de Deploy

### Pré-Deploy
- [ ] **DEPLOY01**: Todas migrações foram aplicadas
- [ ] **DEPLOY02**: Variáveis de ambiente configuradas
- [ ] **DEPLOY03**: Testes passam em staging
- [ ] **DEPLOY04**: Documentação atualizada
- [ ] **DEPLOY05**: Changelog atualizado

### Deploy
- [ ] **DEPLOY06**: Deploy sem erros
- [ ] **DEPLOY07**: Health check passa
- [ ] **DEPLOY08**: Logs não mostram erros
- [ ] **DEPLOY09**: Smoke test em produção

### Pós-Deploy
- [ ] **DEPLOY10**: Monitorar primeiros 30 min
- [ ] **DEPLOY11**: Verificar métricas (se disponíveis)
- [ ] **DEPLOY12**: Testar fluxo completo em prod
- [ ] **DEPLOY13**: Notificar stakeholders
- [ ] **DEPLOY14**: Documentar issues encontrados

## 📋 Registro de Testes

### Template de Teste
```
Teste ID: ________
Data: ________
Testador: ________
Ambiente: [ ] Dev [ ] Staging [ ] Prod
Browser: ________
Resultado: [ ] Pass [ ] Fail
Notas: ________________________________
```

### Issues Encontrados
```
Issue #1:
- Descrição: 
- Severidade: [ ] Crítico [ ] Alto [ ] Médio [ ] Baixo
- Steps to reproduce:
- Expected:
- Actual:
- Screenshot:
```

---

## 🎯 Critérios de Aceitação

### Must Have (Bloqueadores)
- ✅ Admin pode criar dinâmica quemsoeu
- ✅ Usuário pode responder passo a passo
- ✅ Moral é exibida ao final
- ✅ Admin vê respostas
- ✅ CSV exporta corretamente

### Should Have (Importantes)
- ✅ Edição funciona
- ✅ Navegação Anterior/Próximo
- ✅ Validações impedem dados inválidos
- ✅ Mobile responsivo
- ✅ CSRF protection

### Nice to Have (Opcionais)
- ⬜ Analytics de respostas
- ⬜ Compartilhamento social
- ⬜ Gamificação/pontos
- ⬜ Upload direto de imagens
- ⬜ Preview antes de publicar

---

**Versão do Checklist**: 1.0  
**Última atualização**: Outubro 2025  
**Responsável**: Time de Desenvolvimento
