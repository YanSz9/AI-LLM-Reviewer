# 🤖 Scripts de Teste Automático de Modelos AI

## 🚀 Uso Rápido

### Testar um Modelo Específico (Método Simples)
```bash
# Teste completo com uma linha:
./scripts/quick-test.sh o1-mini
./scripts/quick-test.sh gpt-4.1  
./scripts/quick-test.sh gpt-5
```

### Apenas Trocar Modelo (Sem criar PR)
```bash
# Só configura o modelo na main:
python3 scripts/switch-ai-model.py o1-mini
python3 scripts/switch-ai-model.py gpt-4.1
python3 scripts/switch-ai-model.py gpt-5
```

## 📋 Modelos Disponíveis

| Comando | Modelo Real | Descrição |
|---------|-------------|-----------|
| `o1-mini` | o1-mini | O1-Mini compacto |
| `gpt-4.1` | gpt-4-turbo | GPT-4.1 (GPT-4-Turbo) |
| `gpt-5` | gpt-4o | GPT-5 (GPT-4o mais recente) |
| `gpt-4o` | gpt-4o | GPT-4o padrão |
| `claude` | claude-3-5-sonnet | Claude 3.5 Sonnet |
| `llama` | llama-3.1-8b-instant | Llama 3.1 via Groq |

## 🔧 Como Funciona

### `quick-test.sh` (Teste Completo)
1. ✅ Configura o modelo no workflow
2. ✅ Publica na main  
3. ✅ Cria branch de teste
4. ✅ Adiciona arquivo com vulnerabilidades
5. ✅ Cria PR automaticamente
6. ✅ GitHub Actions executa o teste

### `switch-ai-model.py` (Só Configuração)
1. ✅ Atualiza workflow com novo modelo
2. ✅ Faz commit e push na main
3. ✅ Você cria PR manualmente depois

## 💡 Exemplos de Uso

### Testar O1-Mini
```bash
./scripts/quick-test.sh o1-mini
# Resultado: PR criado automaticamente com teste do O1-Mini
```

### Testar GPT-4.1
```bash  
./scripts/quick-test.sh gpt-4.1
# Resultado: PR criado automaticamente com teste do GPT-4.1
```

### Testar GPT-5
```bash
./scripts/quick-test.sh gpt-5  
# Resultado: PR criado automaticamente com teste do GPT-5
```

### Só Configurar Modelo (Sem PR)
```bash
python3 scripts/switch-ai-model.py claude
# Resultado: Workflow configurado para Claude, criar PR manualmente
```

## 📊 Análise dos Resultados

Depois de testar vários modelos:

```bash
# Gerar gráficos comparativos
cd scripts
python3 academic-analyzer.py
# Digite os números dos PRs: 31,32,33,34
```

## 🎯 Fluxo Recomendado

1. **Testar O1-Mini**: `./scripts/quick-test.sh o1-mini`
2. **Testar GPT-4.1**: `./scripts/quick-test.sh gpt-4.1`  
3. **Testar GPT-5**: `./scripts/quick-test.sh gpt-5`
4. **Aguardar reviews completarem**
5. **Gerar gráficos**: `python3 scripts/academic-analyzer.py`
6. **Usar na faculdade!** 🎓

Simples, rápido e automatizado! 🚀