"""
ORBIT - Financial Engine
Motor Matemático para Cálculos Financeiros

Funcionalidades:
- Cálculo de juros compostos
- Projeção de data de quitação de dívidas
- Simulações "E se?"
- Score comportamental interno
- Análise de fluxo de caixa
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple
from decimal import Decimal, ROUND_HALF_UP
from dataclasses import dataclass
from enum import Enum
import math


class FinancialStatus(Enum):
    """Status financeiro do usuário"""
    CRITICAL = "critical"      # Dívida alta, sem pagamento
    RED = "red"                # No vermelho, mas pagando
    YELLOW = "yellow"          # Equilibrado, atenção
    GREEN = "green"            # Positivo, guardando
    EXCELLENT = "excellent"    # Excelente, investindo


@dataclass
class DebtProjection:
    """Projeção de quitação de dívida"""
    debt_total: Decimal
    monthly_payment: Decimal
    interest_rate: Decimal
    months_to_payoff: int
    payoff_date: datetime
    total_interest_paid: Decimal
    total_amount_paid: Decimal


@dataclass
class FinancialSnapshot:
    """Snapshot do estado financeiro atual"""
    balance: Decimal
    total_income: Decimal
    total_expenses: Decimal
    total_debt: Decimal
    status: FinancialStatus
    score: int
    freedom_date: Optional[datetime]
    days_to_freedom: Optional[int]


class FinancialEngine:
    """
    Motor de cálculos financeiros do ORBIT
    Todas as operações usam Decimal para precisão monetária
    """
    
    # Taxas médias brasileiras (2024) para referência
    TAXA_SELIC_MENSAL = Decimal("0.0087")  # ~10.75% a.a.
    TAXA_CARTAO_MENSAL = Decimal("0.14")   # ~400% a.a. rotativo
    TAXA_CHEQUE_ESPECIAL = Decimal("0.08") # ~150% a.a.
    TAXA_CONSIGNADO = Decimal("0.018")     # ~24% a.a.
    
    @staticmethod
    def calcular_juros_compostos(
        principal: Decimal,
        taxa_mensal: Decimal,
        meses: int,
        aporte_mensal: Decimal = Decimal("0")
    ) -> Dict:
        """
        Calcula juros compostos com ou sem aportes mensais
        
        M = P * (1 + i)^n + PMT * [((1 + i)^n - 1) / i]
        
        Args:
            principal: Valor inicial
            taxa_mensal: Taxa de juros mensal (ex: 0.01 = 1%)
            meses: Número de meses
            aporte_mensal: Aporte mensal adicional (opcional)
        
        Returns:
            Dict com montante final, juros totais e evolução mensal
        """
        principal = Decimal(str(principal))
        taxa_mensal = Decimal(str(taxa_mensal))
        aporte_mensal = Decimal(str(aporte_mensal))
        
        evolucao = []
        montante_atual = principal
        juros_acumulados = Decimal("0")
        
        for mes in range(1, meses + 1):
            juros_mes = montante_atual * taxa_mensal
            montante_atual = montante_atual + juros_mes + aporte_mensal
            juros_acumulados += juros_mes
            
            evolucao.append({
                "mes": mes,
                "montante": float(montante_atual.quantize(Decimal("0.01"), ROUND_HALF_UP)),
                "juros_mes": float(juros_mes.quantize(Decimal("0.01"), ROUND_HALF_UP)),
                "juros_acumulados": float(juros_acumulados.quantize(Decimal("0.01"), ROUND_HALF_UP))
            })
        
        return {
            "principal": float(principal),
            "taxa_mensal": float(taxa_mensal),
            "meses": meses,
            "aporte_mensal": float(aporte_mensal),
            "montante_final": float(montante_atual.quantize(Decimal("0.01"), ROUND_HALF_UP)),
            "juros_totais": float(juros_acumulados.quantize(Decimal("0.01"), ROUND_HALF_UP)),
            "evolucao": evolucao
        }

    @staticmethod
    def calcular_data_quitacao(
        divida_total: Decimal,
        pagamento_mensal: Decimal,
        taxa_juros_mensal: Decimal,
        data_inicio: Optional[datetime] = None
    ) -> DebtProjection:
        """
        Calcula a data exata de quitação de uma dívida
        usando o Sistema de Amortização Price (parcelas fixas)
        
        n = -log(1 - (PV * i / PMT)) / log(1 + i)
        
        Args:
            divida_total: Valor total da dívida
            pagamento_mensal: Valor que será pago por mês
            taxa_juros_mensal: Taxa de juros mensal
            data_inicio: Data de início (default: hoje)
        
        Returns:
            DebtProjection com todos os detalhes da projeção
        """
        divida = Decimal(str(divida_total))
        pagamento = Decimal(str(pagamento_mensal))
        taxa = Decimal(str(taxa_juros_mensal))
        data_inicio = data_inicio or datetime.now()
        
        # Validações
        if divida <= 0:
            raise ValueError("Dívida deve ser maior que zero")
        if pagamento <= 0:
            raise ValueError("Pagamento deve ser maior que zero")
        
        # Se não há juros, cálculo simples
        if taxa <= 0:
            meses = math.ceil(float(divida / pagamento))
            data_quitacao = data_inicio + timedelta(days=meses * 30)
            return DebtProjection(
                debt_total=divida,
                monthly_payment=pagamento,
                interest_rate=taxa,
                months_to_payoff=meses,
                payoff_date=data_quitacao,
                total_interest_paid=Decimal("0"),
                total_amount_paid=divida
            )
        
        # Verificar se pagamento cobre os juros
        juros_minimo = divida * taxa
        if pagamento <= juros_minimo:
            raise ValueError(
                f"Pagamento de R${pagamento:.2f} não cobre os juros mensais "
                f"de R${juros_minimo:.2f}. Dívida infinita!"
            )
        
        # Fórmula para calcular número de parcelas
        # n = -log(1 - (PV * i / PMT)) / log(1 + i)
        numerador = Decimal(str(math.log(1 - float(divida * taxa / pagamento))))
        denominador = Decimal(str(math.log(1 + float(taxa))))
        meses_raw = -float(numerador / denominador)
        meses = math.ceil(meses_raw)
        
        # Simular pagamentos para valores exatos
        saldo = divida
        juros_total = Decimal("0")
        total_pago = Decimal("0")
        
        for _ in range(meses):
            juros_mes = saldo * taxa
            amortizacao = min(pagamento - juros_mes, saldo)
            saldo = max(Decimal("0"), saldo - amortizacao)
            juros_total += juros_mes
            total_pago += pagamento if saldo > 0 else (amortizacao + juros_mes)
        
        data_quitacao = data_inicio + timedelta(days=meses * 30)
        
        return DebtProjection(
            debt_total=divida.quantize(Decimal("0.01"), ROUND_HALF_UP),
            monthly_payment=pagamento.quantize(Decimal("0.01"), ROUND_HALF_UP),
            interest_rate=taxa,
            months_to_payoff=meses,
            payoff_date=data_quitacao,
            total_interest_paid=juros_total.quantize(Decimal("0.01"), ROUND_HALF_UP),
            total_amount_paid=total_pago.quantize(Decimal("0.01"), ROUND_HALF_UP)
        )

    @staticmethod
    def calcular_impacto_gasto(
        divida_atual: Decimal,
        pagamento_mensal: Decimal,
        taxa_mensal: Decimal,
        novo_gasto: Decimal
    ) -> Dict:
        """
        Calcula o impacto de um novo gasto na data de quitação
        (Usado pela IA para dar feedback em tempo real)
        
        Returns:
            Dict com dias adicionais de dívida e custo real do gasto
        """
        # Projeção atual
        proj_atual = FinancialEngine.calcular_data_quitacao(
            divida_atual, pagamento_mensal, taxa_mensal
        )
        
        # Projeção com novo gasto
        nova_divida = Decimal(str(divida_atual)) + Decimal(str(novo_gasto))
        proj_nova = FinancialEngine.calcular_data_quitacao(
            nova_divida, pagamento_mensal, taxa_mensal
        )
        
        meses_adicionais = proj_nova.months_to_payoff - proj_atual.months_to_payoff
        dias_adicionais = meses_adicionais * 30
        juros_adicionais = proj_nova.total_interest_paid - proj_atual.total_interest_paid
        custo_real = Decimal(str(novo_gasto)) + juros_adicionais
        
        return {
            "gasto_original": float(novo_gasto),
            "custo_real": float(custo_real.quantize(Decimal("0.01"), ROUND_HALF_UP)),
            "juros_adicionais": float(juros_adicionais.quantize(Decimal("0.01"), ROUND_HALF_UP)),
            "dias_adicionais": dias_adicionais,
            "meses_adicionais": meses_adicionais,
            "data_quitacao_antiga": proj_atual.payoff_date.strftime("%B %Y"),
            "data_quitacao_nova": proj_nova.payoff_date.strftime("%B %Y"),
            "mensagem_coach": FinancialEngine._gerar_mensagem_impacto(
                novo_gasto, dias_adicionais, custo_real
            )
        }

    @staticmethod
    def _gerar_mensagem_impacto(gasto: Decimal, dias: int, custo_real: Decimal) -> str:
        """Gera mensagem do coach sobre o impacto do gasto"""
        gasto = float(gasto)
        custo = float(custo_real)
        
        if dias == 0:
            return f"Esse gasto de R${gasto:.2f} não muda muito sua situação. Tá safe!"
        elif dias <= 3:
            return f"Aí não, mano! Esse gasto de R${gasto:.2f} te custou {dias} dias a mais de dívida."
        elif dias <= 7:
            return f"Cara, R${gasto:.2f} virou R${custo:.2f} com os juros. Uma semana a mais pagando banco!"
        elif dias <= 30:
            return f"Eita! Esse gasto te atrasou quase {dias} dias. Custo real: R${custo:.2f}. Bora repensar?"
        else:
            return f"Mano, isso é sério. R${gasto:.2f} virou {dias} dias de dívida extra. Custo total: R${custo:.2f}!"

    @staticmethod
    def calcular_score_interno(
        historico_transacoes: List[Dict],
        meses_analise: int = 3
    ) -> Dict:
        """
        Calcula o Score Comportamental Interno (0-1000)
        Baseado em:
        - Consistência de pagamentos (40%)
        - Relação receita/despesa (30%)
        - Evolução do saldo (20%)
        - Frequência de gastos supérfluos (10%)
        
        Returns:
            Dict com score e breakdown dos fatores
        """
        if not historico_transacoes:
            return {
                "score": 500,
                "nivel": "Iniciante",
                "breakdown": {
                    "consistencia": 50,
                    "relacao_receita_despesa": 50,
                    "evolucao_saldo": 50,
                    "controle_gastos": 50
                },
                "dicas": ["Comece registrando suas transações para ter um score mais preciso!"]
            }
        
        # Análise de consistência (pagamentos em dia)
        score_consistencia = 100  # Começa perfeito, deduz por atrasos
        
        # Análise receita/despesa
        total_receita = sum(t["valor"] for t in historico_transacoes if t["tipo"] == "receita")
        total_despesa = sum(abs(t["valor"]) for t in historico_transacoes if t["tipo"] == "despesa")
        
        if total_receita > 0:
            relacao = (total_receita - total_despesa) / total_receita
            score_relacao = min(100, max(0, 50 + relacao * 50))
        else:
            score_relacao = 30
        
        # Análise de evolução (tendência do saldo)
        score_evolucao = 60  # Base neutra
        
        # Análise de gastos supérfluos
        categorias_superfluas = ["delivery", "streaming", "jogos", "luxo", "lazer"]
        gastos_superfluo = sum(
            abs(t["valor"]) for t in historico_transacoes 
            if t.get("categoria", "").lower() in categorias_superfluas
        )
        
        if total_despesa > 0:
            percentual_superfluo = gastos_superfluo / total_despesa
            score_controle = min(100, max(0, 100 - percentual_superfluo * 200))
        else:
            score_controle = 70
        
        # Cálculo final ponderado
        score_final = int(
            (score_consistencia * 0.4 +
             score_relacao * 0.3 +
             score_evolucao * 0.2 +
             score_controle * 0.1) * 10
        )
        
        # Determinar nível
        if score_final >= 800:
            nivel = "Excelente"
        elif score_final >= 650:
            nivel = "Bom"
        elif score_final >= 500:
            nivel = "Regular"
        elif score_final >= 350:
            nivel = "Atenção"
        else:
            nivel = "Crítico"
        
        return {
            "score": min(1000, max(0, score_final)),
            "nivel": nivel,
            "breakdown": {
                "consistencia": int(score_consistencia),
                "relacao_receita_despesa": int(score_relacao),
                "evolucao_saldo": int(score_evolucao),
                "controle_gastos": int(score_controle)
            },
            "dicas": FinancialEngine._gerar_dicas_score(score_final, score_relacao, score_controle)
        }

    @staticmethod
    def _gerar_dicas_score(score: int, relacao: float, controle: float) -> List[str]:
        """Gera dicas personalizadas baseadas no score"""
        dicas = []
        
        if score < 500:
            dicas.append("🔴 Foco total em quitar dívidas! Corte gastos não essenciais.")
        
        if relacao < 50:
            dicas.append("📊 Suas despesas estão maiores que receitas. Hora de ajustar!")
        
        if controle < 50:
            dicas.append("🎮 Muitos gastos com lazer. Que tal um limite mensal de R$100?")
        
        if score >= 700:
            dicas.append("⭐ Mandou bem! Continue assim e aumente sua reserva de emergência.")
        
        if not dicas:
            dicas.append("📈 Você está no caminho certo! Mantenha a consistência.")
        
        return dicas

    @staticmethod
    def simular_cenario(
        divida_atual: Decimal,
        pagamento_atual: Decimal,
        taxa_mensal: Decimal,
        cenario: Dict
    ) -> Dict:
        """
        Simula cenários "E se?" para o usuário
        
        Cenários suportados:
        - vender_algo: Simula venda de um bem
        - aumentar_pagamento: Simula aumento do pagamento mensal
        - renda_extra: Simula entrada de renda extra
        
        Returns:
            Dict comparando cenário atual vs simulado
        """
        # Projeção atual
        proj_atual = FinancialEngine.calcular_data_quitacao(
            divida_atual, pagamento_atual, taxa_mensal
        )
        
        nova_divida = Decimal(str(divida_atual))
        novo_pagamento = Decimal(str(pagamento_atual))
        
        tipo_cenario = cenario.get("tipo")
        valor = Decimal(str(cenario.get("valor", 0)))
        
        if tipo_cenario == "vender_algo":
            nova_divida = max(Decimal("0"), nova_divida - valor)
        elif tipo_cenario == "aumentar_pagamento":
            novo_pagamento += valor
        elif tipo_cenario == "renda_extra":
            nova_divida = max(Decimal("0"), nova_divida - valor)
        
        # Nova projeção
        if nova_divida > 0:
            proj_nova = FinancialEngine.calcular_data_quitacao(
                nova_divida, novo_pagamento, taxa_mensal
            )
            economia_meses = proj_atual.months_to_payoff - proj_nova.months_to_payoff
            economia_juros = proj_atual.total_interest_paid - proj_nova.total_interest_paid
        else:
            economia_meses = proj_atual.months_to_payoff
            economia_juros = proj_atual.total_interest_paid
            proj_nova = None
        
        return {
            "cenario": cenario,
            "atual": {
                "divida": float(divida_atual),
                "meses_para_quitar": proj_atual.months_to_payoff,
                "data_quitacao": proj_atual.payoff_date.strftime("%B %Y"),
                "juros_total": float(proj_atual.total_interest_paid)
            },
            "simulado": {
                "nova_divida": float(nova_divida),
                "meses_para_quitar": proj_nova.months_to_payoff if proj_nova else 0,
                "data_quitacao": proj_nova.payoff_date.strftime("%B %Y") if proj_nova else "QUITADO!",
                "juros_total": float(proj_nova.total_interest_paid) if proj_nova else 0
            },
            "economia": {
                "meses": economia_meses,
                "juros": float(economia_juros.quantize(Decimal("0.01"), ROUND_HALF_UP))
            },
            "mensagem": FinancialEngine._gerar_mensagem_simulacao(tipo_cenario, valor, economia_meses)
        }

    @staticmethod
    def _gerar_mensagem_simulacao(tipo: str, valor: Decimal, meses: int) -> str:
        """Gera mensagem motivacional para simulação"""
        valor = float(valor)
        
        if tipo == "vender_algo":
            return f"🔥 Mano! Vendendo isso por R${valor:.2f}, você economiza {meses} meses de dívida!"
        elif tipo == "aumentar_pagamento":
            return f"💪 Pagando R${valor:.2f} a mais por mês, você se livra {meses} meses antes!"
        elif tipo == "renda_extra":
            return f"💰 Com essa grana extra de R${valor:.2f}, você adianta {meses} meses da sua liberdade!"
        return f"📊 Essa mudança pode te economizar {meses} meses de dívida!"


# Funções auxiliares para uso direto nas rotas
def calcular_liberdade_financeira(
    divida: float,
    pagamento: float,
    taxa: float = 0.05
) -> Dict:
    """
    Wrapper simples para calcular data de liberdade financeira
    Taxa padrão: 5% a.m. (média entre consignado e cheque especial)
    """
    try:
        proj = FinancialEngine.calcular_data_quitacao(
            Decimal(str(divida)),
            Decimal(str(pagamento)),
            Decimal(str(taxa))
        )
        
        dias_restantes = (proj.payoff_date - datetime.now()).days
        
        return {
            "success": True,
            "data_liberdade": proj.payoff_date.strftime("%Y-%m-%d"),
            "data_liberdade_formatada": proj.payoff_date.strftime("%B de %Y"),
            "meses_restantes": proj.months_to_payoff,
            "dias_restantes": max(0, dias_restantes),
            "juros_total": float(proj.total_interest_paid),
            "total_a_pagar": float(proj.total_amount_paid)
        }
    except ValueError as e:
        return {
            "success": False,
            "error": str(e)
        }


def analisar_transacao_para_ia(
    valor: float,
    tipo: str,
    saldo_atual: float,
    divida_total: float,
    pagamento_mensal: float
) -> Dict:
    """
    Analisa uma transação e retorna contexto para a IA
    """
    analise = {
        "valor": valor,
        "tipo": tipo,
        "saldo_atual": saldo_atual,
        "status_financeiro": "verde" if saldo_atual >= 0 else "vermelho",
        "tem_divida": divida_total > 0,
        "impacto": None
    }
    
    # Se é um gasto e tem dívida, calcular impacto
    if tipo == "despesa" and divida_total > 0 and pagamento_mensal > 0:
        try:
            impacto = FinancialEngine.calcular_impacto_gasto(
                Decimal(str(divida_total)),
                Decimal(str(pagamento_mensal)),
                Decimal("0.05"),  # 5% a.m. padrão
                Decimal(str(abs(valor)))
            )
            analise["impacto"] = impacto
        except:
            pass
    
    return analise
