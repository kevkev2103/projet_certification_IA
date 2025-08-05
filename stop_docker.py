"""
Script simple pour arrêter le projet Docker
Niveau junior - pas de fioritures
"""
import subprocess

def main():
    print("Arrêt du projet CinApps...")
    
    try:
        # Arrêter tous les conteneurs
        subprocess.run(["docker-compose", "down"], check=True)
        print("✅ Projet arrêté !")
        
    except subprocess.CalledProcessError:
        print("❌ Erreur lors de l'arrêt")

if __name__ == "__main__":
    main()