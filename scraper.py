"""Coleta de vagas em fontes públicas via API REST (requests + BeautifulSoup)."""
import logging
from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup

from config import TIMEOUT

log = logging.getLogger(__name__)

GUPY_URL = "https://portal.api.gupy.io/api/job"
REMOTIVE_URL = "https://remotive.com/api/remote-jobs"
HEADERS = {"User-Agent": "Mozilla/5.0 (radar-vagas; projeto academico)"}


@dataclass
class Vaga:
    id: str
    titulo: str
    empresa: str
    local: str
    url: str
    fonte: str
    remoto: bool
    descricao: str = ""


def _html_para_texto(html: str | None) -> str:
    """As APIs devolvem a descrição em HTML; BeautifulSoup extrai só o texto."""
    return BeautifulSoup(html or "", "html.parser").get_text(" ", strip=True)


def _get_json(url: str, params: dict) -> dict:
    try:
        resp = requests.get(url, params=params, headers=HEADERS, timeout=TIMEOUT)
        resp.raise_for_status()
        return resp.json()
    except (requests.RequestException, ValueError) as exc:
        log.warning("Falha ao consultar %s: %s", url, exc)
        return {}


def buscar_gupy(termo: str, limite: int = 50) -> list[Vaga]:
    """Vagas brasileiras do portal da Gupy."""
    dados = _get_json(GUPY_URL, {"name": termo, "limit": limite}).get("data", [])
    return [
        Vaga(
            id=f"gupy-{j['id']}",
            titulo=j.get("name", ""),
            empresa=j.get("careerPageName", ""),
            local=", ".join(filter(None, [j.get("city"), j.get("state")])) or "Não informado",
            url=j.get("jobUrl", ""),
            fonte="Gupy",
            remoto=bool(j.get("isRemoteWork")) or j.get("workplaceType") == "remote",
            descricao=_html_para_texto(j.get("description")),
        )
        for j in dados
    ]


def buscar_remotive() -> list[Vaga]:
    """Vagas remotas internacionais. Uma única chamada por execução
    (a Remotive pede poucas requisições por dia); o filtro é feito localmente."""
    dados = _get_json(REMOTIVE_URL, {"category": "software-dev", "limit": 100}).get("jobs", [])
    return [
        Vaga(
            id=f"remotive-{j['id']}",
            titulo=j.get("title", ""),
            empresa=j.get("company_name", ""),
            local=j.get("candidate_required_location") or "Remoto",
            url=j.get("url", ""),
            fonte="Remotive",
            remoto=True,
            descricao=_html_para_texto(j.get("description")),
        )
        for j in dados
    ]
