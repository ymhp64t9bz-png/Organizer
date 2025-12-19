"""
ORBIT - OCR Service
Leitura de Recibos e Notas Fiscais

Usa PaddleOCR ou EasyOCR (Open Source / Local)
"""

import os
import re
import json
import tempfile
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
from pathlib import Path
import base64


@dataclass
class ReceiptData:
    """Dados extraídos de um recibo"""
    estabelecimento: Optional[str]
    valor_total: Optional[float]
    data: Optional[str]
    itens: List[Dict]
    texto_completo: str
    confianca: float


class OCRService:
    """
    Serviço de OCR para leitura de recibos
    Prioriza PaddleOCR, fallback para EasyOCR
    """
    
    def __init__(self):
        self.ocr_engine = None
        self.engine_type = None
        self._initialize_engine()
    
    def _initialize_engine(self):
        """Inicializa o melhor engine OCR disponível"""
        
        # Tentar PaddleOCR primeiro (melhor performance)
        try:
            from paddleocr import PaddleOCR
            self.ocr_engine = PaddleOCR(
                use_angle_cls=True,
                lang='pt',  # Português
                use_gpu=False,  # CPU para compatibilidade
                show_log=False
            )
            self.engine_type = "paddle"
            print("📷 OCR Engine: PaddleOCR")
            return
        except ImportError:
            print("⚠️ PaddleOCR não disponível")
        
        # Fallback para EasyOCR
        try:
            import easyocr
            self.ocr_engine = easyocr.Reader(
                ['pt', 'en'],  # Português e Inglês
                gpu=False
            )
            self.engine_type = "easy"
            print("📷 OCR Engine: EasyOCR")
            return
        except ImportError:
            print("⚠️ EasyOCR não disponível")
        
        print("❌ Nenhum OCR engine disponível!")
        self.engine_type = None
    
    async def processar_imagem(
        self, 
        imagem: bytes,
        formato: str = "jpg"
    ) -> ReceiptData:
        """
        Processa uma imagem e extrai dados do recibo
        
        Args:
            imagem: Bytes da imagem
            formato: Formato da imagem (jpg, png)
        
        Returns:
            ReceiptData com informações extraídas
        """
        if not self.ocr_engine:
            raise RuntimeError("OCR Engine não inicializado")
        
        # Salvar imagem temporariamente
        with tempfile.NamedTemporaryFile(
            suffix=f".{formato}", 
            delete=False
        ) as tmp:
            tmp.write(imagem)
            tmp_path = tmp.name
        
        try:
            # Executar OCR
            if self.engine_type == "paddle":
                resultado = self._processar_paddle(tmp_path)
            else:
                resultado = self._processar_easyocr(tmp_path)
            
            # Extrair dados estruturados
            dados_extraidos = self._extrair_dados_recibo(resultado)
            
            return dados_extraidos
            
        finally:
            # Limpar arquivo temporário
            os.unlink(tmp_path)
    
    async def processar_base64(self, base64_str: str) -> ReceiptData:
        """Processa imagem em base64"""
        # Remover prefixo data:image se existir
        if "," in base64_str:
            base64_str = base64_str.split(",")[1]
        
        imagem_bytes = base64.b64decode(base64_str)
        return await self.processar_imagem(imagem_bytes)
    
    def _processar_paddle(self, caminho: str) -> List[Tuple[str, float]]:
        """Processa com PaddleOCR"""
        resultado = self.ocr_engine.ocr(caminho, cls=True)
        
        linhas = []
        if resultado and resultado[0]:
            for linha in resultado[0]:
                texto = linha[1][0]
                confianca = linha[1][1]
                linhas.append((texto, confianca))
        
        return linhas
    
    def _processar_easyocr(self, caminho: str) -> List[Tuple[str, float]]:
        """Processa com EasyOCR"""
        resultado = self.ocr_engine.readtext(caminho)
        
        linhas = []
        for deteccao in resultado:
            texto = deteccao[1]
            confianca = deteccao[2]
            linhas.append((texto, confianca))
        
        return linhas
    
    def _extrair_dados_recibo(
        self, 
        linhas_ocr: List[Tuple[str, float]]
    ) -> ReceiptData:
        """
        Extrai dados estruturados das linhas de OCR
        
        Padrões reconhecidos:
        - Valor total (R$, TOTAL, VALOR)
        - Data (DD/MM/YYYY, DD-MM-YY)
        - Estabelecimento (primeira linha geralmente)
        - Itens (padrão: descrição + valor)
        """
        if not linhas_ocr:
            return ReceiptData(
                estabelecimento=None,
                valor_total=None,
                data=None,
                itens=[],
                texto_completo="",
                confianca=0
            )
        
        texto_completo = "\n".join([l[0] for l in linhas_ocr])
        confianca_media = sum([l[1] for l in linhas_ocr]) / len(linhas_ocr)
        
        # Extrair estabelecimento (primeira linha significativa)
        estabelecimento = None
        for texto, conf in linhas_ocr[:3]:
            if len(texto) > 3 and not re.match(r'^[\d\s\-\/\.]+$', texto):
                estabelecimento = texto.strip()
                break
        
        # Extrair valor total
        valor_total = self._extrair_valor_total(texto_completo)
        
        # Extrair data
        data = self._extrair_data(texto_completo)
        
        # Extrair itens
        itens = self._extrair_itens(linhas_ocr)
        
        return ReceiptData(
            estabelecimento=estabelecimento,
            valor_total=valor_total,
            data=data,
            itens=itens,
            texto_completo=texto_completo,
            confianca=confianca_media
        )
    
    def _extrair_valor_total(self, texto: str) -> Optional[float]:
        """Extrai valor total do recibo"""
        texto_upper = texto.upper()
        
        # Padrões para valor total
        padroes = [
            r'TOTAL\s*:?\s*R?\$?\s*([\d.,]+)',
            r'VALOR\s+TOTAL\s*:?\s*R?\$?\s*([\d.,]+)',
            r'SUBTOTAL\s*:?\s*R?\$?\s*([\d.,]+)',
            r'A\s+PAGAR\s*:?\s*R?\$?\s*([\d.,]+)',
            r'VALOR\s*:?\s*R?\$?\s*([\d.,]+)',
            r'R\$\s*([\d.,]+)',
        ]
        
        valores_encontrados = []
        
        for padrao in padroes:
            matches = re.findall(padrao, texto_upper)
            for match in matches:
                try:
                    valor_str = match.replace('.', '').replace(',', '.')
                    valor = float(valor_str)
                    if valor > 0 and valor < 100000:  # Sanity check
                        valores_encontrados.append(valor)
                except ValueError:
                    continue
        
        # Retornar o maior valor (geralmente é o total)
        if valores_encontrados:
            return max(valores_encontrados)
        
        return None
    
    def _extrair_data(self, texto: str) -> Optional[str]:
        """Extrai data do recibo"""
        # Padrões de data brasileiros
        padroes = [
            r'(\d{2}/\d{2}/\d{4})',
            r'(\d{2}/\d{2}/\d{2})',
            r'(\d{2}-\d{2}-\d{4})',
            r'(\d{2}-\d{2}-\d{2})',
        ]
        
        for padrao in padroes:
            match = re.search(padrao, texto)
            if match:
                data_str = match.group(1)
                # Normalizar para formato ISO
                try:
                    if len(data_str) == 10:  # DD/MM/YYYY
                        dt = datetime.strptime(
                            data_str.replace('-', '/'), 
                            "%d/%m/%Y"
                        )
                    else:  # DD/MM/YY
                        dt = datetime.strptime(
                            data_str.replace('-', '/'), 
                            "%d/%m/%y"
                        )
                    return dt.strftime("%Y-%m-%d")
                except ValueError:
                    continue
        
        return None
    
    def _extrair_itens(
        self, 
        linhas_ocr: List[Tuple[str, float]]
    ) -> List[Dict]:
        """Extrai itens individuais do recibo"""
        itens = []
        
        # Padrão: texto seguido de valor
        padrao_item = r'(.+?)\s+R?\$?\s*([\d.,]+)$'
        
        for texto, confianca in linhas_ocr:
            match = re.match(padrao_item, texto.strip())
            if match:
                descricao = match.group(1).strip()
                valor_str = match.group(2).replace('.', '').replace(',', '.')
                
                try:
                    valor = float(valor_str)
                    if valor > 0 and valor < 10000 and len(descricao) > 2:
                        itens.append({
                            "descricao": descricao,
                            "valor": valor,
                            "confianca": confianca
                        })
                except ValueError:
                    continue
        
        return itens
    
    def recibo_para_transacao(self, recibo: ReceiptData) -> Dict:
        """
        Converte dados do recibo para formato de transação
        """
        return {
            "tipo": "despesa",
            "categoria": self._inferir_categoria(recibo.estabelecimento),
            "valor": recibo.valor_total,
            "descricao": recibo.estabelecimento or "Compra",
            "data": recibo.data or datetime.now().strftime("%Y-%m-%d"),
            "origem": "ocr",
            "confianca_ocr": recibo.confianca,
            "itens": recibo.itens
        }
    
    def _inferir_categoria(self, estabelecimento: Optional[str]) -> str:
        """Infere categoria baseado no nome do estabelecimento"""
        if not estabelecimento:
            return "outro"
        
        estab_lower = estabelecimento.lower()
        
        mapeamento = {
            "alimentação": [
                "restaurante", "lanchonete", "pizzaria", "ifood", "rappi",
                "mcdonald", "burger", "subway", "mercado", "supermercado",
                "padaria", "açougue", "hortifruti", "café", "bar"
            ],
            "transporte": [
                "uber", "99", "posto", "shell", "ipiranga", "petrobras",
                "estacionamento", "metro", "ônibus"
            ],
            "farmácia": [
                "farmácia", "droga", "drogaria", "drogasil", "pacheco"
            ],
            "lazer": [
                "cinema", "teatro", "show", "netflix", "spotify",
                "livraria", "games"
            ],
            "moradia": [
                "luz", "água", "gás", "enel", "sabesp", "comgás",
                "aluguel", "condomínio"
            ]
        }
        
        for categoria, palavras in mapeamento.items():
            if any(p in estab_lower for p in palavras):
                return categoria
        
        return "outro"


# Instância global
ocr_service = OCRService()


# ============================================
# 🚀 FUNÇÕES DE CONVENIÊNCIA
# ============================================

async def processar_foto_recibo(imagem_base64: str) -> Dict:
    """
    Função simplificada para processar foto de recibo
    
    Returns:
        Dict pronto para criar transação
    """
    recibo = await ocr_service.processar_base64(imagem_base64)
    return ocr_service.recibo_para_transacao(recibo)


async def extrair_texto_imagem(imagem_base64: str) -> str:
    """
    Extrai apenas o texto de uma imagem
    """
    recibo = await ocr_service.processar_base64(imagem_base64)
    return recibo.texto_completo
