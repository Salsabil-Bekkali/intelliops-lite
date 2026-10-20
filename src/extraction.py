import re

from src.contrat import Evenement

_SECRET_RE = re.compile(
    r"\b(password|passwd|token|secret|api_key|apikey)(\s*[=:]\s*)([^\s&,;]+)",
    re.IGNORECASE,
)

_BEARER_RE = re.compile(r"\b(Bearer\s+)([^\s&,;]+)", re.IGNORECASE)

_SEVERITES_LOG = {
    "CRITICAL": "CRITICAL",
    "FATAL": "CRITICAL",
    "ERROR": "HIGH",
    "WARN": "MEDIUM",
    "WARNING": "MEDIUM",
}


def masquer_secrets(texte: str) -> str:
    texte = _SECRET_RE.sub(r"\1\2[SECRET]", texte)
    return _BEARER_RE.sub(r"\1[SECRET]", texte)

def _id(numero: int) -> str:
    return f"EVT-{numero:05d}"


def _verifier_cles(rapport: dict, cles: tuple) -> None:
    for cle in cles:
        if cle not in rapport:
            raise ValueError(f"Cle manquante : {cle}")


def normaliser_log(ligne: str, numero: int, source: str = "DOCKER",
                   environment: str = "production") -> Evenement:
    champs = ligne.split(None, 4)
    if len(champs) < 5:
        raise ValueError("Ligne de log invalide : 5 champs minimum")
    date, heure, niveau, composant, message = champs
    return Evenement(
        id=_id(numero),
        timestamp=f"{date}T{heure}Z",
        source=source,
        component=composant,
        environment=environment,
        event_type="LOG",
        severity=_SEVERITES_LOG.get(niveau.upper(), "LOW"),
        message=masquer_secrets(message),
    )


def normaliser_scan(rapport: dict, numero: int,
                    environment: str = "production") -> Evenement:
    _verifier_cles(rapport, ("cve", "package", "severity", "date"))
    severite = str(rapport["severity"]).upper()
    if severite not in ("CRITICAL", "HIGH", "MEDIUM", "LOW"):
        severite = "LOW"
    return Evenement(
        id=_id(numero),
        timestamp=rapport["date"],
        source="TRIVY",
        component=rapport["package"],
        environment=environment,
        event_type="VULNERABILITY",
        severity=severite,
        message=f"Vulnerabilite {rapport['cve']} dans {rapport['package']}",
    )


def normaliser_pipeline(rapport: dict, numero: int,
                        environment: str = "production") -> Evenement:
    _verifier_cles(rapport, ("job", "status", "date"))
    echec = str(rapport["status"]).lower() == "failed"
    return Evenement(
        id=_id(numero),
        timestamp=rapport["date"],
        source="CI",
        component=rapport["job"],
        environment=environment,
        event_type="PIPELINE_FAILURE" if echec else "PIPELINE_OK",
        severity="HIGH" if echec else "LOW",
        message=f"Pipeline {rapport['job']} : {rapport['status']}",
    ) 