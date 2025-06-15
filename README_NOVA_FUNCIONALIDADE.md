# Nova Funcionalidade: Sinalização Manual de Discrepâncias

## Resumo

Foi implementada uma nova funcionalidade que permite aos utilizadores sinalizar manualmente anotações como discrepantes na seção dataset. Esta funcionalidade complementa o sistema automático de detecção de discrepâncias existente.

## Funcionalidades Implementadas

### 1. Novo Botão "Sinalizar" na Lista de Documentos

- **Localização**: Coluna de ações na tabela de documentos do dataset
- **Aparência**: Botão laranja com ícone de bandeira
- **Funcionalidade**: Abre um modal para análise manual de discrepâncias

### 2. Modal de Análise de Percentagens

O modal apresenta:

#### Seção de Informações do Exemplo
- Texto completo do exemplo selecionado
- Fácil identificação do conteúdo a ser analisado

#### Seção de Percentagens de Labels
- Visualização das percentagens de cada label para o exemplo específico
- Barras de progresso coloridas (vermelho < threshold, amarelo < 90%, verde ≥ 90%)
- Percentagens exibidas tanto em números como em chips coloridos

#### Análise Automática
- Comparação com o threshold do projeto (configurável)
- Indicação visual se há possível discrepância detectada automaticamente
- Percentagem de concordância máxima destacada

#### Estado Atual da Sinalização
- Mostra se o exemplo já foi sinalizado anteriormente
- Exibe quando foi feita a sinalização
- Apresenta observações anteriores se existirem
- Indica visualmente o estado atual (discrepante/consistente)
- Alerta automático se a base de dados não estiver disponível

#### Decisão Manual
- Radio buttons para classificar como "Discrepante" ou "Consistente"  
- Pré-preenchimento automático se há estado anterior
- Campo de observações para adicionar notas explicativas
- Interface adaptativa: "Nova Sinalização" vs "Alterar Sinalização"
- Validação para garantir que uma decisão seja tomada

## Arquivos Criados/Modificados

### Novos Arquivos
- `frontend/components/example/PercentageModal.vue` - Modal principal da funcionalidade

### Arquivos Modificados
- `frontend/components/example/DocumentList.vue` - Adicionado botão "Sinalizar"
- `frontend/pages/projects/_id/dataset/index.vue` - Integração do modal

## Integração com Sistema Existente

### APIs Utilizadas
- `$repositories.metrics.fetchCategoryPercentage()` - Para projetos de categorização
- `$repositories.metrics.fetchSpanPercentage()` - Para projetos de spans
- `$repositories.metrics.fetchRelationPercentage()` - Para projetos de relações

### Dados Utilizados
- Threshold de discrepância do projeto (`project.minPercentage`)
- Percentagens de labels por exemplo específico
- Informações do utilizador logado

## Fluxo de Utilização

1. **Acesso**: O utilizador navega para a seção Dataset do projeto
2. **Seleção**: Clica no botão "Sinalizar" de um exemplo específico
3. **Análise**: O modal abre mostrando:
   - Texto do exemplo
   - Estado atual da sinalização (se existir)
   - Percentagens de cada label
   - Análise automática (se há discrepância detectada)
4. **Decisão**: O utilizador pode:
   - Ver a sinalização anterior (se existir)
   - Manter ou alterar a classificação existente
   - Escolher entre "Discrepante" ou "Consistente"
5. **Observações**: Opcionalmente adiciona observações explicativas
6. **Confirmação**: Clica em "Guardar Decisão"
7. **Feedback**: Recebe confirmação da ação realizada

## Benefícios

### Para os Utilizadores
- **Controlo Manual**: Permite decisões humanas sobre discrepâncias complexas
- **Contexto Visual**: Vê as percentagens exatas antes de decidir
- **Flexibilidade**: Pode marcar como discrepante mesmo se o sistema não detectou
- **Documentação**: Pode adicionar observações para futura referência

### Para o Sistema
- **Dados de Qualidade**: Melhora a qualidade dos dados de treino
- **Feedback Humano**: Incorpora conhecimento especializado
- **Auditoria**: Mantém registo das decisões manuais
- **Flexibilidade**: Complementa a detecção automática

## Considerações Técnicas

### Performance
- Carregamento assíncrono das percentagens
- Estados de loading para melhor UX
- Tratamento de erros com mensagens informativas

### Responsividade
- Modal adaptável a diferentes tamanhos de ecrã
- Interface otimizada para dispositivos móveis
- Componentes Vuetify para consistência visual

### Extensibilidade
- Estrutura preparada para futura persistência das decisões
- Eventos emitidos para integração com outros componentes
- Código modular e reutilizável
- Verificação automática da conectividade da base de dados

### Robustez
- Monitorização contínua da conectividade da base de dados
- Alertas visuais quando há problemas de conexão
- Graceful degradation quando APIs falham
- Verificação a cada 5 segundos durante o uso do modal

## Próximos Passos Sugeridos

1. **Persistência**: Implementar salvamento das decisões na base de dados
2. **Histórico**: Criar registo de decisões manuais
3. **Filtros**: Adicionar filtros para ver apenas exemplos sinalizados
4. **Relatórios**: Incluir decisões manuais nos relatórios de discrepâncias
5. **Notificações**: Sistema de notificações para revisões pendentes

## Configuração

A funcionalidade utiliza o threshold do projeto configurado em:
- **Configuração**: `project.minPercentage`
- **Padrão**: 80% se não configurado
- **Personalização**: Pode ser ajustado por projeto nas configurações

## Suporte a Tipos de Projeto

A funcionalidade suporta automaticamente:
- ✅ **Projetos de Categorização** (`canDefineCategory`)
- ✅ **Projetos de Spans** (`canDefineSpan`) 
- ✅ **Projetos de Relações** (`canDefineRelation`)

A detecção do tipo é automática baseada nas capacidades do projeto. 