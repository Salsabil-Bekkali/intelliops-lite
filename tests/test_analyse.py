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