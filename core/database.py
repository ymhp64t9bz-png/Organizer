"""
ORBIT - Database Connection
Conexão assíncrona com PostgreSQL
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# Engine assíncrono
engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    echo=settings.DEBUG
)

# Session factory
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Base para os modelos
Base = declarative_base()


async def get_db():
    """Dependency para injetar sessão do banco"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Inicializa o banco de dados"""
    async with engine.begin() as conn:
        # Criar extensão pgvector se disponível
        try:
            await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
        except:
            print("⚠️ PGVector não disponível")
        
        # Criar tabelas
        await conn.run_sync(Base.metadata.create_all)
    
    print("✅ Banco de dados inicializado")
