"""
ORBIT - OCR Routes
Rotas da API de OCR (Leitura de Recibos)
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from app.services.ocr_service import ocr_service, processar_foto_recibo

router = APIRouter()


# ============================================
# 📝 SCHEMAS
# ============================================

class OCRInput(BaseModel):
    """Input para OCR via base64"""
    imagem_base64: str


class OCRResponse(BaseModel):
    """Resposta do OCR"""
    estabelecimento: Optional[str]
    valor_total: Optional[float]
    data: Optional[str]
    itens: List[dict]
    confianca: float
    texto_completo: str


class TransacaoSugerida(BaseModel):
    """Transação sugerida baseada no OCR"""
    tipo: str
    categoria: str
    valor: Optional[float]
    descricao: str
    data: str
    origem: str
    confianca_ocr: float


# ============================================
# 🚀 ENDPOINTS
# ============================================

@router.post("/processar", response_model=OCRResponse)
async def processar_imagem(input: OCRInput):
    """
    Processa imagem e extrai dados do recibo
    Aceita imagem em base64
    """
    if not ocr_service.ocr_engine:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Serviço OCR não disponível. Instale paddleocr ou easyocr."
        )
    
    try:
        recibo = await ocr_service.processar_base64(input.imagem_base64)
        
        return OCRResponse(
            estabelecimento=recibo.estabelecimento,
            valor_total=recibo.valor_total,
            data=recibo.data,
            itens=recibo.itens,
            confianca=recibo.confianca,
            texto_completo=recibo.texto_completo
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro no processamento OCR: {str(e)}"
        )


@router.post("/processar/upload")
async def processar_upload(
    imagem: UploadFile = File(...)
):
    """
    Processa imagem via upload de arquivo
    Aceita: jpg, jpeg, png, webp
    """
    if not ocr_service.ocr_engine:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Serviço OCR não disponível"
        )
    
    # Validar tipo de arquivo
    allowed_types = ["image/jpeg", "image/png", "image/webp"]
    if imagem.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo de arquivo não suportado: {imagem.content_type}"
        )
    
    try:
        # Ler arquivo
        imagem_bytes = await imagem.read()
        
        # Extrair formato
        formato = imagem.filename.split(".")[-1] if imagem.filename else "jpg"
        
        # Processar
        recibo = await ocr_service.processar_imagem(imagem_bytes, formato)
        
        return {
            "estabelecimento": recibo.estabelecimento,
            "valor_total": recibo.valor_total,
            "data": recibo.data,
            "itens": recibo.itens,
            "confianca": recibo.confianca,
            "arquivo": imagem.filename
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar imagem: {str(e)}"
        )


@router.post("/para-transacao", response_model=TransacaoSugerida)
async def ocr_para_transacao(input: OCRInput):
    """
    Processa imagem e retorna transação sugerida
    Ideal para integração direta com o chat
    """
    try:
        transacao = await processar_foto_recibo(input.imagem_base64)
        
        return TransacaoSugerida(
            tipo=transacao["tipo"],
            categoria=transacao["categoria"],
            valor=transacao["valor"],
            descricao=transacao["descricao"],
            data=transacao["data"],
            origem=transacao["origem"],
            confianca_ocr=transacao["confianca_ocr"]
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao processar recibo: {str(e)}"
        )


@router.get("/status")
async def status_ocr():
    """Retorna status do serviço OCR"""
    return {
        "disponivel": ocr_service.ocr_engine is not None,
        "engine": ocr_service.engine_type,
        "formatos_suportados": ["jpg", "jpeg", "png", "webp"]
    }
