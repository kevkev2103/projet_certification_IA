"""
Script simple pour démarrer le projet avec Docker

"""
import subprocess
import sys

def main():
    print("Démarrage du projet CinApps...")
    
    try:
        # Arrêter les conteneurs s'ils existent
        subprocess.run(["docker-compose", "down"], check=False)
        
        # Construire et démarrer
        subprocess.run(["docker-compose", "up", "--build", "-d"], check=True)
        
        print("✅ Projet démarré !")
        print("📱 Streamlit: http://localhost:8501")
        print("🚀 API: http://localhost:8002")
        print("🗄️ MySQL: localhost:3306")
        
    except subprocess.CalledProcessError:
        print("❌ Erreur lors du démarrage")
        sys.exit(1)

if __name__ == "__main__":
    main()