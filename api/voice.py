"""
ORBIT - Voice Routes
Rotas da API de Voz
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, status
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from app.services.voice_service import voice_service, transcrever_mensagem_voz

router = APIRouter()


# ============================================
# 📝 SCHEMAS
# ============================================

class VoiceTranscriptionInput(BaseModel):
    """Input para transcrição via base64"""
    audio_base64: str
    formato: str = "webm"


class VoiceTranscriptionResponse(BaseModel):
    """Resposta da transcrição"""
    texto: str
    idioma: str
    confianca: float
    duracao_segundos: float
    timestamp: datetime


# ============================================
# 🚀 ENDPOINTS
# ============================================

@router.post("/transcrever", response_model=VoiceTranscriptionResponse)
async def transcrever_audio(input: VoiceTranscriptionInput):
    """
    Transcreve áudio para texto
    Aceita áudio em base64
    """
    if not voice_service.esta_disponivel():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Serviço de voz não disponível. Instale faster-whisper."
        )
    
    try:
        resultado = await voice_service.transcrever_base64(
            input.audio_base64,
            input.formato
        )
        
        return VoiceTranscriptionResponse(
            texto=resultado.texto,
            idioma=resultado.idioma,
            confianca=resultado.confianca,
            duracao_segundos=resultado.duracao_segundos,
            timestamp=datetime.now()
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro na transcrição: {str(e)}"
        )


@router.post("/transcrever/upload")
async def transcrever_upload(
    audio: UploadFile = File(...)
):
    """
    Transcreve áudio via upload de arquivo
    Aceita: webm, mp3, wav, m4a
    """
    if not voice_service.esta_disponivel():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Serviço de voz não disponível"
        )
    
    # Validar tipo de arquivo
    allowed_types = ["audio/webm", "audio/mp3", "audio/wav", "audio/x-m4a", "audio/mpeg"]
    if audio.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo de arquivo não suportado: {audio.content_type}"
        )
    
    try:
        # Ler arquivo
        audio_bytes = await audio.read()
        
        # Extrair formato da extensão
        formato = audio.filename.split(".")[-1] if audio.filename else "webm"
        
        # Transcrever
        resultado = await voice_service.transcrever_audio(audio_bytes, formato)
        
        return {
            "texto": resultado.texto,
            "idioma": resultado.idioma,
            "confianca": resultado.confianca,
            "duracao_segundos": resultado.duracao_segundos,
            "arquivo": audio.filename
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar áudio: {str(e)}"
        )


@router.get("/status")
async def status_voz():
    """Retorna status do serviço de voz"""
    return {
        "disponivel": voice_service.esta_disponivel(),
        "modelo": voice_service.model_size if voice_service.model else None,
        "engine": "faster-whisper"
    }
