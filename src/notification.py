from src.contrat import Analyse, Evenement, Notification

CANAUX = {"CRITICAL": "TEAMS", "HIGH": "SLACK", "MEDIUM": "EMAIL", "LOW": "DASHBOARD"}


def choisir_canal(niveau: str) -> str:
    if niveau not in CANAUX:
        raise ValueError(f"Niveau inconnu : {niveau}")
    return CANAUX[niveau]