from pydantic import BaseModel
from typing import List


# RAMAL
class IronvoxRamalItem(BaseModel):
    ramal: str
    nome_usuario: str
    setor: str


class IronvoxRamalRequest(BaseModel):
    dados: List[IronvoxRamalItem]


# AGENTE
class IronvoxAgenteItem(BaseModel):
    nome_usuario: str
    ramal: str
    setor: str


class IronvoxAgenteRequest(BaseModel):
    agentes: List[IronvoxAgenteItem]


class ListaNumerosRequest(BaseModel):
    numeros: List[str]
