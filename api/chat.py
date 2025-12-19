"""
ORBIT - Chat Routes
Rotas da API de Chat (Core da aplicação)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.ai_service import ai_service, get_ai_response
from app.services.financial_engine import (
    FinancialEngine, 
    analisar_transacao_para_ia,
    calcular_liberdade_financeira
)

router = APIRouter()


# ============================================
# 📝 SCHEMAS
# ============================================

class ChatMessageInput(BaseModel):
    """Input de mensagem do chat"""
    mensagem: str
    usuario_id: Optional[UUID] = None
    contexto: Optional[dict] = None


class ChatMessageResponse(BaseModel):
    """Resposta do chat"""
    resposta: str
    tipo_detectado: Optional[str] = None  # receita, despesa, conversa
    transacao: Optional[dict] = None
    impacto: Optional[dict] = None
    timestamp: datetime
    provider: str


class TransacaoDetectada(BaseModel):
    """Transação detectada pela IA"""
    tipo: str
    categoria: str
    valor: Optional[float]
    descricao: str


class ContextoFinanceiro(BaseModel):
    """Contexto financeiro para a IA"""
    saldo_atual: float = 0
    divida_total: float = 0
    pagamento_mensal: float = 0


# ============================================
# 🚀 ENDPOINTS
# ============================================

@router.post("/enviar", response_model=ChatMessageResponse)
async def enviar_mensagem(
    input: ChatMessageInput,
    db: AsyncSession = Depends(get_db)
):
    """
    Endpoint principal do chat
    
    1. Recebe mensagem do usuário
    2. Classifica se é transação ou conversa
    3. Se transação, calcula impacto
    4. Gera resposta da IA com personalidade
    """
    # Garantir que serviço de IA está inicializado
    if not ai_service.current_provider:
        await ai_service.initialize()
    
    # Extrair contexto financeiro
    contexto = input.contexto or {}
    contexto_financeiro = {
        "saldo_atual": contexto.get("saldo_atual", 0),
        "divida_total": contexto.get("divida_total", 0),
        "pagamento_mensal": contexto.get("pagamento_mensal", 0)
    }
    
    # Classificar a mensagem
    classificacao = await ai_service.classificar_transacao(input.mensagem)
    
    transacao = None
    impacto = None
    
    # Se for uma transação
    if classificacao["tipo"] in ["receita", "despesa"] and classificacao.get("valor"):
        transacao = classificacao
        
        # Calcular impacto se for despesa e tiver dívida
        if (classificacao["tipo"] == "despesa" and 
            contexto_financeiro["divida_total"] > 0 and
            contexto_financeiro["pagamento_mensal"] > 0):
            
            try:
                from decimal import Decimal
                impacto = FinancialEngine.calcular_impacto_gasto(
                    Decimal(str(contexto_financeiro["divida_total"])),
                    Decimal(str(contexto_financeiro["pagamento_mensal"])),
                    Decimal("0.05"),  # 5% a.m. padrão
                    Decimal(str(classificacao["valor"]))
                )
                contexto_financeiro["impacto"] = impacto
            except Exception as e:
                print(f"Erro ao calcular impacto: {e}")
    
    # Gerar resposta da IA
    resultado_ia = await ai_service.processar_mensagem(
        input.mensagem,
        contexto_financeiro
    )
    
    return ChatMessageResponse(
        resposta=resultado_ia["resposta"],
        tipo_detectado=classificacao["tipo"],
        transacao=transacao,
        impacto=impacto,
        timestamp=datetime.now(),
        provider=resultado_ia["provider"]
    )


@router.post("/classificar")
async def classificar_mensagem(input: ChatMessageInput):
    """
    Classifica uma mensagem sem gerar resposta
    Útil para preview de transações
    """
    if not ai_service.current_provider:
        await ai_service.initialize()
    
    classificacao = await ai_service.classificar_transacao(input.mensagem)
    return classificacao


@router.get("/status")
async def status_chat():
    """Retorna status do serviço de chat/IA"""
    if not ai_service.current_provider:
        await ai_service.initialize()
    
    return {
        "status": "online",
        "provider": ai_service.current_provider.value if ai_service.current_provider else "none",
        "disponivel": ai_service.current_provider is not None
    }


@router.post("/simular-impacto")
async def simular_impacto(
    valor_gasto: float,
    contexto: ContextoFinanceiro
):
    """
    Simula o impacto de um gasto antes de confirmar
    """
    if contexto.divida_total <= 0 or contexto.pagamento_mensal <= 0:
        return {
            "impacto": None,
            "mensagem": "Sem dívida ativa para calcular impacto"
        }
    
    try:
        from decimal import Decimal
        impacto = FinancialEngine.calcular_impacto_gasto(
            Decimal(str(contexto.divida_total)),
            Decimal(str(contexto.pagamento_mensal)),
            Decimal("0.05"),
            Decimal(str(valor_gasto))
        )
        return {
            "impacto": impacto,
            "mensagem": impacto.get("mensagem_coach")
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/historico/{usuario_id}")
async def get_historico(
    usuario_id: UUID,
    limite: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """
    Retorna histórico de mensagens do chat
    """
    # TODO: Implementar query no banco
    return {
        "usuario_id": usuario_id,
        "mensagens": [],
        "total": 0
    }
