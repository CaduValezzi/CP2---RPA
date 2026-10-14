# Radar de vagas front-end

Automação em Python que busca vagas front-end (Gupy e Remotive), filtra por regras
configuráveis, ignora as já vistas (SQLite) e envia as novas no Telegram.

## Uso
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # preencha TELEGRAM_TOKEN e TELEGRAM_CHAT_ID
python main.py --dry-run    # testa sem enviar
python main.py              # roda de verdade
```

## Telegram
1. Fale com `@BotFather` → `/newbot` → copie o token.
2. Mande uma mensagem para o seu bot e abra `https://api.telegram.org/bot<TOKEN>/getUpdates` para achar o `chat.id`.

## Ajustes
Palavras-chave, exclusões, senioridade e modo "somente remoto" ficam em `config.py`.

## Estrutura
- `scraper.py`: coleta (requests + BeautifulSoup)
- `filtros.py`: regras de filtragem
- `storage.py`: histórico em SQLite
- `notificador.py`: envio via Telegram Bot API
- `main.py`: orquestra o fluxo

## Fontes de dados
- Gupy (API pública do portal, não documentada oficialmente): `https://portal.api.gupy.io/api/v1/jobs`
- Remotive: <https://github.com/remotive-com/remote-jobs-api> (exige citar a Remotive e linkar a vaga original; máx. ~4 consultas/dia)
- LinkedIn: endpoint público de vagas (sem login, sem API oficial). Os termos de uso do LinkedIn restringem scraping; use com poucas buscas, só para fins acadêmicos, e desative com `ATIVAR_LINKEDIN = False` em `config.py`
- Telegram Bot API: <https://core.telegram.org/bots/api>
