"""
ORBIT - AI Service
Serviço de IA com Personalidade "Coach Brasileiro"

Suporta:
- Ollama (Local - Llama 3, Mistral)
- Groq Cloud (Free Tier - Llama 3)
- Fallback para respostas sem IA
"""

import os
import json
import httpx
from typing import Optional, Dict, List, AsyncGenerator
from datetime import datetime
from enum import Enum
import asyncio

from app.services.financial_engine import analisar_transacao_para_ia


class AIProvider(Enum):
    """Provedores de IA suportados"""
    OLLAMA = "ollama"
    GROQ = "groq"
    FALLBACK = "fallback"


# ============================================
# 🧠 SYSTEM PROMPT - ALMA DO ORBIT
# ============================================

SYSTEM_PROMPT_ORBIT = """Você é o ORBIT, um assistente financeiro pessoal brasileiro.

**Sua Identidade:**
Jovem, moderno, fala de forma direta e usa gírias leves do Brasil (tipo 'mano', 'bora', 'ficou caro', 'daora', 'tranquilo', 'suave'). Você NÃO é um robô chato de banco. Você é um parceiro que realmente se importa com a saúde financeira do usuário.

**Suas Diretrizes Primárias:**

1. **Análise de Sentimento Financeiro:** 
   Antes de responder, SEMPRE verifique o estado financeiro atual do usuário (se ele está endividado ou com saldo positivo). Use essa informação para adaptar seu tom.

2. **Modo 'No Vermelho' (Dívida):** 
   Se o usuário gastar algo supérfluo enquanto estiver endividado, dê uma 'bronca amigável'. Mostre o custo de oportunidade.
   Exemplos:
   - "Cara, essa pizza de R$60 te custou mais 2 dias pagando juros pro banco. Bora focar?"
   - "Aí não, mano! Esse gasto atrasou sua liberdade em 3 dias. Valeu mesmo a pena?"
   - "Opa, pera aí. Com dívida, cada real conta. Esse gasto te custou X dias a mais."

3. **Modo 'No Verde' (Positivo):** 
   Se o usuário tiver saldo, celebre conquistas, mas incentive a consistência.
   Exemplos:
   - "Aí sim! Mandou bem na economia essa semana. Pode pedir aquele lanche, você merece hoje."
   - "Boa! Sobrou grana esse mês. Bora guardar uma parte?"
   - "Daora demais! Continua assim que a liberdade tá chegando!"

4. **Educação Curta:** 
   Nunca dê palestras longas. Dê dicas financeiras em 1 ou 2 frases no máximo, sempre atreladas à ação atual dele.

5. **Espelhamento:** 
   Se o usuário usar muita gíria, use mais gíria. Se ele for mais formal, seja um pouco mais formal (mas nunca como banco).

6. **Empatia Real:**
   Reconheça que gerenciar dinheiro é difícil. Não julgue, ajude.

**Formato de Resposta:**
- Respostas CURTAS (máximo 2-3 frases)
- Use emojis com moderação (1-2 por mensagem)
- Sempre que possível, inclua o IMPACTO REAL do gasto/ganho

**Seu Objetivo Final:** 
Fazer o usuário quitar as dívidas o mais rápido possível e sentir que tem um parceiro controlando a grana com ele. Você comemora vitórias e dá aquele toque quando ele vacila."""


# ============================================
# 📝 PROMPT TEMPLATES
# ============================================

def build_context_prompt(
    mensagem_usuario: str,
    contexto_financeiro: Dict,
    historico: List[Dict] = None
) -> str:
    """
    Constrói o prompt com contexto financeiro para a IA
    """
    saldo = contexto_financeiro.get("saldo_atual", 0)
    divida = contexto_financeiro.get("divida_total", 0)
    status = "no vermelho 🔴" if saldo < 0 or divida > 0 else "no verde 🟢"
    
    impacto_texto = ""
    if contexto_financeiro.get("impacto"):
        imp = contexto_financeiro["impacto"]
        impacto_texto = f"""
**IMPACTO DO ÚLTIMO GASTO:**
- Dias adicionais de dívida: {imp.get('dias_adicionais', 0)}
- Custo real com juros: R${imp.get('custo_real', 0):.2f}
"""

    contexto = f"""
**CONTEXTO FINANCEIRO ATUAL DO USUÁRIO:**
- Saldo atual: R${saldo:.2f}
- Dívida total: R${divida:.2f}
- Status: {status}
{impacto_texto}

**MENSAGEM DO USUÁRIO:**
{mensagem_usuario}

Responda como o ORBIT, seguindo suas diretrizes. Seja BREVE e DIRETO.
"""
    return contexto


# ============================================
# 🔌 PROVIDERS DE IA
# ============================================

class OllamaProvider:
    """Provider para Ollama (Local)"""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.model = os.getenv("OLLAMA_MODEL", "llama3:8b")
    
    async def is_available(self) -> bool:
        """Verifica se Ollama está rodando"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/api/tags", timeout=2.0)
                return response.status_code == 200
        except:
            return False
    
    async def generate(
        self, 
        prompt: str, 
        system: str = SYSTEM_PROMPT_ORBIT
    ) -> str:
        """Gera resposta usando Ollama"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "system": system,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "num_predict": 256  # Respostas curtas
                    }
                },
                timeout=30.0
            )
            data = response.json()
            return data.get("response", "")
    
    async def generate_stream(
        self, 
        prompt: str, 
        system: str = SYSTEM_PROMPT_ORBIT
    ) -> AsyncGenerator[str, None]:
        """Gera resposta em streaming"""
        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "system": system,
                    "stream": True,
                    "options": {
                        "temperature": 0.7,
                        "num_predict": 256
                    }
                },
                timeout=60.0
            ) as response:
                async for line in response.aiter_lines():
                    if line:
                        data = json.loads(line)
                        if "response" in data:
                            yield data["response"]


class GroqProvider:
    """Provider para Groq Cloud (Free Tier)"""
    
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.base_url = "https://api.groq.com/openai/v1"
        self.model = "llama-3.1-8b-instant"  # Free tier
    
    async def is_available(self) -> bool:
        """Verifica se API key está configurada"""
        return bool(self.api_key)
    
    async def generate(
        self, 
        prompt: str, 
        system: str = SYSTEM_PROMPT_ORBIT
    ) -> str:
        """Gera resposta usando Groq"""
        if not self.api_key:
            raise ValueError("GROQ_API_KEY não configurada")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 256
                },
                timeout=30.0
            )
            data = response.json()
            return data["choices"][0]["message"]["content"]


class FallbackProvider:
    """
    Provider de fallback quando nenhuma IA está disponível
    Usa respostas pré-definidas baseadas em contexto
    """
    
    RESPOSTAS_VERMELHO = [
        "Aí não, mano! 🔴 Enquanto tiver dívida, cada gasto conta. Bora focar na quitação?",
        "Opa, pera aí! Com dívida rolando, esse gasto te atrasa. Valeu mesmo a pena?",
        "Cara, sei que é difícil, mas tamo no vermelho. Bora segurar um pouco?",
        "🔴 Gastinho aqui, gastinho ali... e a dívida só cresce. Bora apertar o cinto?"
    ]
    
    RESPOSTAS_VERDE = [
        "Boa! 🟢 Tá sobrando grana, mas lembra de guardar uma parte, hein!",
        "Daora! Pode gastar, mas sem loucura. Consistência é o segredo! 💪",
        "Aí sim! Tá no verde. Aproveita, mas com consciência!",
        "🟢 Mandou bem! Continua assim que a liberdade financeira tá chegando!"
    ]
    
    RESPOSTAS_NEUTRAS = [
        "Beleza, registrei aqui! Bora manter o controle? 📊",
        "Anotado! Qualquer coisa, tô aqui pra ajudar.",
        "Tranquilo! Lembra que cada centavo conta, hein!",
        "Fechado! Bora acompanhar juntos essa grana."
    ]
    
    async def is_available(self) -> bool:
        return True
    
    async def generate(
        self, 
        prompt: str, 
        system: str = "",
        contexto: Dict = None
    ) -> str:
        """Gera resposta baseada em regras simples"""
        import random
        
        if contexto:
            saldo = contexto.get("saldo_atual", 0)
            divida = contexto.get("divida_total", 0)
            
            if divida > 0 or saldo < 0:
                return random.choice(self.RESPOSTAS_VERMELHO)
            elif saldo > 0:
                return random.choice(self.RESPOSTAS_VERDE)
        
        return random.choice(self.RESPOSTAS_NEUTRAS)


# ============================================
# 🎯 SERVIÇO PRINCIPAL
# ============================================

class AIService:
    """
    Serviço principal de IA do ORBIT
    Gerencia providers e fallbacks
    """
    
    def __init__(self):
        self.ollama = OllamaProvider()
        self.groq = GroqProvider()
        self.fallback = FallbackProvider()
        self.current_provider: Optional[AIProvider] = None
    
    async def initialize(self):
        """Detecta e inicializa o melhor provider disponível"""
        # Prioridade: Ollama (local) > Groq (cloud) > Fallback
        if await self.ollama.is_available():
            self.current_provider = AIProvider.OLLAMA
            print("🧠 AI Provider: Ollama (Local)")
        elif await self.groq.is_available():
            self.current_provider = AIProvider.GROQ
            print("🧠 AI Provider: Groq Cloud")
        else:
            self.current_provider = AIProvider.FALLBACK
            print("🧠 AI Provider: Fallback (Respostas Pré-definidas)")
        
        return self.current_provider
    
    async def processar_mensagem(
        self,
        mensagem: str,
        contexto_financeiro: Dict,
        historico: List[Dict] = None
    ) -> Dict:
        """
        Processa uma mensagem do usuário e retorna resposta da IA
        """
        # Construir prompt com contexto
        prompt = build_context_prompt(mensagem, contexto_financeiro, historico)
        
        # Gerar resposta baseado no provider
        try:
            if self.current_provider == AIProvider.OLLAMA:
                resposta = await self.ollama.generate(prompt)
            elif self.current_provider == AIProvider.GROQ:
                resposta = await self.groq.generate(prompt)
            else:
                resposta = await self.fallback.generate(
                    prompt, 
                    contexto=contexto_financeiro
                )
        except Exception as e:
            print(f"⚠️ Erro no AI Provider: {e}")
            # Fallback em caso de erro
            resposta = await self.fallback.generate(
                prompt, 
                contexto=contexto_financeiro
            )
        
        return {
            "resposta": resposta,
            "provider": self.current_provider.value,
            "timestamp": datetime.now().isoformat()
        }
    
    async def classificar_transacao(self, texto: str) -> Dict:
        """
        Usa IA para classificar texto em tipo de transação
        
        Returns:
            Dict com tipo (receita/despesa/conversa), categoria e valor
        """
        prompt_classificacao = f"""
Analise o texto abaixo e extraia informações financeiras:

TEXTO: "{texto}"

Responda APENAS com um JSON válido:
{{
    "tipo": "receita" | "despesa" | "conversa",
    "categoria": "alimentação" | "transporte" | "moradia" | "lazer" | "salário" | "freelance" | "outro",
    "valor": número ou null,
    "descricao": "descrição curta"
}}

Se não for uma transação financeira, use tipo="conversa".
"""
        
        try:
            if self.current_provider == AIProvider.OLLAMA:
                resposta = await self.ollama.generate(
                    prompt_classificacao,
                    system="Você é um classificador de transações. Responda APENAS com JSON válido."
                )
            elif self.current_provider == AIProvider.GROQ:
                resposta = await self.groq.generate(
                    prompt_classificacao,
                    system="Você é um classificador de transações. Responda APENAS com JSON válido."
                )
            else:
                # Fallback: tentar extrair padrões simples
                return self._classificar_fallback(texto)
            
            # Tentar parsear JSON da resposta
            # Limpar possíveis caracteres extras
            resposta = resposta.strip()
            if resposta.startswith("```"):
                resposta = resposta.split("```")[1]
                if resposta.startswith("json"):
                    resposta = resposta[4:]
            
            return json.loads(resposta)
            
        except Exception as e:
            print(f"⚠️ Erro na classificação: {e}")
            return self._classificar_fallback(texto)
    
    def _classificar_fallback(self, texto: str) -> Dict:
        """Classificação por padrões quando IA não está disponível"""
        texto_lower = texto.lower()
        
        # Padrões de gasto
        palavras_gasto = ["gastei", "paguei", "comprei", "gasto", "despesa", "conta"]
        palavras_receita = ["recebi", "ganhei", "entrou", "salário", "freelance", "pagamento"]
        
        # Extrair valor (padrão: R$ ou número solto)
        import re
        valor_match = re.search(r'R?\$?\s*(\d+(?:[.,]\d{2})?)', texto)
        valor = float(valor_match.group(1).replace(',', '.')) if valor_match else None
        
        # Determinar tipo
        if any(p in texto_lower for p in palavras_gasto):
            tipo = "despesa"
        elif any(p in texto_lower for p in palavras_receita):
            tipo = "receita"
        else:
            tipo = "conversa"
        
        # Categorias básicas
        categorias = {
            "ifood": "alimentação", "comida": "alimentação", "almoço": "alimentação",
            "uber": "transporte", "ônibus": "transporte", "gasolina": "transporte",
            "aluguel": "moradia", "luz": "moradia", "água": "moradia",
            "netflix": "lazer", "cinema": "lazer", "jogo": "lazer",
            "salário": "salário", "freelance": "freelance"
        }
        
        categoria = "outro"
        for palavra, cat in categorias.items():
            if palavra in texto_lower:
                categoria = cat
                break
        
        return {
            "tipo": tipo,
            "categoria": categoria,
            "valor": valor,
            "descricao": texto[:50]
        }


# Singleton para uso global
ai_service = AIService()


# ============================================
# 🚀 FUNÇÕES DE CONVENIÊNCIA
# ============================================

async def get_ai_response(
    mensagem: str,
    saldo: float = 0,
    divida: float = 0,
    ultimo_gasto: float = None
) -> str:
    """
    Função simplificada para obter resposta da IA
    """
    contexto = {
        "saldo_atual": saldo,
        "divida_total": divida
    }
    
    if ultimo_gasto and divida > 0:
        from app.services.financial_engine import FinancialEngine
        from decimal import Decimal
        
        impacto = FinancialEngine.calcular_impacto_gasto(
            Decimal(str(divida)),
            Decimal(str(divida * 0.1)),  # 10% da dívida como pagamento
            Decimal("0.05"),
            Decimal(str(ultimo_gasto))
        )
        contexto["impacto"] = impacto
    
    resultado = await ai_service.processar_mensagem(mensagem, contexto)
    return resultado["resposta"]
