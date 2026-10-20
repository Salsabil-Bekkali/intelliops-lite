from src.contrat import Analyse, Evenement


def est_doublon(evt, vus):
    cle = (evt.timestamp, evt.source, evt.component, evt.event_type, evt.message)
    if cle in vus:
        return True
    vus.add(cle)
    return False

def compter_erreurs(evt, compteur):
    if evt.event_type == "LOG" and evt.severity in ("HIGH", "CRITICAL"):
        compteur[evt.component] = compteur.get(evt.component, 0) + 1
        return compteur[evt.component]
    return 0


def chercher_procedures(evt, base):
    msg = evt.message.lower()
    return [proc for mot, proc in base.items() if mot.lower() in msg]


def classifier(evt, nb_erreurs=0):
    if nb_erreurs >= 3:
        return "CRITICAL"
    return evt.severity


def analyser(evt: Evenement, base: dict, nb_erreurs: int = 0) -> Analyse:
    raise NotImplementedError