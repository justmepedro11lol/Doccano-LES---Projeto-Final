# Correções nas Estatísticas de Anotações

## Problemas Corrigidos

### 🐛 **1. Dados de Percentagem e Status Incorretos**

**Problema:** As percentagens e status de discrepância não estavam corretos.

**Solução:** 
- Reimplementação completa usando a **mesma lógica da seção de discrepâncias**
- Uso das APIs corretas: `fetchCategoryPercentage`, `fetchSpanPercentage`, `fetchRelationPercentage`
- Carregamento dos nomes reais das labels através dos serviços `categoryType`, `spanType`, `relationType`

### 🐛 **2. Frases Sem Labels Aparecendo**

**Problema:** Frases do dataset sem anotações apareciam nas estatísticas.

**Solução:**
- **Filtro rigoroso**: Só processa exemplos que têm anotações (`percentages[exampleId]`)
- **Validação de labels**: Verifica se `labelEntries.length > 0` antes de processar
- **Dados reais**: Carrega apenas exemplos com percentagens calculadas

### 🐛 **3. Bug de Caixa Vazia nas Perspectivas**

**Problema:** Gerar estatísticas de perspectivas e discrepâncias juntas causava caixa vazia.

**Solução:**
- **Carregamento separado**: Perspectivas e discrepâncias carregadas independentemente
- **Combinação correta**: `[...perspectiveData, ...discrepancyData]`
- **Resetar estado**: Limpa dados antes de cada geração

## 🔧 **Alterações Técnicas**

### **Método `generateStatistics()` Refatorado**

```javascript
// ANTES: Carregamento único confuso
const statisticsData = await this.loadStatisticsData()

// DEPOIS: Carregamento separado e claro
let perspectiveData = []
if (this.selectedQuestions.length > 0 || this.selectedAnnotators.length > 0) {
  perspectiveData = await this.loadStatisticsData()
}

let discrepancyData = []
if (this.selectedExamples.length > 0) {
  discrepancyData = await this.loadDiscrepancyStatistics()
}

const allData = [...perspectiveData, ...discrepancyData]
```

### **Método `loadDiscrepancyStatistics()` Melhorado**

#### **1. Carregamento de Labels Correto**
```javascript
// Carregar labels do projeto para obter nomes corretos
let labelTypes = []
if (project.canDefineCategory) {
  labelTypes = await this.$services.categoryType.list(this.projectId)
}

// Criar mapa de ID para nome da label
const labelMap = {}
labelTypes.forEach(labelType => {
  labelMap[labelType.id] = labelType.text || labelType.name
})
```

#### **2. Filtro de Exemplos com Anotações**
```javascript
// Filtrar apenas os exemplos selecionados que têm anotações
const selectedPercentages = {}
for (const exampleId of this.selectedExamples) {
  if (percentages[exampleId]) {
    selectedPercentages[exampleId] = percentages[exampleId]
  }
}
```

#### **3. Cálculo Correto de Discrepâncias**
```javascript
// Encontrar a percentagem máxima para determinar se há discrepância
const maxPercentage = Math.max(...labelEntries.map(([, perc]) => perc))
const hasDiscrepancy = maxPercentage < project.minPercentage

// Para cada label individual
const isDiscrepant = percentage < project.minPercentage
```

## 🎨 **Melhorias na Interface**

### **Nova Seção: Resumo por Exemplo**
- **Cards visuais** mostrando status de cada exemplo
- **Chip colorido** (verde/vermelho) para status
- **Percentagem máxima** de consenso
- **Contagem de labels** anotadas

### **Tabela Melhorada**
- **Barras de progresso** visuais para percentagens
- **Tooltips** para textos longos dos exemplos
- **Paginação** (10 itens por página)
- **Cores consistentes** com o tema do sistema

### **Estrutura Visual**
```
┌─── Resumo de Estatísticas de Discrepâncias ───┐
│ 🔢 Labels Discrepantes: 5    Consistentes: 12 │
│                                               │
│ 📊 Resumo por Exemplo:                        │
│ ┌─────────────┐ ┌─────────────┐              │
│ │ ❌ Discrepante │ │ ✅ Consistente │              │
│ │ Max: 45.2%    │ │ Max: 87.3%     │              │
│ │ Texto exemplo │ │ Texto exemplo  │              │
│ │ 3 labels      │ │ 2 labels       │              │
│ └─────────────┘ └─────────────┘              │
│                                               │
│ 📋 Tabela Detalhada:                          │
│ Exemplo | Label | ████▓▓ 75% | ✅ Consistente │
│ ───────────────────────────────────────────   │
└───────────────────────────────────────────────┘
```

## 📊 **Dados Estruturados Corretamente**

### **Cada Item de Discrepância**
```javascript
{
  questionId: 'discrepancy',
  question: 'Análise de Discrepâncias',
  answer: 'Sentimento Positivo: 85.5%',
  annotator: 'Sistema',
  exampleId: 123,
  example: 'Texto do exemplo completo...',
  label: 'Sentimento Positivo',
  percentage: 85.5,
  discrepancy: false,
  maxPercentage: 85.5,
  hasExampleDiscrepancy: false,
  date: '2024-01-15'
}
```

### **Computed Properties Adicionadas**
- `uniqueExamples`: Agrupa dados por exemplo
- `totalDiscrepantLabels`: Conta labels discrepantes  
- `totalConsistentLabels`: Conta labels consistentes

## ✅ **Resultados**

### **Dados Corretos**
- ✅ **Percentagens reais** das APIs de métricas
- ✅ **Nomes corretos** das labels
- ✅ **Status preciso** baseado no threshold do projeto
- ✅ **Filtro eficaz** (só exemplos com anotações)

### **Interface Melhorada**  
- ✅ **Visão por exemplo** e por label
- ✅ **Barras de progresso** visuais
- ✅ **Tooltips informativos**
- ✅ **Responsividade** mantida

### **Bugs Corrigidos**
- ✅ **Carregamento separado** resolve conflito perspectivas/discrepâncias
- ✅ **Dados limpos** a cada geração
- ✅ **Validação rigorosa** de dados

## 🚀 **Como Usar**

1. **Selecionar exemplos** nos filtros
2. **Clicar "Gerar Estatísticas"**
3. **Ver resumo visual** dos exemplos
4. **Analisar tabela detalhada** das labels
5. **Exportar automaticamente** escolhendo formato

A implementação agora segue exatamente a mesma lógica da seção de discrepâncias, garantindo consistência e precisão dos dados! 