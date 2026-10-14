"""Regras de filtragem das vagas (padrões definidos em config.py)."""
import re

from config import EXCLUIR, INCLUIR, SENIORIDADE, SOMENTE_REMOTO
from scraper import Vaga


def _casa(texto: str, padroes: list[str]) -> bool:
    return any(re.search(p, texto, re.IGNORECASE) for p in padroes)


def filtrar(vagas: list[Vaga]) -> list[Vaga]:
    """Remove duplicadas e mantém só as vagas que batem com as regras."""
    vistos: set[str] = set()
    aprovadas = []
    for v in vagas:
        if v.id in vistos:
            continue
        vistos.add(v.id)

        if not _casa(v.titulo, INCLUIR) or _casa(v.titulo, EXCLUIR):
            continue
        if SENIORIDADE and not _casa(f"{v.titulo} {v.descricao}", SENIORIDADE):
            continue
        if SOMENTE_REMOTO and not v.remoto:
            continue
        aprovadas.append(v)
    return aprovadas
