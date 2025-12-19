"""
ORBIT - Transaction Routes
Rotas da API de Transações
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date
from uuid import UUID
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db

router = APIRouter()


# ============================================
# 📝 SCHEMAS
# ============================================

class TransactionCreate(BaseModel):
    """Criar nova transação"""
    tipo: str  # receita, despesa
    categoria: str
    valor: float
    descricao: Optional[str] = None
    data: Optional[datetime] = None
    origem: str = "manual"


class TransactionResponse(BaseModel):
    """Resposta de transação"""
    id: UUID
    tipo: str
    categoria: str
    valor: float
    descricao: Optional[str]
    data: datetime
    origem: str
    criado_em: datetime


class TransactionSummary(BaseModel):
    """Resumo de transações"""
    periodo: str
    total_receitas: float
    total_despesas: float
    saldo: float
    por_categoria: dict


# ============================================
# 🚀 ENDPOINTS
# ============================================

@router.post("/", response_model=dict)
async def criar_transacao(
    transacao: TransactionCreate,
    db: AsyncSession = Depends(get_db)
):
    """Cria uma nova transação"""
    # TODO: Salvar no banco
    return {
        "success": True,
        "message": "Transação criada com sucesso",
        "transacao": {
            "id": "uuid-gerado",
            **transacao.dict()
        }
    }


@router.get("/", response_model=List[dict])
async def listar_transacoes(
    usuario_id: UUID,
    tipo: Optional[str] = None,
    categoria: Optional[str] = None,
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    limite: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """Lista transações com filtros"""
    # TODO: Implementar query
    return []


@router.get("/resumo/{usuario_id}")
async def resumo_transacoes(
    usuario_id: UUID,
    periodo: str = "mes",  # dia, semana, mes, ano
    db: AsyncSession = Depends(get_db)
):
    """Retorna resumo das transações"""
    # TODO: Implementar agregação
    return {
        "periodo": periodo,
        "total_receitas": 0,
        "total_despesas": 0,
        "saldo": 0,
        "por_categoria": {}
    }


@router.get("/{transacao_id}")
async def get_transacao(
    transacao_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Busca transação por ID"""
    # TODO: Implementar busca
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Transação não encontrada"
    )


@router.put("/{transacao_id}")
async def atualizar_transacao(
    transacao_id: UUID,
    transacao: TransactionCreate,
    db: AsyncSession = Depends(get_db)
):
    """Atualiza uma transação"""
    # TODO: Implementar update
    return {"success": True, "message": "Transação atualizada"}


@router.delete("/{transacao_id}")
async def deletar_transacao(
    transacao_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Deleta uma transação"""
    # TODO: Implementar delete
    return {"success": True, "message": "Transação deletada"}
