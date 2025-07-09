#!/usr/bin/env python3
"""
Script pour générer un hash correct pour l'utilisateur testuser
"""

from app.security import generate_test_user_hash

if __name__ == "__main__":
    print("🔐 Génération du hash pour l'utilisateur testuser...")
    hash_value = generate_test_user_hash()
    print("\n📋 Copiez ce hash dans votre fichier mysql-init/init_bdd_app.sql :")
    print(f"'{hash_value}'")
    print("\n💡 Ou exécutez cette requête SQL :")
    print(f"UPDATE main_user SET password = '{hash_value}' WHERE username = 'testuser';") 