from flask import Flask, request
import requests

app = Flask(__name__)

# ATTENTION : secret factice à des fins de démonstration (détection par Gitleaks)
# Ceci n'est PAS un vrai identifiant AWS - format d'exemple officiel AWS, sans valeur réelle
AWS_ACCESS_KEY = "AKIAIOSFODNN7EXAMPLE"

@app.route("/")
def home():
    return "Hello from the DevSecOps demo app!"

@app.route("/status")
def status():
    return {"status": "ok"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
