"""
ORBIT - Dashboard Routes
Rotas da API do Dashboard
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.financial_engine import (
    FinancialEngine,
    calcular_liberdade_financeira
)

router = APIRouter()


# ============================================
# 📝 SCHEMAS
# ============================================

class DashboardData(BaseModel):
    """Dados completos do dashboard"""
    saldo_atual: float
    receita_mes: float
    despesa_mes: float
    divida_total: float
    score: int
    nivel: str
    liberdade: Optional[dict]
    tendencia: str  # subindo, descendo, estavel


class FreedomTimelineData(BaseModel):
    """Dados da Linha do Tempo da Liberdade"""
    data_liberdade: Optional[str]
    meses_restantes: Optional[int]
    dias_restantes: Optional[int]
    progresso_percentual: float
    juros_total_projetado: Optional[float]


class SimulacaoInput(BaseModel):
    """Input para simulação E se?"""
    tipo: str  # vender_algo, aumentar_pagamento, renda_extra
    valor: float


# ============================================
# 🚀 ENDPOINTS
# ============================================

@router.get("/{usuario_id}")
async def get_dashboard(
    usuario_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Retorna dados completos do dashboard"""
    # TODO: Buscar dados reais do banco
    
    # Dados mockados para demonstração
    divida = 5000
    pagamento = 500
    
    liberdade = calcular_liberdade_financeira(divida, pagamento, 0.05)
    
    score_data = FinancialEngine.calcular_score_interno([
        {"tipo": "receita", "valor": 3000, "categoria": "salário"},
        {"tipo": "despesa", "valor": 1500, "categoria": "moradia"},
        {"tipo": "despesa", "valor": 300, "categoria": "alimentação"},
        {"tipo": "despesa", "valor": 200, "categoria": "lazer"},
    ])
    
    return {
        "saldo_atual": 1000,
        "receita_mes": 3000,
        "despesa_mes": 2000,
        "divida_total": divida,
        "pagamento_mensal": pagamento,
        "score": score_data["score"],
        "nivel": score_data["nivel"],
        "breakdown_score": score_data["breakdown"],
        "dicas": score_data["dicas"],
        "liberdade": liberdade if liberdade["success"] else None,
        "tendencia": "subindo"
    }


@router.get("/{usuario_id}/liberdade")
async def get_linha_liberdade(
    usuario_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Retorna dados da Linha do Tempo da Liberdade"""
    # TODO: Buscar dados reais
    
    divida = 5000
    pagamento = 500
    
    resultado = calcular_liberdade_financeira(divida, pagamento, 0.05)
    
    if not resultado["success"]:
        return {
            "erro": resultado.get("error"),
            "progresso_percentual": 0
        }
    
    # Calcular progresso (assumindo dívida original de 10000)
    divida_original = 10000
    progresso = ((divida_original - divida) / divida_original) * 100
    
    return {
        "data_liberdade": resultado["data_liberdade_formatada"],
        "meses_restantes": resultado["meses_restantes"],
        "dias_restantes": resultado["dias_restantes"],
        "progresso_percentual": round(progresso, 1),
        "juros_total_projetado": resultado["juros_total"],
        "total_a_pagar": resultado["total_a_pagar"]
    }


@router.get("/{usuario_id}/score")
async def get_score(
    usuario_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Retorna Score Gamificado detalhado"""
    # TODO: Buscar histórico real
    
    historico = [
        {"tipo": "receita", "valor": 3000, "categoria": "salário"},
        {"tipo": "despesa", "valor": 1500, "categoria": "moradia"},
        {"tipo": "despesa", "valor": 300, "categoria": "alimentação"},
        {"tipo": "despesa", "valor": 200, "categoria": "lazer"},
    ]
    
    score_data = FinancialEngine.calcular_score_interno(historico)
    
    return score_data


@router.get("/{usuario_id}/pulmao")
async def get_pulmao_financeiro(
    usuario_id: UUID,
    periodo: str = "semana",
    db: AsyncSession = Depends(get_db)
):
    """Retorna dados do Pulmão Financeiro (gráfico de área)"""
    # TODO: Buscar dados reais agregados por dia
    
    # Dados mockados para 7 dias
    dados = [
        {"dia": "Seg", "receita": 0, "despesa": 150},
        {"dia": "Ter", "receita": 0, "despesa": 80},
        {"dia": "Qua", "receita": 3000, "despesa": 200},
        {"dia": "Qui", "receita": 0, "despesa": 120},
        {"dia": "Sex", "receita": 0, "despesa": 350},
        {"dia": "Sáb", "receita": 0, "despesa": 200},
        {"dia": "Dom", "receita": 0, "despesa": 100},
    ]
    
    total_receita = sum(d["receita"] for d in dados)
    total_despesa = sum(d["despesa"] for d in dados)
    
    return {
        "periodo": periodo,
        "dados": dados,
        "total_receita": total_receita,
        "total_despesa": total_despesa,
        "saldo_periodo": total_receita - total_despesa,
        "status": "verde" if total_receita >= total_despesa else "vermelho"
    }


@router.post("/{usuario_id}/simular")
async def simular_cenario(
    usuario_id: UUID,
    simulacao: SimulacaoInput,
    db: AsyncSession = Depends(get_db)
):
    """Simula cenário 'E se?'"""
    # TODO: Buscar dados reais
    
    divida_atual = Decimal("5000")
    pagamento_atual = Decimal("500")
    taxa_mensal = Decimal("0.05")
    
    resultado = FinancialEngine.simular_cenario(
        divida_atual,
        pagamento_atual,
        taxa_mensal,
        {"tipo": simulacao.tipo, "valor": simulacao.valor}
    )
    
    return resultado


@router.get("/{usuario_id}/transacoes-recentes")
async def get_transacoes_recentes(
    usuario_id: UUID,
    limite: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """Retorna transações recentes para o feed"""
    # TODO: Buscar do banco
    
    # Dados mockados
    return {
        "transacoes": [
            {
                "id": "1",
                "tipo": "despesa",
                "categoria": "alimentação",
                "valor": 45.90,
                "descricao": "iFood",
                "data": datetime.now().isoformat(),
                "icone": "🍕"
            },
            {
                "id": "2",
                "tipo": "despesa",
                "categoria": "transporte",
                "valor": 25.00,
                "descricao": "Uber",
                "data": datetime.now().isoformat(),
                "icone": "🚗"
            },
            {
                "id": "3",
                "tipo": "receita",
                "categoria": "salário",
                "valor": 3000.00,
                "descricao": "Salário",
                "data": datetime.now().isoformat(),
                "icone": "💰"
            }
        ],
        "total": 3
    }
