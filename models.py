from pydantic import BaseModel, Field
from typing import Optional
from logger import setup_logger

logger = setup_logger(__name__)


class CertidaoNegativa(BaseModel):
    """Modelo de dados para Certidão Negativa"""
    
    estado: str = Field(..., description="Estado emissor da certidão")
    numero_doc: str = Field(..., description="Número do documento da certidão")
    data_emissao: str = Field(..., description="Data de emissão (DD/MM/YYYY)")
    hora_emissao: str = Field(..., description="Hora de emissão (HH:MM:SS)")
    validade: str = Field(..., description="Data de validade (DD/MM/YYYY)")
    autenticacao: str = Field(..., description="Número de autenticação")
    cnpj: Optional[str] = Field(None, description="CNPJ associado (opcional)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "estado": "MATO GROSSO",
                "numero_doc": "0062719864",
                "data_emissao": "30/04/2026",
                "hora_emissao": "11:49:54",
                "validade": "28/06/2026",
                "autenticacao": "TM9BLLB2BTTKU277"
            }
        }
    
    def to_dict(self):
        """Converte para dicionário, excluindo None values"""
        return {k: v for k, v in self.dict().items() if v is not None}
    
    def __str__(self):
        return f"CertidaoNegativa(doc={self.numero_doc}, estado={self.estado}, valida até {self.validade})"
