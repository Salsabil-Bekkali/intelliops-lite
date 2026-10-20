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

def valider_action(analyse: Analyse, reponse: str) -> bool:
    if not analyse.sensitive:
        return True
    return reponse.strip().lower() in ("o", "oui", "ok", "yes")


def tracer_decision(analyse: Analyse, approuve: bool, acteur: str,
                    journal: list, horodatage: str) -> dict:
    entree = {
        "event_id": analyse.event_id,
        "action": analyse.action,
        "approved": approuve,
        "actor": acteur,
        "timestamp": horodatage,
    }
    journal.append(entree)
    return entree