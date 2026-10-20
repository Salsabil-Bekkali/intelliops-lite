import unittest
from src.contrat import Analyse, Evenement
from src.notification import (choisir_canal, notifier, rediger,
                              tracer_decision, valider_action)


def exemple(sensible=True, niveau="CRITICAL"):
    e = Evenement("EVT-00125", "2026-10-05T10:02:11Z", "DOCKER", "backend",
                  "production", "LOG", "HIGH", "OOMKilled restarts=14")
    a = Analyse("EVT-00125", niveau, "Manque de memoire",
                "Redemarrer le service backend", sensible, ["DOCKER"])
    return e, a


class TestNotification(unittest.TestCase):
    def test_canaux(self):
        self.assertEqual(choisir_canal("CRITICAL"), "TEAMS")
        self.assertEqual(choisir_canal("HIGH"), "SLACK")
        self.assertEqual(choisir_canal("MEDIUM"), "EMAIL")
        self.assertEqual(choisir_canal("LOW"), "DASHBOARD")

    def test_canal_invalide(self):
        with self.assertRaises(ValueError):
            choisir_canal("INCONNU")

    def test_rediger(self):
        e, a = exemple()
        lignes = rediger(e, a).split("\n")
        self.assertEqual(len(lignes), 5)
        self.assertEqual(lignes[0], "[CRITICAL] Composant : backend")
        self.assertEqual(lignes[1], "Evenement : OOMKilled restarts=14")
        self.assertEqual(lignes[2], "Explication : Manque de memoire")
        self.assertEqual(lignes[3], "Action proposee : Redemarrer le service backend")
        self.assertEqual(lignes[4], "Sources : DOCKER")

    def test_rediger_plusieurs_sources(self):
        e, a = exemple()
        a.sources = ["DOCKER", "CI"]
        self.assertTrue(rediger(e, a).endswith("Sources : DOCKER, CI"))

    def test_notifier(self):
        e, a = exemple()
        hist = []
        n = notifier(e, a, hist)
        self.assertEqual(n.channel, "TEAMS")
        self.assertEqual(n.recipient, "equipe-ops")
        self.assertEqual(n.event_id, "EVT-00125")
        self.assertEqual(hist, [n])
        self.assertEqual(e.status, "NOTIFIED")

    def test_validation(self):
        _, a = exemple()
        self.assertTrue(valider_action(a, " OUI "))
        self.assertTrue(valider_action(a, "o"))
        self.assertFalse(valider_action(a, "n"))

    def test_validation_non_sensible(self):
        _, a = exemple(sensible=False)
        self.assertTrue(valider_action(a, "n"))

    def test_tracer_decision(self):
        _, a = exemple()
        journal = []
        r = tracer_decision(a, True, "ops-oncall", journal, "2026-10-05T10:10:00Z")
        self.assertEqual(journal, [r])
        self.assertEqual(r, {
            "event_id": "EVT-00125",
            "action": "Redemarrer le service backend",
            "approved": True,
            "actor": "ops-oncall",
            "timestamp": "2026-10-05T10:10:00Z",
        })


if __name__ == "__main__":
    unittest.main()