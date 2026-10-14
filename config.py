"""Configuração do radar. Ajuste os filtros aqui sem mexer na lógica."""
import os

from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

DB_PATH = "vagas.db"
TIMEOUT = 15  # segundos por requisição

# Termos enviados à busca da Gupy (uma requisição por termo)
BUSCAS = ["front-end", "frontend", "react", "vue", "angular"]

# Filtros aplicados ao TÍTULO da vaga (regex, case-insensitive)
INCLUIR = [r"front", r"react", r"vue", r"angular", r"typescript", r"next\.?js", r"javascript"]
EXCLUIR = [r"back-?end", r"java\b", r"php", r"\.net", r"dba", r"est[aá]gi", r"designer"]

# Se preenchido, a vaga precisa mencionar ao menos um destes termos (título ou descrição).
# Ex.: [r"pleno", r"s[eê]nior", r"lead", r"l[ií]der"]. Vazio = qualquer senioridade.
SENIORIDADE: list[str] = []

SOMENTE_REMOTO = False
