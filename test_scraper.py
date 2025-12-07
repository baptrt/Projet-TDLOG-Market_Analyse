import unittest
import os
import json

class TestScrapingResult(unittest.TestCase):
    """
    Ce test vérifie automatiquement la qualité des données récupérées par le Scraper.
    Il simule un "audit" du fichier news.json.
    """

    def setUp(self):
        # Cette fonction s'exécute avant chaque test.
        self.filename = "news.json"

    def test_1_existence_fichier(self):
        """Le fichier de sortie existe-t-il ?"""
        existe = os.path.exists(self.filename)
        self.assertTrue(existe, f"ERREUR CRITIQUE : Le fichier {self.filename} est introuvable. Le scraper a-t-il tourné ?")

    def test_2_donnees_non_vides(self):
        """Le fichier contient-il bien des articles ?"""
        if not os.path.exists(self.filename):
            self.skipTest("Fichier absent")

        with open(self.filename, 'r', encoding='utf-8', errors='ignore') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                self.fail("Le fichier news.json n'est pas un JSON valide (il est peut-être corrompu).")

        self.assertIsInstance(data, list, "Le format attendu est une liste d'articles.")
        self.assertGreater(len(data), 0, "ÉCHEC : Le scraper a tourné mais n'a trouvé AUCUN article (liste vide).")
        print(f"\n[INFO] Audit de {len(data)} articles récupérés.")

    def test_3_qualite_des_champs(self):
        """Chaque article a-t-il les informations obligatoires (Titre, Lien, Contenu) ?"""
        if not os.path.exists(self.filename):
            self.skipTest("Fichier absent")

        with open(self.filename, 'r', encoding='utf-8', errors='ignore') as f:
            data = json.load(f)

        # On teste les 5 premiers articles pour être sûr
        for index, article in enumerate(data[:5]):
            # 1. Vérifier le titre
            self.assertIn("title", article, f"Article {index} sans titre")
            self.assertIsNotNone(article["title"], f"Le titre de l'article {index} est 'None'")
            self.assertNotEqual(article["title"].strip(), "", f"Le titre de l'article {index} est vide")

            # 2. Vérifier l'entreprise (TSLA ou AAPL)
            self.assertIn("company", article)
            self.assertIn(article["company"], ["TSLA", "AAPL"], f"Entreprise inconnue : {article['company']}")

            # 3. Vérifier qu'on a bien récupéré du texte (c'est le but du projet !)
            self.assertIn("full_text", article)
            text_length = len(article.get("full_text", ""))
            self.assertGreater(text_length, 50, f"L'article {index} a un contenu trop court ({text_length} caractères). Scraping incomplet ?")

    def test_4_format_date(self):
        """La date est-elle présente ? (Important pour la prévision J+1)"""
        with open(self.filename, 'r', encoding='utf-8', errors='ignore') as f:
            data = json.load(f)
        
        article = data[0]
        self.assertIn("time", article)
        # On ne force pas le test sur le contenu exact de la date car elle peut être None selon Yahoo
        if article["time"] is None:
            print("\n[WARN] Attention : Certaines dates n'ont pas pu être récupérées (Yahoo API).")

if __name__ == '__main__':
    print("DEMARRAGE DES TESTS DU SCRAPER...")
    unittest.main()