#!/usr/bin/env python3
"""
Script para trocar automaticamente o modelo de AI e publicar na main
Uso: python3 switch-ai-model.py <modelo>

Modelos disponíveis:
- o1-mini
- gpt-4.1 (gpt-4-turbo)
- gpt-5 (gpt-4o mais recente)
- gpt-4o
- gpt-4-turbo
- o1-preview
- claude-3-5-sonnet
- llama-3.1-8b
"""

import sys
import os
import subprocess
from datetime import datetime

# Configurações dos modelos disponíveis
MODELS_CONFIG = {
    "o1-mini": {
        "provider": "openai",
        "model": "o1-mini",
        "max_tokens": 3000,
        "temperature": 0.1,
        "description": "O1-Mini - Modelo de raciocínio compacto"
    },
    "gpt-4.1": {
        "provider": "openai", 
        "model": "gpt-4-turbo",
        "max_tokens": 4000,
        "temperature": 0.2,
        "description": "GPT-4.1 (GPT-4-Turbo) - Versão otimizada"
    },
    "gpt-5": {
        "provider": "openai",
        "model": "gpt-4o",
        "max_tokens": 4000,
        "temperature": 0.15,
        "description": "GPT-5 (GPT-4o mais recente) - Última versão"
    },
    "gpt-4o": {
        "provider": "openai",
        "model": "gpt-4o", 
        "max_tokens": 3000,
        "temperature": 0.2,
        "description": "GPT-4o - Modelo otimizado padrão"
    },
    "gpt-4-turbo": {
        "provider": "openai",
        "model": "gpt-4-turbo",
        "max_tokens": 3000,
        "temperature": 0.2,
        "description": "GPT-4-Turbo - Versão turbo"
    },
    "o1-preview": {
        "provider": "openai",
        "model": "o1-preview",
        "max_tokens": 3000,
        "temperature": 0.1,
        "description": "O1-Preview - Modelo de raciocínio avançado"
    },
    "claude": {
        "provider": "anthropic",
        "model": "claude-3-5-sonnet-20241022",
        "max_tokens": 3000,
        "temperature": 0.3,
        "description": "Claude 3.5 Sonnet - Modelo da Anthropic"
    },
    "llama": {
        "provider": "groq",
        "model": "llama-3.1-8b-instant",
        "max_tokens": 2000,
        "temperature": 0.3,
        "description": "Llama 3.1 8B - Via Groq"
    }
}

def run_command(command, description=""):
    """Executa comando e retorna resultado"""
    if description:
        print(f"🔧 {description}...")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd="/home/yan/projects/AI-TCC")
        if result.returncode == 0:
            print(f"✅ Sucesso: {description}")
            return True, result.stdout.strip()
        else:
            print(f"❌ Erro: {description}")
            print(f"   {result.stderr.strip()}")
            return False, result.stderr.strip()
    except Exception as e:
        print(f"❌ Exceção: {e}")
        return False, str(e)

def update_workflow_file(model_key):
    """Atualiza o arquivo de workflow com o novo modelo"""
    config = MODELS_CONFIG[model_key]
    workflow_path = "/home/yan/projects/AI-TCC/.github/workflows/ai-pr-review.yml"
    
    # Lê o arquivo atual
    with open(workflow_path, 'r') as f:
        content = f.read()
    
    # Substitui as configurações do modelo
    lines = content.split('\n')
    new_lines = []
    
    for line in lines:
        if 'provider:' in line and '# Options:' in line:
            new_lines.append(f'          provider: "{config["provider"]}"              # Modelo atual: {config["description"]}')
        elif 'model:' in line and 'OpenAI:' in line:
            new_lines.append(f'          model: "{config["model"]}"                 # {model_key.upper()} configurado automaticamente')
        elif 'max-tokens:' in line and '# Token limit' in line:
            new_lines.append(f'          max-tokens: {config["max_tokens"]}                # Token limit otimizado para {model_key}')
        elif 'temperature:' in line and '# Creativity' in line:
            new_lines.append(f'          temperature: {config["temperature"]}                # Temperatura otimizada para {model_key}')
        else:
            new_lines.append(line)
    
    # Escreve o arquivo atualizado
    with open(workflow_path, 'w') as f:
        f.write('\n'.join(new_lines))
    
    print(f"✅ Workflow atualizado para {config['description']}")

def main():
    if len(sys.argv) != 2:
        print("🤖 Script de Troca Automática de Modelo AI")
        print("=" * 50)
        print("Uso: python3 switch-ai-model.py <modelo>")
        print("\n📋 Modelos disponíveis:")
        for key, config in MODELS_CONFIG.items():
            print(f"  • {key:15} - {config['description']}")
        print(f"\n💡 Exemplo: python3 switch-ai-model.py o1-mini")
        sys.exit(1)
    
    model_key = sys.argv[1].lower()
    
    if model_key not in MODELS_CONFIG:
        print(f"❌ Modelo '{model_key}' não encontrado!")
        print("📋 Modelos disponíveis:")
        for key in MODELS_CONFIG.keys():
            print(f"  • {key}")
        sys.exit(1)
    
    config = MODELS_CONFIG[model_key]
    print(f"🚀 Configurando {config['description']}...")
    print("=" * 60)
    
    # 1. Garantir que estamos na main
    success, _ = run_command("git checkout main", "Mudando para branch main")
    if not success:
        sys.exit(1)
    
    # 2. Puxar últimas mudanças
    success, _ = run_command("git pull origin main", "Atualizando branch main")
    if not success:
        sys.exit(1)
    
    # 3. Atualizar arquivo de workflow
    try:
        update_workflow_file(model_key)
    except Exception as e:
        print(f"❌ Erro ao atualizar workflow: {e}")
        sys.exit(1)
    
    # 4. Adicionar mudanças
    success, _ = run_command("git add .github/workflows/ai-pr-review.yml", "Adicionando arquivo de workflow")
    if not success:
        sys.exit(1)
    
    # 5. Fazer commit
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    commit_msg = f"Configure AI workflow for {config['description']} - {timestamp}"
    success, _ = run_command(f'git commit -m "{commit_msg}"', "Fazendo commit das mudanças")
    if not success:
        print("⚠️  Nenhuma mudança para commit (modelo já pode estar configurado)")
    
    # 6. Publicar na main
    success, _ = run_command("git push origin main", "Publicando mudanças na main")
    if not success:
        sys.exit(1)
    
    print(f"\n🎉 CONFIGURAÇÃO COMPLETA!")
    print("=" * 40)
    print(f"✅ Modelo: {config['description']}")
    print(f"✅ Provider: {config['provider']}")
    print(f"✅ Model ID: {config['model']}")
    print(f"✅ Max Tokens: {config['max_tokens']}")
    print(f"✅ Temperature: {config['temperature']}")
    print(f"✅ Publicado na main")
    print("\n💡 Agora você pode criar um PR para testar o modelo!")
    print("💡 O workflow será executado automaticamente com as novas configurações.")

if __name__ == "__main__":
    main()