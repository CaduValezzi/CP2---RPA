"""Coleta de vagas em fontes públicas via API REST (requests + BeautifulSoup)."""
import logging
import time
from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup

from config import LINKEDIN_LOCAL, LINKEDIN_ULTIMAS_HORAS, TIMEOUT

log = logging.getLogger(__name__)

GUPY_URL = "https://portal.api.gupy.io/api/v1/jobs"
REMOTIVE_URL = "https://remotive.com/api/remote-jobs"
LINKEDIN_URL = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
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
    dados = _get_json(GUPY_URL, {"jobName": termo, "limit": limite, "offset": 0}).get("data", [])
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


def parsear_cards_linkedin(html: str) -> list[Vaga]:
    """Extrai as vagas do HTML devolvido pelo endpoint público do LinkedIn.
    Os seletores dependem das classes CSS do LinkedIn e podem quebrar se elas mudarem."""
    soup = BeautifulSoup(html, "html.parser")
    vagas = []
    for card in soup.select("div.base-card"):
        urn = card.get("data-entity-urn", "")  # ex.: urn:li:jobPosting:1234567890
        titulo = card.select_one("h3.base-search-card__title")
        empresa = card.select_one("h4.base-search-card__subtitle")
        local = card.select_one("span.job-search-card__location")
        link = card.select_one("a.base-card__full-link")
        if not (urn and titulo and link):
            continue
        vagas.append(
            Vaga(
                id=f"linkedin-{urn.split(':')[-1]}",
                titulo=titulo.get_text(strip=True),
                empresa=empresa.get_text(strip=True) if empresa else "",
                local=local.get_text(strip=True) if local else "Não informado",
                url=link["href"].split("?")[0],  # remove parâmetros de rastreio
                fonte="LinkedIn",
                remoto=False,
            )
        )
    return vagas


def buscar_linkedin(termo: str) -> list[Vaga]:
    """Vagas públicas do LinkedIn (uma página de ~25 resultados por termo)."""
    params = {
        "keywords": termo,
        "location": LINKEDIN_LOCAL,
        "f_TPR": f"r{LINKEDIN_ULTIMAS_HORAS * 3600}",
        "start": 0,
    }
    try:
        resp = requests.get(LINKEDIN_URL, params=params, headers=HEADERS, timeout=TIMEOUT)
        if resp.status_code == 429:
            log.warning("LinkedIn limitou as requisições (429); pulando esta fonte.")
            return []
        resp.raise_for_status()
    except requests.RequestException as exc:
        log.warning("Falha ao consultar o LinkedIn: %s", exc)
        return []
    time.sleep(2)  # intervalo educado entre requisições
    return parsear_cards_linkedin(resp.text)
