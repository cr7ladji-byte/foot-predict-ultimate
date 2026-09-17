from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import math
import random

app = FastAPI(title="Foot Predict Ultimate API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Route pour afficher la page d'accueil (index.html)
@app.get("/", response_class=HTMLResponse)
def read_root():
    try:
        with open("public/index.html", "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return "<h1>Fichier public/index.html introuvable</h1>"

def poisson_pmf(k: int, mu: float) -> float:
    if mu <= 0:
        return 1.0 if k == 0 else 0.0
    return (math.pow(mu, k) * math.exp(-mu)) / math.factorial(k)

def generate_ultimate_prediction(home: str, away: str, competition: str):
    seed_str = f"{home.lower().strip()}_{away.lower().strip()}_{competition.lower().strip()}"
    seed_val = sum(ord(c) for c in seed_str)
    random.seed(seed_val)
    
    lambda_home = round(random.uniform(1.25, 2.45), 2)
    lambda_away = round(random.uniform(0.75, 1.85), 2)
    total_xg = round(lambda_home + lambda_away, 2)
    
    max_goals = 6
    prob_home = prob_draw = prob_away = 0.0
    scores_matrix = {}
    
    for h in range(max_goals + 1):
        p_h = poisson_pmf(h, lambda_home)
        for a in range(max_goals + 1):
            p_a = poisson_pmf(a, lambda_away)
            p_exact = p_h * p_a
            scores_matrix[f"{h}-{a}"] = p_exact
            if h > a: prob_home += p_exact
            elif h == a: prob_draw += p_exact
            else: prob_away += p_exact

    top_scores = sorted(scores_matrix.items(), key=lambda x: x[1], reverse=True)[:3]
    top_scores_formatted = [{"score": s[0], "prob": round(s[1] * 100, 1)} for s in top_scores]

    arbitres = ["Clément Turpin", "Anthony Taylor", "Szymon Marciniak", "Daniele Orsato", "Slavko Vinčić"]
    arbitre_nom = random.choice(arbitres)
    avg_cartons_ref = round(random.uniform(3.9, 5.7), 1)
    avg_fautes_ref = round(random.uniform(21.5, 27.5), 1)
    severite_ref = "Sévère (Cartons rapides)" if avg_cartons_ref >= 4.8 else "Permissif (Laisse jouer)"
    
    corners_home = round(random.uniform(4.8, 7.2), 1)
    corners_away = round(random.uniform(3.2, 5.8), 1)
    corners_total = round(corners_home + corners_away, 1)
    domination_corners = f"{home} domine largement les côtés" if corners_home > corners_away + 1.2 else "Équilibre tactique au milieu"

    fautes_totales = random.randint(22, 31)
    cartons_totaux = round((avg_cartons_ref + (fautes_totales * 0.16)) / 2, 1)

    prob_ht2 = round(random.uniform(53.0, 59.0), 1)
    prob_ht1 = round(random.uniform(24.0, 29.0), 1)

    joueurs_clefs = {
        "domicile": [
            {"nom": f"Attaquant Star ({home})", "role": "Buteur principal", "prob": f"{round(random.uniform(42, 68))}%"},
            {"nom": f"Meneur de Jeu ({home})", "role": "Passeur décisif", "prob": f"{round(random.uniform(35, 58))}%"}
        ],
        "exterieur": [
            {"nom": f"Buteur ({away})", "role": "Buteur principal", "prob": f"{round(random.uniform(30, 52))}%"},
            {"nom": f"Ailier Rapide ({away})", "role": "Passeur décisif", "prob": f"{round(random.uniform(28, 48))}%"}
        ]
    }

    opp_cartons_line = math.floor(cartons_totaux - 0.5)
    opp_corners_line = math.floor(corners_total - 0.5)
    
    opportunites = [
        {"marche": "Mi-temps", "choix": "Plus de buts en 2ème mi-temps", "confiance": f"{prob_ht2}%"},
        {"marche": "Corners", "choix": f"Plus de {opp_corners_line}.5 Corners", "confiance": "79%"},
        {"marche": "Cartons & Arbitre", "choix": f"Plus de {opp_cartons_line}.5 Cartons ({arbitre_nom})", "confiance": "76%"},
        {"marche": "Joueur Décisif", "choix": f"{joueurs_clefs['domicile'][0]['nom']} décisif", "confiance": joueurs_clefs['domicile'][0]['prob']},
        {"marche": "Résultat / Buts", "choix": f"Double chance {home}/Nul & +1.5 buts", "confiance": f"{round(prob_home*100 + prob_draw*50)}%"}
    ]

    return {
        "match": {"domicile": home, "exterieur": away, "competition": competition},
        "xg": {"domicile": lambda_home, "exterieur": lambda_away, "total": total_xg},
        "probabilites_1N2": {
            "domicile": round(prob_home * 100, 1),
            "nul": round(prob_draw * 100, 1),
            "exterieur": round(prob_away * 100, 1)
        },
        "scores_exacts": top_scores_formatted,
        "arbitrage": {
            "nom": arbitre_nom,
            "style": severite_ref,
            "cartons_moyens": avg_cartons_ref,
            "fautes_moyennes": avg_fautes_ref
        },
        "corners": {
            "total": corners_total,
            "domicile": corners_home,
            "exterieur": corners_away,
            "domination": domination_corners
        },
        "mitemps": {"mt1": prob_ht1, "mt2": prob_ht2},
        "joueurs_cles": joueurs_clefs,
        "meilleures_opportunites": opportunites
    }

@app.get("/api/predict")
def predict(home: str = Query(...), away: str = Query(...), competition: str = Query("Toutes compétitions")):
    return generate_ultimate_prediction(home, away, competition)
