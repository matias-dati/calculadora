# 💰 AWS Cost Calculator - Interface Moderna

Uma aplicação Streamlit moderna e intuitiva para processar arquivos CSV da Calculadora AWS e gerar resumos formatados de custos.

## ✨ Principais Melhorias

### 🎨 Interface Visual
- **Design moderno** com cores AWS (laranja e azul escuro)
- **Layout responsivo** com sidebar organizada
- **Cards informativos** para métricas principais
- **Gráficos interativos** com Plotly
- **Animações** e feedback visual

### 📊 Funcionalidades Aprimoradas
- **Dashboard de métricas** (cliente, conta, regiões, serviços)
- **Gráfico de pizza** para distribuição de custos
- **Resumo financeiro visual** separado por tipo de pagamento
- **Visualização por região** expansível
- **Área de debug** para desenvolvedores

### 🚀 Experiência do Usuário
- **Feedback em tempo real** durante processamento
- **Mensagens de erro** mais claras e úteis
- **Tooltips informativos** em todos os campos
- **Botões de ação** destacados
- **Organização intuitiva** do conteúdo

## 📁 Estrutura de Arquivos

```
Front calculadora/
├── app_modern.py          # Nova aplicação moderna
├── app (1) (1).py        # Aplicação original
├── requirements.txt       # Dependências atualizadas
├── .streamlit/
│   └── config.toml       # Configurações de tema
└── README_MODERN.md      # Esta documentação
```

## 🛠️ Instalação

1. **Instalar dependências:**
```bash
pip install -r requirements.txt
```

2. **Executar aplicação moderna:**
```bash
streamlit run app_modern.py
```

## 🎯 Como Usar

### 1. Configurações (Sidebar)
- **Taxa de câmbio**: Ajuste USD → BRL
- **Taxa de imposto**: Configure percentual (padrão 13,83%)
- **Formas de pagamento**: Escolha para Lambda e Fargate

### 2. Upload do Arquivo
- Arraste ou selecione arquivo CSV da Calculadora AWS
- Processamento automático com feedback visual
- Validação de formato em tempo real

### 3. Visualização dos Resultados
- **Métricas principais**: Cliente, conta, regiões, serviços
- **Gráfico de custos**: Distribuição por serviço
- **Resumo financeiro**: No Upfront vs All Upfront
- **Resumo detalhado**: Texto formatado para download

### 4. Análise Detalhada
- **Por região**: Expandir para ver detalhes
- **Por serviço**: Tabelas organizadas
- **Debug**: Dados brutos em JSON

## 🎨 Personalização Visual

### Cores AWS
- **Primária**: #FF9900 (Laranja AWS)
- **Secundária**: #232F3E (Azul escuro AWS)
- **Fundo**: #FFFFFF (Branco)
- **Cards**: #F8F9FA (Cinza claro)

### Componentes Customizados
- **Header gradiente** com logo conceitual
- **Cards de métricas** com bordas coloridas
- **Área de upload** estilizada
- **Banners de sucesso/erro** destacados

## 📈 Funcionalidades Técnicas

### Processamento de Dados
- Mantém toda lógica original de cálculos
- Adiciona métricas agregadas para visualização
- Otimiza estrutura de dados para gráficos

### Visualizações
- **Plotly** para gráficos interativos
- **Métricas Streamlit** para KPIs
- **DataFrames** para tabelas detalhadas
- **Expansores** para organização de conteúdo

### Performance
- **Spinner** durante processamento
- **Cache** de configurações
- **Lazy loading** de componentes pesados

## 🔧 Configurações Avançadas

### Tema Personalizado (.streamlit/config.toml)
```toml
[theme]
primaryColor = "#FF9900"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
```

### Upload de Arquivos
- Limite: 200MB
- Formatos: CSV (UTF-8)
- Validação automática de estrutura

## 🚀 Próximos Passos

### Melhorias Futuras
- [ ] Histórico de processamentos
- [ ] Comparação entre cenários
- [ ] Exportação para Excel/PDF
- [ ] API REST para integração
- [ ] Autenticação de usuários
- [ ] Dashboard administrativo

### Otimizações
- [ ] Cache de resultados
- [ ] Processamento assíncrono
- [ ] Compressão de dados
- [ ] Logs detalhados

## 🤝 Contribuição

Para melhorar a aplicação:
1. Teste a nova interface
2. Reporte bugs ou sugestões
3. Proponha novas funcionalidades
4. Contribua com código

## 📞 Suporte

- **Interface moderna**: `app_modern.py`
- **Interface original**: `app (1) (1).py`
- **Configurações**: `.streamlit/config.toml`
- **Dependências**: `requirements.txt`