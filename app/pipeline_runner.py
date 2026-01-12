# app/pipeline_runner.py

import json
import subprocess
from datetime import datetime
from pathlib import Path

from domain.services.sentiment_analyzer import FinBERTSentimentAnalyzer
from domain.services.aggregator import SentimentAggregator
from domain.entities.article import Article
from infrastructure.database.repository import DatabaseRepository

class ContinuousPipelineRunner:
    """
    Orchestrateur de pipeline en temps réel.
    
    Exécute en boucle :
    1. Scraping (nouveau articles)
    2. Analyse sentiment
    3. Sauvegarde DB
    4. Mise à jour historique
    
    Architecture Pipeline.
    """
    
    def __init__(
        self,
        scrapy_project_path: str = "infrastructure/datasources/cnbc_scraper",
        spider_name: str = "cnbc",
        output_dir: str = "outputs",
    ):
        # Résolution des chemins absolus depuis la racine du projet
        self.project_root = Path(__file__).parent.parent.resolve()
        self.scrapy_project_path = (self.project_root / scrapy_project_path).resolve()
        self.spider_name = spider_name
        self.output_dir = (self.project_root / output_dir).resolve()
        
        # Vérification que le dossier Scrapy existe
        if not self.scrapy_project_path.exists():
            raise FileNotFoundError(
                f"Le dossier Scrapy n'existe pas : {self.scrapy_project_path}"
            )
        
        # Vérification de scrapy.cfg
        scrapy_cfg = self.scrapy_project_path / "scrapy.cfg"
        if not scrapy_cfg.exists():
            raise FileNotFoundError(
                f"scrapy.cfg introuvable dans {self.scrapy_project_path}"
            )
        
        # Services métier
        self.sentiment_analyzer = FinBERTSentimentAnalyzer()
        self.aggregator = SentimentAggregator()
        self.db_repository = DatabaseRepository()
        
        # Création du dossier outputs
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.trend_history_path = self.output_dir / "trend_history.json"
        self._ensure_trend_history_exists()
        
        print(f"[INIT] Dossier Scrapy : {self.scrapy_project_path}")
        print(f"[INIT] Dossier output : {self.output_dir}")
    
    def _ensure_trend_history_exists(self):
        """Crée le fichier d'historique s'il n'existe pas."""
        if not self.trend_history_path.exists():
            with open(self.trend_history_path, 'w', encoding='utf-8') as f:
                json.dump([], f, indent=4)
    
    def _run_single_cycle(self, cycle_number: int, timestamp: str):
        """Exécute un seul cycle du pipeline."""
        # Fichiers pour ce cycle
        temp_raw_file = self.output_dir / f"temp_scraping_{cycle_number}.json"
        scraped_archive = self.output_dir / "scraped_articles_archive.json"
        
        # ÉTAPE 1 : SCRAPING
        print("[1/4] Scraping des nouveaux articles...")
        new_articles_raw = self._run_scraping(temp_raw_file)
        
        if not new_articles_raw:
            print("Aucun nouvel article trouvé")
            if temp_raw_file.exists():
                temp_raw_file.unlink()
            return
        
        print(f" {len(new_articles_raw)} articles récupérés")
        
        # Sauvegarde des articles bruts dans l'archive JSON
        self._save_scraped_articles_to_archive(new_articles_raw, scraped_archive, timestamp)
        
        # ÉTAPE 2 : ANALYSE SENTIMENT
        print("\n[2/4] Analyse de sentiment (FinBERT)...")
        analyzed_articles = self._analyze_articles(new_articles_raw)
        print(f" {len(analyzed_articles)} articles analysés")
        
        # ÉTAPE 3 : SAUVEGARDE EN BASE
        print("\n[3/4] Sauvegarde dans la base de données...")
        added_count = self._save_to_database(analyzed_articles)
        print(f" {added_count} nouveaux articles ajoutés")
        
        # ÉTAPE 4 : MISE À JOUR HISTORIQUE
        print("\n[4/4] Mise à jour de l'historique des tendances...")
        self._update_trend_history(analyzed_articles, timestamp)
        print(" Historique mis à jour")
        
        # Nettoyage
        if temp_raw_file.exists():
            temp_raw_file.unlink()
            
    def run_once(self):
        """
        Lance UN SEUL cycle de scraping (Mode Manuel).
        Utilisé par le bouton 'Rafraîchir' de l'interface.
        """
        print("DÉMARRAGE DU SCRAPING MANUEL")
        
        start_time = datetime.now()
        timestamp = start_time.strftime("%Y-%m-%d %H:%M:%S")
        
        try:
            # On appelle la méthode qui fait tout le travail
            # On met '1' comme numéro de cycle par défaut
            self._run_single_cycle(1, timestamp)
            print("\n Scraping manuel terminé avec succès.")
            
        except Exception as e:
            print(f"\n Erreur critique durant le scraping manuel : {e}")
            raise e # On remonte l'erreur pour le debugging
    
    def _run_scraping(self, output_file: Path) -> list:
        """
        Exécute le spider Scrapy.
        
        Returns:
            Liste de dictionnaires (articles bruts)
        """
        try:
            # Construction de la commande Scrapy
            # Utilisation du chemin absolu pour le fichier de sortie
            cmd = [
                "scrapy", "crawl", self.spider_name, 
                "-O", str(output_file.resolve())
            ]
            
            print(f"   Commande : {' '.join(cmd)}")
            print(f"   Dossier de travail : {self.scrapy_project_path}")
            print(f"   Fichier de sortie : {output_file}")
            
            # Exécution depuis le dossier du projet Scrapy
            result = subprocess.run(
                cmd,
                cwd=str(self.scrapy_project_path),
                capture_output=True,
                text=True,
                check=False  # Ne pas lever d'exception, on gère manuellement
            )
            
            # Affichage des logs Scrapy
            if result.stdout:
                print(f"\n   STDOUT Scrapy :")
                print("   " + "\n   ".join(result.stdout.split('\n')[-10:]))  # 10 dernières lignes
            
            if result.stderr:
                print(f"\n   STDERR Scrapy :")
                print("   " + "\n   ".join(result.stderr.split('\n')[-10:]))
            
            # Vérification du code retour
            if result.returncode != 0:
                print(f" Scrapy s'est terminé avec le code {result.returncode}")
            
            # Lecture du fichier généré
            if output_file.exists() and output_file.stat().st_size > 5:
                with open(output_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                # Vérification que c'est bien une liste
                if isinstance(data, list):
                    return data
                else:
                    print(f" Format JSON invalide (attendu: liste)")
                    return []
            else:
                print(f" Fichier de sortie vide ou inexistant")
                return []
            
        except subprocess.CalledProcessError as e:
            print(f"   ✗ Erreur Scrapy : {e}")
            print(f"   STDERR : {e.stderr}")
        except json.JSONDecodeError as e:
            print(f"   ✗ Erreur parsing JSON : {e}")
        except Exception as e:
            print(f"   ✗ Erreur inattendue : {e}")
            import traceback
            traceback.print_exc()

        return []
    
    def _analyze_articles(self, raw_articles: list) -> list:
        """
        Analyse le sentiment des articles.
        
        Args:
            raw_articles: Liste de dictionnaires bruts
        
        Returns:
            Liste d'objets Article analysés
        """
        # Conversion dict → Article
        articles = [Article.from_dict(raw) for raw in raw_articles]
        
        # Analyse de sentiment
        analyzed_articles = self.sentiment_analyzer.analyze_batch(articles)
        
        return analyzed_articles
    
    def _save_to_database(self, articles: list) -> int:
        """Sauvegarde les articles et retourne le nombre de VRAIS ajouts."""
        print("\nSauvegarde dans la base de données...")
        
        added_count = 0
        for article in articles:
            try:
                article_dict = article.to_dict()
                # On incrémente SEULEMENT si la DB retourne True (Nouveau)
                is_new = self.db_repository.save_article(article_dict)
                if is_new:
                    added_count += 1
            except Exception as e:
                print(f"Erreur sauvegarde article : {e}")
        
        if added_count > 0:
            print(f" {added_count} nouveaux articles ajoutés (Doublons ignorés)")
        else:
            print(f" Aucune nouveauté (tous les articles existent déjà)")
            
        return added_count
    
    def _update_trend_history(self, articles: list, timestamp: str):
        """
        Met à jour l'historique des tendances.
        
        Args:
            articles: Articles analysés de ce cycle
            timestamp: Horodatage du cycle
        """
        # Agrégation des sentiments par entreprise
        company_scores = self.aggregator.aggregate_by_company(articles)
        
        print(f"   Scores actuels :")
        for company, score in company_scores.items():
            print(f"      - {company} : {score:+.3f}")
        
        # Ajout à l'historique
        trend_entry = {
            "timestamp": timestamp,
            "scores": company_scores
        }
        
        # Lecture de l'historique existant
        try:
            with open(self.trend_history_path, 'r', encoding='utf-8') as f:
                history = json.load(f)
        except:
            history = []
        
        history.append(trend_entry)
        
        # Sauvegarde
        with open(self.trend_history_path, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=4, ensure_ascii=False)
    
    def _save_scraped_articles_to_archive(self, articles: list, archive_path: Path, timestamp: str):
        """
        Sauvegarde les articles scrapés dans un fichier JSON d'archive.
        
        Args:
            articles: Liste des articles scrapés (bruts)
            archive_path: Chemin du fichier d'archive JSON
            timestamp: Horodatage du scraping
        """
        # Structure de l'entrée d'archive
        archive_entry = {
            "timestamp": timestamp,
            "count": len(articles),
            "articles": articles
        }
        
        # Lecture de l'archive existante
        if archive_path.exists():
            try:
                with open(archive_path, 'r', encoding='utf-8') as f:
                    archive_data = json.load(f)
            except:
                archive_data = []
        else:
            archive_data = []
        
        # Ajout de la nouvelle entrée
        archive_data.append(archive_entry)
        
        # Sauvegarde de l'archive mise à jour
        with open(archive_path, 'w', encoding='utf-8') as f:
            json.dump(archive_data, f, indent=4, ensure_ascii=False)
        
        print(f" Articles archivés dans {archive_path.name}")


def main():
    """Point d'entrée du pipeline continu."""
    runner = ContinuousPipelineRunner(
        scrapy_project_path="infrastructure/datasources/cnbc_scraper",
        spider_name="cnbc",
        output_dir="outputs",
    )
    
    runner.run_continuous()


if __name__ == "__main__":
    main()