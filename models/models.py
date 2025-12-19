"""
ORBIT - Database Models
Modelos SQLAlchemy para PostgreSQL + PGVector
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from enum import Enum as PyEnum

from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Boolean,
    ForeignKey, Text, Enum, Numeric, JSON, Index
)
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.dialects.postgresql import UUID, ARRAY
import uuid

# Tentar importar pgvector
try:
    from pgvector.sqlalchemy import Vector
    PGVECTOR_AVAILABLE = True
except ImportError:
    PGVECTOR_AVAILABLE = False
    Vector = None

Base = declarative_base()


# ============================================
# 📊 ENUMS
# ============================================

class TransactionType(str, PyEnum):
    """Tipo de transação"""
    RECEITA = "receita"
    DESPESA = "despesa"


class TransactionCategory(str, PyEnum):
    """Categorias de transação"""
    ALIMENTACAO = "alimentação"
    TRANSPORTE = "transporte"
    MORADIA = "moradia"
    SAUDE = "saúde"
    EDUCACAO = "educação"
    LAZER = "lazer"
    VESTUARIO = "vestuário"
    SALARIO = "salário"
    FREELANCE = "freelance"
    INVESTIMENTO = "investimento"
    DIVIDA = "dívida"
    OUTRO = "outro"


class TransactionSource(str, PyEnum):
    """Origem da transação"""
    MANUAL = "manual"
    VOICE = "voice"
    OCR = "ocr"
    IMPORT = "import"


class FinancialStatus(str, PyEnum):
    """Status financeiro"""
    CRITICAL = "critical"
    RED = "red"
    YELLOW = "yellow"
    GREEN = "green"
    EXCELLENT = "excellent"


# ============================================
# 👤 USUÁRIO
# ============================================

class User(Base):
    """Modelo de Usuário"""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    nome = Column(String(255), nullable=False)
    senha_hash = Column(String(255), nullable=False)
    
    # Preferências
    avatar_url = Column(String(500))
    idioma = Column(String(5), default="pt-BR")
    tema = Column(String(20), default="dark")
    
    # Gamificação
    score_interno = Column(Integer, default=500)
    nivel = Column(String(50), default="Iniciante")
    
    # Timestamps
    criado_em = Column(DateTime, default=datetime.utcnow)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    ultimo_acesso = Column(DateTime)
    
    # Relacionamentos
    transacoes = relationship("Transaction", back_populates="usuario")
    dividas = relationship("Debt", back_populates="usuario")
    metas = relationship("Goal", back_populates="usuario")
    mensagens = relationship("ChatMessage", back_populates="usuario")


# ============================================
# 💰 TRANSAÇÃO
# ============================================

class Transaction(Base):
    """Modelo de Transação Financeira"""
    __tablename__ = "transactions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Dados principais
    tipo = Column(Enum(TransactionType), nullable=False)
    categoria = Column(Enum(TransactionCategory), default=TransactionCategory.OUTRO)
    valor = Column(Numeric(12, 2), nullable=False)
    descricao = Column(String(500))
    
    # Metadados
    data = Column(DateTime, default=datetime.utcnow)
    origem = Column(Enum(TransactionSource), default=TransactionSource.MANUAL)
    
    # OCR específico
    confianca_ocr = Column(Float)
    imagem_url = Column(String(500))
    dados_ocr = Column(JSON)  # Itens extraídos
    
    # Análise IA
    impacto_calculado = Column(JSON)  # Dias adicionais, custo real
    resposta_ia = Column(Text)
    
    # Timestamps
    criado_em = Column(DateTime, default=datetime.utcnow)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    usuario = relationship("User", back_populates="transacoes")
    
    # Índices
    __table_args__ = (
        Index('idx_transaction_usuario_data', 'usuario_id', 'data'),
        Index('idx_transaction_tipo', 'tipo'),
        Index('idx_transaction_categoria', 'categoria'),
    )


# ============================================
# 💳 DÍVIDA
# ============================================

class Debt(Base):
    """Modelo de Dívida"""
    __tablename__ = "debts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Dados da dívida
    nome = Column(String(255), nullable=False)  # Ex: "Cartão Nubank"
    tipo = Column(String(100))  # cartao, emprestimo, financiamento
    valor_original = Column(Numeric(12, 2), nullable=False)
    valor_atual = Column(Numeric(12, 2), nullable=False)
    
    # Juros
    taxa_juros_mensal = Column(Numeric(6, 4))  # Ex: 0.0500 = 5%
    taxa_juros_anual = Column(Numeric(6, 4))
    
    # Pagamentos
    pagamento_mensal = Column(Numeric(12, 2))
    dia_vencimento = Column(Integer)
    
    # Projeções
    data_quitacao_projetada = Column(DateTime)
    meses_para_quitar = Column(Integer)
    juros_total_projetado = Column(Numeric(12, 2))
    
    # Status
    ativo = Column(Boolean, default=True)
    quitado = Column(Boolean, default=False)
    data_quitacao = Column(DateTime)
    
    # Timestamps
    criado_em = Column(DateTime, default=datetime.utcnow)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    usuario = relationship("User", back_populates="dividas")


# ============================================
# 🎯 META FINANCEIRA
# ============================================

class Goal(Base):
    """Modelo de Meta Financeira"""
    __tablename__ = "goals"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Dados da meta
    titulo = Column(String(255), nullable=False)
    descricao = Column(Text)
    valor_alvo = Column(Numeric(12, 2), nullable=False)
    valor_atual = Column(Numeric(12, 2), default=0)
    
    # Prazos
    data_inicio = Column(DateTime, default=datetime.utcnow)
    data_alvo = Column(DateTime)
    
    # Status
    ativo = Column(Boolean, default=True)
    concluido = Column(Boolean, default=False)
    percentual_progresso = Column(Float, default=0)
    
    # Timestamps
    criado_em = Column(DateTime, default=datetime.utcnow)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    usuario = relationship("User", back_populates="metas")


# ============================================
# 💬 MENSAGEM DO CHAT
# ============================================

class ChatMessage(Base):
    """Modelo de Mensagem do Chat"""
    __tablename__ = "chat_messages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Conteúdo
    role = Column(String(20), nullable=False)  # user, assistant
    conteudo = Column(Text, nullable=False)
    
    # Metadados
    origem = Column(String(20))  # text, voice, ocr
    transacao_id = Column(UUID(as_uuid=True), ForeignKey("transactions.id"))
    
    # IA
    provider_ia = Column(String(50))  # ollama, groq, fallback
    
    # Timestamps
    criado_em = Column(DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    usuario = relationship("User", back_populates="mensagens")
    
    # Índice
    __table_args__ = (
        Index('idx_chat_usuario_data', 'usuario_id', 'criado_em'),
    )


# ============================================
# 🧠 MEMÓRIA DA IA (PGVector)
# ============================================

if PGVECTOR_AVAILABLE:
    class AIMemory(Base):
        """
        Memória vetorial da IA para contexto de longo prazo
        Requer extensão pgvector no PostgreSQL
        """
        __tablename__ = "ai_memories"
        
        id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
        usuario_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
        
        # Conteúdo
        conteudo = Column(Text, nullable=False)
        tipo = Column(String(50))  # preferencia, padrao, insight
        
        # Vetor de embedding (1536 dimensões para OpenAI, 384 para modelos menores)
        embedding = Column(Vector(384))
        
        # Metadados
        relevancia = Column(Float, default=1.0)
        acessos = Column(Integer, default=0)
        
        # Timestamps
        criado_em = Column(DateTime, default=datetime.utcnow)
        ultimo_acesso = Column(DateTime)


# ============================================
# 📊 SNAPSHOT FINANCEIRO (Histórico)
# ============================================

class FinancialSnapshot(Base):
    """Snapshot diário do estado financeiro"""
    __tablename__ = "financial_snapshots"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Data do snapshot
    data = Column(DateTime, nullable=False)
    
    # Valores
    saldo = Column(Numeric(12, 2))
    receita_mes = Column(Numeric(12, 2))
    despesa_mes = Column(Numeric(12, 2))
    divida_total = Column(Numeric(12, 2))
    
    # Score e status
    score = Column(Integer)
    status = Column(Enum(FinancialStatus))
    
    # Projeção
    dias_para_liberdade = Column(Integer)
    
    # Índice único por usuário/data
    __table_args__ = (
        Index('idx_snapshot_usuario_data', 'usuario_id', 'data', unique=True),
    )


# ============================================
# 🔧 FUNÇÕES AUXILIARES
# ============================================

def criar_tabelas(engine):
    """Cria todas as tabelas no banco"""
    Base.metadata.create_all(engine)


def verificar_pgvector(engine) -> bool:
    """Verifica se extensão pgvector está instalada"""
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1 FROM pg_extension WHERE extname = 'vector'")
            return True
    except:
        return False
