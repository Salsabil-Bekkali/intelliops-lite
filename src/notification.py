from src.contrat import Analyse, Evenement, Notification

CANAUX = {"CRITICAL": "TEAMS", "HIGH": "SLACK", "MEDIUM": "EMAIL", "LOW": "DASHBOARD"}


def choisir_canal(niveau: str) -> str:
    if niveau not in CANAUX:
        raise ValueError(f"Niveau inconnu : {niveau}")
    return CANAUX[niveau]

def rediger(evt: Evenement, analyse: Analyse) -> str:
    return "\n".join([
        f"[{analyse.level}] Composant : {evt.component}",
        f"Evenement : {evt.message}",
        f"Explication : {analyse.explanation}",
        f"Action proposee : {analyse.action}",
        f"Sources : {', '.join(analyse.sources)}",
    ])


def notifier(evt: Evenement, analyse: Analyse, historique: list) -> Notification:
    notif = Notification(
        event_id=evt.id,
        channel=choisir_canal(analyse.level),
        recipient="equipe-ops",
        text=rediger(evt, analyse),
    )
    historique.append(notif)
    evt.status = "NOTIFIED"
    return notif