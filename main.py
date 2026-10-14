"""Radar de vagas front-end: coleta -> filtra -> remove já vistas -> notifica."""
import argparse
import logging

import notificador
import storage
from config import BUSCAS
from filtros import filtrar
from scraper import buscar_gupy, buscar_remotive

log = logging.getLogger("radar")


def main() -> None:
    parser = argparse.ArgumentParser(description="Radar de vagas front-end")
    parser.add_argument("--dry-run", action="store_true",
                        help="mostra as vagas no terminal sem enviar nem gravar histórico")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    coletadas = []
    for termo in BUSCAS:
        log.info("Buscando '%s' na Gupy...", termo)
        coletadas += buscar_gupy(termo)
    log.info("Buscando vagas remotas na Remotive...")
    coletadas += buscar_remotive()

    candidatas = filtrar(coletadas)
    novas = storage.filtrar_novas(candidatas)
    log.info("%d coletadas | %d após filtros | %d novas", len(coletadas), len(candidatas), len(novas))

    if not novas:
        log.info("Nada de novo por aqui.")
        return

    if args.dry_run or not notificador.telegram_configurado():
        if not args.dry_run:
            log.warning("Telegram não configurado (.env); exibindo no terminal.")
        for v in novas:
            print(f"- {v.titulo} | {v.empresa} | {v.local} | {v.url}")
        return

    if notificador.enviar_telegram(novas):
        storage.registrar(novas)  # só marca como vista se o envio deu certo
        log.info("%d vagas enviadas.", len(novas))


if __name__ == "__main__":
    main()
