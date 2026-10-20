import unittest
from src.analyse import analyser, chercher_procedures, classifier, compter_erreurs, est_doublon
from src.contrat import PROCEDURES, Evenement


def evt(type_="LOG", severity="HIGH", message="OOMKilled restarts=14",
        composant="backend"):
    return Evenement("EVT-00001", "2026-10-05T10:00:00Z", "DOCKER", composant,
                     "production", type_, severity, message)


class TestAnalyse(unittest.TestCase):

    # --- fournis par le sujet ---
    def test_doublon(self):
        vus = set()
        self.assertFalse(est_doublon(evt(), vus))
        self.assertTrue(est_doublon(evt(), vus))

    def test_classifier_boucle(self):
        e = evt()
        self.assertEqual(classifier(e, 3), "CRITICAL")
        self.assertEqual(classifier(e, 2), "HIGH")

    # --- commit 6 : doublons et comptage ---
    def test_doublon_secondes_differentes(self):
        vus = set()
        e1 = Evenement("EVT-00001", "2026-10-05T10:00:00Z", "DOCKER", "backend",
                       "production", "LOG", "HIGH", "OOMKilled")
        e2 = Evenement("EVT-00002", "2026-10-05T10:00:01Z", "DOCKER", "backend",
                       "production", "LOG", "HIGH", "OOMKilled")
        self.assertFalse(est_doublon(e1, vus))
        self.assertFalse(est_doublon(e2, vus))

    def test_compter_erreurs_high(self):
        compteur = {}
        self.assertEqual(compter_erreurs(evt(), compteur), 1)
        self.assertEqual(compter_erreurs(evt(), compteur), 2)

    def test_compter_erreurs_critical(self):
        compteur = {}
        self.assertEqual(compter_erreurs(evt(severity="CRITICAL"), compteur), 1)

    def test_compter_erreurs_low(self):
        compteur = {}
        self.assertEqual(compter_erreurs(evt(severity="LOW"), compteur), 0)
        self.assertEqual(compteur, {})

    def test_compter_erreurs_non_log(self):
        compteur = {}
        self.assertEqual(compter_erreurs(evt(type_="PIPELINE_FAILURE"), compteur), 0)
        self.assertEqual(compteur, {})

    def test_compter_erreurs_composants_separes(self):
        compteur = {}
        compter_erreurs(evt(composant="backend"), compteur)
        compter_erreurs(evt(composant="frontend"), compteur)
        self.assertEqual(compteur, {"backend": 1, "frontend": 1})

    # --- commit 7 : procedures et analyse ---
    def test_chercher_procedures_trouvee(self):
        res = chercher_procedures(evt(message="OOMKilled restarts=14"), PROCEDURES)
        self.assertEqual(res, [PROCEDURES["oomkilled"]])

    def test_chercher_procedures_aucune(self):
        self.assertEqual(chercher_procedures(evt(message="Service demarre"), PROCEDURES), [])

    def test_analyser_cause_inconnue(self):
        a = analyser(evt(severity="LOW", message="Service demarre"), PROCEDURES)
        self.assertEqual(a.explanation, "Cause inconnue : analyse manuelle requise")
        self.assertEqual(a.action, "Surveiller")
        self.assertFalse(a.sensitive)

    def test_analyser_critical(self):
        e = evt()
        a = analyser(e, PROCEDURES, 3)
        self.assertEqual(a.level, "CRITICAL")
        self.assertEqual(a.action, "Redemarrer le service backend")
        self.assertTrue(a.sensitive)
        self.assertEqual(e.status, "ANALYZED")
        self.assertEqual(a.sources, ["DOCKER"])

    def test_analyser_vulnerabilite(self):
        a = analyser(evt(type_="VULNERABILITY", severity="CRITICAL",
                         message="Vulnerabilite CVE-1 dans lib-xyz",
                         composant="lib-xyz"), PROCEDURES)
        self.assertEqual(a.action, "Mettre a jour la dependance lib-xyz")

    def test_analyser_pipeline(self):
        a = analyser(evt(type_="PIPELINE_FAILURE", message="Pipeline build : failed",
                         composant="build"), PROCEDURES)
        self.assertEqual(a.action, "Relancer le pipeline build")


if __name__ == "__main__":
    unittest.main()