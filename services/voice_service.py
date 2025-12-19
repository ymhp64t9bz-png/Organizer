"""
ORBIT - Voice Service
Transcrição de Voz para Texto

Usa Faster-Whisper (Open Source / Local)
"""

import os
import tempfile
import base64
from typing import Dict, Optional
from dataclasses import dataclass


@dataclass
class TranscriptionResult:
    """Resultado da transcrição"""
    texto: str
    idioma: str
    confianca: float
    duracao_segundos: float


class VoiceService:
    """
    Serviço de transcrição de voz
    Usa Faster-Whisper para transcrição local
    """
    
    def __init__(self):
        self.model = None
        self.model_size = os.getenv("WHISPER_MODEL", "base")
        self._initialize_model()
    
    def _initialize_model(self):
        """Inicializa o modelo Whisper"""
        try:
            from faster_whisper import WhisperModel
            
            self.model = WhisperModel(
                self.model_size,
                device="cpu",  # Usar CPU para compatibilidade
                compute_type="int8"  # Otimizado para CPU
            )
            print(f"🎤 Voice Engine: Faster-Whisper ({self.model_size})")
            
        except ImportError:
            print("⚠️ Faster-Whisper não disponível")
            self.model = None
    
    async def transcrever_audio(
        self, 
        audio: bytes,
        formato: str = "webm"
    ) -> TranscriptionResult:
        """
        Transcreve áudio para texto
        
        Args:
            audio: Bytes do áudio
            formato: Formato do áudio (webm, mp3, wav, m4a)
        
        Returns:
            TranscriptionResult com texto e metadados
        """
        if not self.model:
            raise RuntimeError("Modelo Whisper não inicializado")
        
        # Salvar áudio temporariamente
        with tempfile.NamedTemporaryFile(
            suffix=f".{formato}",
            delete=False
        ) as tmp:
            tmp.write(audio)
            tmp_path = tmp.name
        
        try:
            # Transcrever
            segments, info = self.model.transcribe(
                tmp_path,
                language="pt",  # Português
                beam_size=5,
                vad_filter=True,  # Filtrar silêncio
                vad_parameters=dict(
                    min_silence_duration_ms=500
                )
            )
            
            # Concatenar segmentos
            texto_completo = ""
            for segment in segments:
                texto_completo += segment.text + " "
            
            return TranscriptionResult(
                texto=texto_completo.strip(),
                idioma=info.language,
                confianca=info.language_probability,
                duracao_segundos=info.duration
            )
            
        finally:
            os.unlink(tmp_path)
    
    async def transcrever_base64(
        self, 
        base64_str: str,
        formato: str = "webm"
    ) -> TranscriptionResult:
        """Transcreve áudio em base64"""
        # Remover prefixo data:audio se existir
        if "," in base64_str:
            base64_str = base64_str.split(",")[1]
        
        audio_bytes = base64.b64decode(base64_str)
        return await self.transcrever_audio(audio_bytes, formato)
    
    def esta_disponivel(self) -> bool:
        """Verifica se o serviço está disponível"""
        return self.model is not None


# Instância global
voice_service = VoiceService()


# ============================================
# 🚀 FUNÇÕES DE CONVENIÊNCIA
# ============================================

async def transcrever_mensagem_voz(audio_base64: str) -> str:
    """
    Função simplificada para transcrever mensagem de voz
    
    Returns:
        Texto transcrito
    """
    if not voice_service.esta_disponivel():
        raise RuntimeError(
            "Serviço de voz não disponível. "
            "Instale faster-whisper: pip install faster-whisper"
        )
    
    resultado = await voice_service.transcrever_base64(audio_base64)
    return resultado.texto


def verificar_servico_voz() -> Dict:
    """Verifica status do serviço de voz"""
    return {
        "disponivel": voice_service.esta_disponivel(),
        "modelo": voice_service.model_size if voice_service.model else None,
        "engine": "faster-whisper"
    }
