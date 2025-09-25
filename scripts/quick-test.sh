#!/bin/bash
# Script auxiliar para testar modelos rapidamente
# Uso: ./quick-test.sh <modelo>

cd /home/yan/projects/AI-TCC

echo "🚀 Teste Rápido de Modelo AI"
echo "=========================="

if [ $# -eq 0 ]; then
    echo "💡 Uso: ./quick-test.sh <modelo>"
    echo "📋 Modelos disponíveis:"
    echo "  • o1-mini     - O1-Mini compacto"
    echo "  • gpt-4.1     - GPT-4.1 (GPT-4-Turbo)"
    echo "  • gpt-5       - GPT-5 (GPT-4o mais recente)"
    echo "  • gpt-4o      - GPT-4o padrão"
    echo "  • claude      - Claude 3.5 Sonnet"
    echo "  • llama       - Llama 3.1 via Groq"
    exit 1
fi

MODEL=$1

# 1. Configurar o modelo
echo "🔧 Configurando modelo: $MODEL"
python3 scripts/switch-ai-model.py $MODEL

if [ $? -ne 0 ]; then
    echo "❌ Falha ao configurar modelo"
    exit 1
fi

# 2. Criar branch de teste
BRANCH_NAME="test-$MODEL-$(date +%Y%m%d-%H%M%S)"
echo "🌿 Criando branch de teste: $BRANCH_NAME"
git checkout -b $BRANCH_NAME

# 3. Adicionar arquivo de teste (usando um dos arquivos existentes)
echo "📝 Adicionando arquivo de teste..."
cp src/user-service.ts src/test-$MODEL.ts

# Adicionar cabeçalho de teste
cat > src/test-$MODEL.ts << EOF
// Teste do modelo AI: $MODEL
// Data: $(date)
// Este arquivo contém vulnerabilidades intencionais para teste

// VULNERABILIDADE 1: SQL Injection
const query = \`SELECT * FROM users WHERE id = \${userId}\`;

// VULNERABILIDADE 2: XSS
document.innerHTML = userInput;

// VULNERABILIDADE 3: Hardcoded Secret
const API_KEY = "sk-1234567890abcdef";

// VULNERABILIDADE 4: Path Traversal
const filePath = \`./uploads/\${fileName}\`;

// VULNERABILIDADE 5: Command Injection
exec(\`tar -czf backup_\${filename}.tar.gz /data/\`);

// Função com vulnerabilidades múltiplas para testar o modelo $MODEL
function vulnerableFunction(userInput: string) {
    // Sem validação de input
    eval(userInput); // Dangerous!
    
    // SQL injection direto  
    db.query(\`SELECT * FROM users WHERE name = '\${userInput}'\`);
    
    // XSS vulnerability
    return \`<div>Hello \${userInput}</div>\`;
}

export default vulnerableFunction;
EOF

# 4. Fazer commit e push
git add .
git commit -m "Teste do modelo $MODEL com vulnerabilidades intencionais"
git push origin $BRANCH_NAME

# 5. Criar PR automaticamente
echo "📋 Criando PR para teste..."
gh pr create \
    --title "🤖 Teste AI: $MODEL" \
    --body "## Teste do Modelo $MODEL

**Data:** $(date)
**Branch:** $BRANCH_NAME

### Objetivos
- Testar capacidade de detecção de vulnerabilidades
- Avaliar qualidade dos comentários
- Comparar com outros modelos

### Vulnerabilidades Incluídas
- SQL Injection
- Cross-Site Scripting (XSS)  
- Hardcoded Secrets
- Path Traversal
- Command Injection
- Eval() usage

**Modelo será testado automaticamente pelo GitHub Actions!**
" \
    --base main \
    --head $BRANCH_NAME

echo ""
echo "🎉 TESTE CONFIGURADO COM SUCESSO!"
echo "================================="
echo "✅ Modelo: $MODEL configurado"
echo "✅ Branch: $BRANCH_NAME criada"
echo "✅ PR criado automaticamente"
echo "✅ GitHub Actions executará em breve"
echo ""
echo "💡 Monitore o PR para ver os comentários do modelo $MODEL!"