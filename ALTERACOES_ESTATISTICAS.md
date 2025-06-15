# Alterações na Interface de Estatísticas de Anotações

## Resumo

Foram implementadas duas melhorias principais na página de estatísticas (`frontend/pages/projects/_id/statistics.vue`):

1. **Automatização da exportação**
2. **Estatísticas de discrepâncias detalhadas**

## 🚀 **Funcionalidades Implementadas**

### **1. Exportação Automática**

#### **Mudanças na Interface**
- **Removido**: Botão "Exportar" que exigia clique manual
- **Adicionado**: Opção "Não exportar" como primeira opção na lista de formatos
- **Comportamento**: Exportação automática quando formato é selecionado

#### **Fluxo de Utilizador**
```
Antes:
1. Gerar estatísticas
2. Escolher formato
3. Clicar "Exportar"

Depois:
1. Gerar estatísticas  
2. Escolher formato → Exporta automaticamente
```

#### **Opções de Exportação**
- **Não exportar** (padrão)
- **PDF**
- **CSV** 
- **PDF e CSV**

### **2. Estatísticas de Discrepâncias**

#### **Nova Seção Visual**
Quando exemplos são selecionados, é gerada uma nova seção com:

- **Métricas Resumo**:
  - Total de labels com discrepância
  - Total de labels consistentes
  
- **Tabela Detalhada** com:
  - Texto do exemplo (truncado)
  - Nome da label
  - Percentagem de consenso
  - Status (Discrepante/Consistente)

#### **Lógica de Discrepâncias**
Utiliza a mesma API que a funcionalidade de sinalização:
- `fetchCategoryPercentage` para projetos de categorização
- `fetchSpanPercentage` para projetos de spans
- `fetchRelationPercentage` para projetos de relações

## 🔧 **Alterações Técnicas**

### **Arquivo Modificado**: `frontend/pages/projects/_id/statistics.vue`

#### **1. Dados (data)**
```javascript
// Novo formato padrão
exportFormat: 'none',

// Novos formatos disponíveis
exportFormats: [
  { text: 'Não exportar', value: 'none' },
  { text: 'PDF', value: 'pdf' },
  { text: 'CSV', value: 'csv' },
  { text: 'PDF e CSV', value: 'both' }
],

// Headers para tabela de discrepâncias
discrepancyHeaders: [
  { text: 'Exemplo', value: 'example', sortable: false },
  { text: 'Label', value: 'label' },
  { text: 'Percentagem', value: 'percentage' },
  { text: 'Status', value: 'discrepancy' }
]
```

#### **2. Computed Properties**
```javascript
hasDiscrepancyStatistics() {
  return this.statistics.detailedData.some(item => item.questionId === 'discrepancy')
},

discrepancyItems() {
  return this.statistics.detailedData.filter(item => item.questionId === 'discrepancy')
},

totalDiscrepantLabels() {
  // Conta labels com percentagem abaixo do threshold do projeto
},

totalConsistentLabels() {
  // Conta labels com percentagem acima do threshold do projeto
}
```

#### **3. Watchers**
```javascript
exportFormat: {
  handler(newValue) {
    // Exporta automaticamente quando formato != 'none'
    if (newValue && newValue !== 'none' && this.hasStatistics) {
      this.exportStatistics()
    }
  }
}
```

#### **4. Novos Métodos**
```javascript
async loadDiscrepancyStatistics(data) {
  // Carrega percentagens usando APIs de métricas
  // Obtém labels do projeto
  // Calcula discrepâncias baseadas no threshold
  // Adiciona dados ao array de estatísticas
}
```

## 📊 **Estrutura dos Dados de Discrepâncias**

Cada item de discrepância contém:
```javascript
{
  questionId: 'discrepancy',
  question: 'Análise de Discrepâncias',
  answer: 'NomeDaLabel: 85.5%',
  annotator: 'Sistema',
  exampleId: 123,
  example: 'Texto do exemplo...',
  label: 'NomeDaLabel',
  percentage: 85.5,
  discrepancy: false, // true se < threshold do projeto
  date: '2024-01-15'
}
```

## 🎨 **Interface Visual**

### **Seção de Discrepâncias**
- **Card com gradiente laranja/vermelho**
- **Duas métricas destacadas** (discrepantes vs consistentes) 
- **Tabela responsiva** com:
  - Chips coloridos para status
  - Percentagens coloridas (verde/vermelho)
  - Texto truncado para exemplos longos

### **Botões Reorganizados**
- **Layout 3 colunas** em vez de 4
- **Botão "Exportar" removido**
- **Espaçamento melhorado**

## ⚡ **Melhorias de UX**

### **Fluxo Simplificado**
- **Menos cliques**: Exportação em um passo
- **Feedback imediato**: Reset automático do formato
- **Prevenção de erros**: Não exporta se formato for "none"

### **Informações Mais Ricas**
- **Visão quantitativa** das discrepâncias
- **Dados contextualizados** por exemplo
- **Status visual claro** (chips coloridos)

### **Integração Consistente**
- **Usa APIs existentes** (métricas de percentagem)
- **Segue padrões visuais** do projeto
- **Compatível com todos os tipos** de projeto

## 🔄 **Compatibilidade**

### **Tipos de Projeto Suportados**
- ✅ **Categorização** (`canDefineCategory`)
- ✅ **Spans** (`canDefineSpan`) 
- ✅ **Relações** (`canDefineRelation`)

### **Funcionalidades Mantidas**
- ✅ **Gráficos de perspectivas** (quando perguntas selecionadas)
- ✅ **Gráficos de discrepâncias visuais** (quando exemplos selecionados)
- ✅ **Filtros existentes** (perguntas, anotadores, exemplos)
- ✅ **Exportação PDF/CSV** (funcionalidade melhorada)

## 📈 **Vantagens**

### **Para Utilizadores**
- **Workflow mais rápido** (exportação automática)
- **Dados mais detalhados** (estatísticas de discrepâncias)
- **Interface mais limpa** (menos botões)

### **Para Administradores**
- **Análise quantitativa** das discrepâncias
- **Identificação rápida** de problemas de consenso
- **Exportação facilitada** dos dados

### **Para o Sistema**
- **Reutilização de código** (APIs existentes)
- **Código mais limpo** (menos lógica manual)
- **Melhor performance** (carregamento inteligente)

## 🚨 **Considerações**

### **Limitações**
- **Requer exemplos selecionados** para estatísticas de discrepâncias
- **Depende das APIs de métricas** funcionarem corretamente
- **Reset automático** do formato pode confundir alguns utilizadores

### **Pontos de Atenção**
- **Verificar performance** com muitos exemplos selecionados
- **Monitorizar uso** da exportação automática
- **Considerar feedback** dos utilizadores sobre o novo fluxo 