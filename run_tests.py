"""
Exécute AUTOMATIQUEMENT l'ensemble des tests du projet en une seule commande

Ce script :
  1. Lance tous les tests unitaires (logique métier pure)
  2. Lance tous les tests d'intégration (services + mocks partiels)
  3. Lance tous les tests fonctionnels (scénarios complets)
  4. Lance les tests CRUD réels (base de données physique)
  5. Génère un rapport synthétique (succès/échec)

=============================================================================
USAGE
=============================================================================
Commande :
    python run_tests.py

Output attendu :
    🚀 Lancement des tests UNITAIRES...
    ................................................................
    Ran *** tests in ***s
    
    OK
    
    🚀 Lancement des tests INTÉGRATION...
    ....
    Ran *** tests in ***s
    
    OK
    
    ... (suite) ...
    
    ============================================================
    ✅ TOUS LES TESTS ONT RÉUSSI — SYSTÈME PRÊT POUR DÉMO
    ============================================================

=============================================================================
SORTIES ET CODES DE RETOUR
=============================================================================
- Code 0 : Tous les tests ont réussi (OK pour démo)
- Code 1 : Un ou plusieurs tests ont échoué (NE PAS DÉMO)

=============================================================================
PRÉREQUIS
=============================================================================
- Fichier .env présent et configuré correctement
- Base de données MySQL accessible
- Tous les modules requirements.txt installés
"""

import unittest
import sys
import os
from datetime import datetime


def print_separator(title=None):
    """
    Affiche une ligne de séparation visuelle pour améliorer la lisibilité du rapport.
    
    Args:
        title (str, optional): Texte centré sur la ligne. Si None, affiche juste des '='.
    """
    if title:
        separator = "=" * 60
        print(f"\n{separator}")
        print(f" {title}")
        print(separator)
    else:
        print("-" * 60)


def run_test_suite(display_name, discover_path, pattern="test_*.py"):
    """
    Exécute une suite de tests spécifique et retourne le résultat.
    
    Args:
        display_name (str): Nom affiché pour cette catégorie de tests
                            (ex: "UNITAIRES", "INTÉGRATION")
        discover_path (str): Chemin relatif du dossier contenant les tests
        pattern (str): Pattern de nommage des fichiers de tests (par défaut: test_*.py)
    
    Returns:
        unittest.TestResult: Objet contenant le résultat de l'exécution
                            (nombre de tests, erreurs, échecs, succès)
    
    Note:
        Cette méthode utilise unittest.discover pour charger automatiquement
        tous les fichiers de test correspondant au pattern dans le dossier spécifié.
    """
    print_separator(f"🚀 Lancement des tests {display_name}...")
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    try:
        # Discovery automatique des tests
        discovered_tests = loader.discover(
            start_dir=discover_path,
            pattern=pattern,
            top_level_dir="."
        )
        suite.addTests(discovered_tests)
        
        # Exécution avec verbosité moyenne (affiche chaque test)
        runner = unittest.TextTestRunner(verbosity=1)
        result = runner.run(suite)
        
        # Statistiques
        test_count = result.testsRun
        error_count = len(result.errors)
        fail_count = len(result.failures)
        
        print(f"\n📊 Résultats {display_name}:")
        print(f"   • Tests exécutés : {test_count}")
        print(f"   • Succès : {test_count - error_count - fail_count}")
        print(f"   • Erreurs : {error_count}")
        print(f"   • Échecs : {fail_count}")
        
        return result
        
    except Exception as e:
        print(f"❌ ERREUR CRITIQUE dans {display_name}: {e}")
        # Retourner un résultat "vide" mais échoué
        return unittest.TestResult()


def main():
    """
    Orchestre l'exécution de TOUS les tests dans l'ordre :
      1. Tests unitaires (rapides, sans DB)
      2. Tests d'intégration (avec mocks partiels)
      3. Tests fonctionnels (scénarios complets)
    
    À la fin, génère un rapport synthétique et exit avec code approprié.
    
    Exit Codes:
        0 : Tous les tests ont réussi
        1 : Un ou plusieurs tests ont échoué
    """
    print("\n" + "=" * 60)
    print("🧪 EPIC EVENTS CRM - TESTS AUTOMATISÉS")
    print(f"📅 Date d'exécution : {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 60)
    
    # Initialisation des compteurs globaux
    total_errors = 0
    total_failures = 0
    total_tests = 0
    
    # ------------------------------------------------------------------------
    # ÉTAPE 1 : Tests Unitaires (Logique métier pure - MOCKS)
    # ------------------------------------------------------------------------
    print_separator("PHASE 1 / 3 : TESTS UNITAIRES")
    print("(Logique métier, modèles, hashage - Sans connexion DB)\n")
    
    result_unit = run_test_suite(
        display_name="UNITAIRES",
        discover_path="tests/unittests"
    )
    
    total_tests += result_unit.testsRun
    total_errors += len(result_unit.errors)
    total_failures += len(result_unit.failures)
    
    if result_unit.wasSuccessful():
        print("✅ Tests unitaires : VERT")
    else:
        print("❌ Tests unitaires : ERREURS DETECTÉES")
    
    print()
    
    # ------------------------------------------------------------------------
    # ÉTAPE 2 : Tests d'Intégration (Services + Mocks partiels)
    # ------------------------------------------------------------------------
    print_separator("PHASE 2 / 3 : TESTS D'INTÉGRATION")
    print("(Interaction services, UserManager - Mocks DB partiels)\n")
    
    result_integration = run_test_suite(
        display_name="INTÉGRATION",
        discover_path="tests/integrationtests"
    )
    
    total_tests += result_integration.testsRun
    total_errors += len(result_integration.errors)
    total_failures += len(result_integration.failures)
    
    if result_integration.wasSuccessful():
        print("✅ Tests d'intégration : VERT")
    else:
        print("❌ Tests d'intégration : ERREURS DETECTÉES")
    
    print()
    
    # ------------------------------------------------------------------------
    # ÉTAPE 3 : Tests Fonctionnels (Scénarios complets + CRUD réel)
    # ------------------------------------------------------------------------
    print_separator("PHASE 3 / 3 : TESTS FONCTIONNELS")
    print("(Scénarios complets + Tests CRUD réels sur base MySQL)\n")
    
    result_functional = run_test_suite(
        display_name="FONCTIONNELS",
        discover_path="tests/functionaltests"
    )
    
    total_tests += result_functional.testsRun
    total_errors += len(result_functional.errors)
    total_failures += len(result_functional.failures)
    
    if result_functional.wasSuccessful():
        print("✅ Tests fonctionnels : VERT")
    else:
        print("❌ Tests fonctionnels : ERREURS DETECTÉES")
    
    print()
    
    # ------------------------------------------------------------------------
    # RAPPORT SYNTHÉTIQUE FINAL
    # ------------------------------------------------------------------------
    print_separator("📋 RAPPORT SYNTHÉTIQUE FINAL")
    
    print(f"""
Total cumulé :
   • Tests exécutés : {total_tests}
   • Succès : {total_tests - total_errors - total_failures}
   • Erreurs : {total_errors}
   • Échecs : {total_failures}

Durée estimée totale : ~2 minutes
""")
    
    # Bannière de verdict FINAL
    if total_errors == 0 and total_failures == 0:
        print("=" * 60)
        print("✅ TOUS LES TESTS ONT RÉUSSI ✅")
        print("=" * 60)
        sys.exit(0)
    else:
        print("=" * 60)
        print("❌ ERREURS DÉTECTÉES ❌")
        print(f"   Corrections nécessaires : {total_errors} erreurs, {total_failures} échecs")
        print("=" * 60)
        sys.exit(1)


if __name__ == '__main__':
    """
    Point d'entrée lorsque ce fichier est lancé directement.    
    Usage :
        python run_tests.py
    """
    main()