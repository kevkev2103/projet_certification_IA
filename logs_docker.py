"""
Script simple pour voir les logs Docker
Niveau junior - pas de fioritures
"""
import subprocess
import sys

def main():
    if len(sys.argv) > 1:
        service = sys.argv[1]
        print(f"Logs du service {service}...")
        subprocess.run(["docker-compose", "logs", "-f", service])
    else:
        print("Logs de tous les services...")
        subprocess.run(["docker-compose", "logs", "-f"])

if __name__ == "__main__":
    main()