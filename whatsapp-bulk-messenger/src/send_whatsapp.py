import os
import time
import logging
from typing import List
from dotenv import load_dotenv
import pywhatkit as kit

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

def to_e164(number: str, country_code: str) -> str:
    """Normaliza a formato E.164 (+<cc><number>), sin espacios ni signos."""
    n = number.strip().replace(" ", "").replace("+", "")
    cc = country_code.strip().replace("+", "")
    if n.startswith(cc):
        return f"+{n}"
    return f"+{cc}{n}"

def parse_numbers(raw: str) -> List[str]:
    return [x.strip() for x in raw.split(",") if x.strip()]

def send_spaced_messages(numbers: List[str], message: str, cc: str, wait_between: int, dry_run: bool):
    total = len(numbers)
    for i, raw in enumerate(numbers, start=1):
        phone = to_e164(raw, cc)
        logging.info("(%d/%d) Destinatario: %s", i, total, phone)
        if dry_run:
            continue
        # Abre WhatsApp Web y envía el mensaje en la pestaña activa
        kit.sendwhatmsg_instantly(phone, message, wait_time=10, tab_close=True, close_time=2)
        if i < total:
            logging.info("Esperando %d s antes del siguiente envío...", wait_between)
            time.sleep(wait_between)

if __name__ == "__main__":
    load_dotenv()

    cc = os.getenv("COUNTRY_CODE", "591")
    raw_numbers = os.getenv("NUMBERS", "")
    message = (os.getenv("MESSAGE", "") or "").replace("\\n", "\n")
    wait_between = int(os.getenv("WAIT_BETWEEN_SECONDS", "60"))
    dry_run = os.getenv("DRY_RUN", "false").lower() in {"1", "true", "yes", "y"}

    numbers = parse_numbers(raw_numbers)

    if not numbers or not message:
        raise SystemExit("Configura NUMBERS y MESSAGE en .env (ver .env.example).")

    logging.info("Mensajes a enviar: %d | CC=%s | intervalo=%ds | dry_run=%s",
                 len(numbers), cc, wait_between, dry_run)
    logging.info("Requisito: sesión iniciada en WhatsApp Web en este navegador.")
    send_spaced_messages(numbers, message, cc, wait_between, dry_run)
    logging.info("Proceso finalizado.")
