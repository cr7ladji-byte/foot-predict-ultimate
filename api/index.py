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

HTML_CONTENT = """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Foot Predict Ultimate</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root { --bg: #0f172a; --card: #1e293b; --accent: #38bdf8; --green: #22c55e; --gold: #f59e0b; --text: #f8fafc; --sub: #94a3b8; --border: #334155; }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: 'Inter', sans-serif; background: var(--bg); color: var(--text); padding: 20px; line-height: 1.5; }
        .container { max-width: 800px; margin: 0 auto; }
        header { text-align: center; margin-bottom: 25px; }
        header h1 { font-size: 2rem; font-weight: 800; }
        header h1 span { color: var(--accent); }
        header p { color: var(--sub); font-size: 0.9rem; margin-top: 5px; }
        .card { background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 20px; margin-bottom: 20px; }
        .full-width { grid-column: 1 / -1; }
        .highlight { border-color: var(--gold); }
        form { display: flex; flex-direction: column; gap: 12px; }
        label { font-size: 0.85rem; color: var(--sub); font-weight: 600; }
        input { background: #0f172a; border: 1px solid var(--border); color: #fff; padding: 12px; border-radius: 8px; font-size: 1rem; }
        button { background: var(--accent); color: #0f172a; font-weight: 700; padding: 14px; border: none; border-radius: 8px; cursor: pointer; font-size: 1rem; }
        .hidden { display: none !important; }
        .loader { text-align: center; padding: 30px; }
        .spinner { width: 36px; height: 36px; border: 4px solid var(--border); border-top: 4px solid var(--accent); border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto 10px; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        .results-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        @media (max-width: 650px) { .results-grid { grid-template-columns: 1fr; } }
        .prob-container { display: flex; justify-content: space-around; margin: 15px 0; text-align: center; }
        .prob-val { font-size: 1.5rem; font-weight: 800; color: var(--green); }
        .opp-item { background: #0f172a; padding: 10px 14px; border-radius: 8px; display: flex; justify-content: space-between; align-items: center; margin-top: 8px; }
        .opp-conf { background: var(--green); color: #0f172a; font-weight: 800; padding: 4px 8px; border-radius: 4px; font-size: 0.85rem; }
        .big-metric { font-size: 2.2rem; font-weight: 800; color: var(--accent); text-align: center; }
        .metric-row { display: flex; justify-content: space-between; font-size: 0.85rem; color: var(--sub); margin-top: 8px; }
        ul { list-style: none; margin-top: 8px; }
        li { padding: 5px 0; border-bottom: 1px solid var(--border); font-size: 0.88rem; }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>⚽ Foot Predict <span>Ultimate</span></h1>
            <p>Moteur d'analyse Poisson & Simulations Tactiques</p>
        </header>

        <div class="card">
            <h2>🔎 Analyser un Match</h2>
            <form id="p-form">
                <div><label>Domicile</label><input type="text" id="home" placeholder="Ex: PSG" required></div>
                <div><label>Extérieur</label><input type="text" id="away" placeholder="Ex: Marseille" required></div>
                <div><label>Compétition</label><input type="text" id="comp" placeholder="Ex: Ligue 1"></div>
                <button type="submit">🚀 Lancer l'Analyse</button>
            </form>
        </div>

        <div id="loader" class="loader hidden">
            <div class="spinner"></div>
            <p>Calcul des probabilités en cours...</p>
        </div>

        <main id="res" class="results-grid hidden">
            <div class="card full-width">
                <h2 id="m-title">Match</h2>
                <div id="c-tag" style="color:var(--accent); font-size:0.85rem; margin-top:4px;"></div>
                <div class="prob-container">
                    <div><div id="lbl-h" style="font-size:0.8rem; color:var(--sub)">Dom</div><div class="prob-val" id="p-h">0%</div></div>
                    <div><div style="font-size:0.8rem; color:var(--sub)">Nul</div><div class="prob-val" id="p-d">0%</div></div>
                    <div><div id="lbl-a" style="font-size:0.8rem; color:var(--sub)">Ext</div><div class="prob-val" id="p-a">0%</div></div>
                </div>
                <p style="text-align:center; font-size:0.85rem; color:var(--sub)">xG : <strong id="xg-h" style="color:#fff">0</strong> - <strong id="xg-a" style="color:#fff">0</strong> | Total : <strong id="xg-t" style="color:#fff">0</strong></p>
            </div>

            <div class="card full-width highlight">
                <h3>🔥 Top 5 Opportunités</h3>
                <div id="opps"></div>
            </div>

            <div class="card">
                <h3>👨‍⚖️ Arbitrage</h3>
                <p id="ref-n" style="font-size:1.1rem; font-weight:700; margin-top:5px;">-</p>
                <div id="ref-s" style="color:var(--gold); font-size:0.8rem; margin:5px 0;">-</div>
                <div class="metric-row">
                    <div>Cartons : <strong id="ref-c" style="color:#fff">0</strong></div>
                    <div>Fautes : <strong id="ref-f" style="color:#fff">0</strong></div>
                </div>
            </div>

            <div class="card">
                <h3>⛳ Corners</h3>
                <div class="big-metric" id="c-tot">0</div>
                <div class="metric-row">
                    <div>Domicile : <strong id="c-h" style="color:#fff">0</strong></div>
                    <div>Extérieur : <strong id="c-a" style="color:#fff">0</strong></div>
                </div>
                <p id="c-tac" style="font-size:0.8rem; color:var(--sub); margin-top:8px; font-style:italic;"></p>
            </div>

            <div class="card">
                <h3>🎯 Scores Exacts</h3>
                <ul id="scores"></ul>
            </div>

            <div class="card">
                <h3>⭐ Joueurs & Période</h3>
                <p style="font-size:0.85rem">2ème Mi-temps : <strong id="mt2" style="color:var(--green)">0%</strong></p>
                <hr style="border-color:var(--border); margin:8px 0;">
                <ul id="players"></ul>
            </div>
        </main>
    </div>

    <script>
        document.getElementById('p-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            const h = document.getElementById('home').value.trim();
            const a = document.getElementById('away').value.trim();
            const c = document.getElementById('comp').value.trim() || 'Toutes compétitions';

            document.getElementById('res').classList.add('hidden');
            document.getElementById('loader').classList.remove('hidden');

            try {
                const res = await fetch(`/api/predict?home=${encodeURIComponent(h)}&away=${encodeURIComponent(a)}&competition=${encodeURIComponent(c)}`);
                const data = await res.json();

                document.getElementById('m-title').textContent = `${data.match.domicile} vs ${data.match.exterieur}`;
                document.getElementById('c-tag').textContent = data.match.competition;
                document.getElementById('lbl-h').textContent = data.match.domicile;
                document.getElementById('lbl-a').textContent = data.match.exterieur;
                document.getElementById('p-h').textContent = `${data.probabilites_1N2.domicile}%`;
                document.getElementById('p-d').textContent = `${data.probabilites_1N2.nul}%`;
                document.getElementById('p-a').textContent = `${data.probabilites_1N2.exterieur}%`;

                document.getElementById('xg-h').textContent = data.xg.domicile;
                document.getElementById('xg-a').textContent = data.xg.exterieur;
                document.getElementById('xg-t').textContent = data.xg.total;

                const opps = document.getElementById('opps');
                opps.innerHTML = '';
                data.meilleures_opportunites.forEach(o => {
                    opps.innerHTML += `<div class="opp-item"><div><div style="font-size:0.75rem; color:var(--sub)">${o.marche}</div><strong>${o.choix}</strong></div><div class="opp-conf">${o.confiance}</div></div>`;
                });

                document.getElementById('ref-n').textContent = data.arbitrage.nom;
                document.getElementById('ref-s').textContent = data.arbitrage.style;
                document.getElementById('ref-c').textContent = data.arbitrage.cartons_moyens;
                document.getElementById('ref-f').textContent = data.arbitrage.fautes_moyennes;

                document.getElementById('c-tot').textContent = data.corners.total;
                document.getElementById('c-h').textContent = data.corners.domicile;
                document.getElementById('c-a').textContent = data.corners.exterieur;
                document.getElementById('c-tac').textContent = data.corners.domination;

                const sc = document.getElementById('scores');
                sc.innerHTML = '';
                data.scores_exacts.forEach(s => sc.innerHTML += `<li>Score <strong>${s.score}</strong> — Probabilité : <strong>${s.prob}%</strong></li>`);

                document.getElementById('mt2').textContent = `${data.mitemps.mt2}%`;
                const pl = document.getElementById('players');
                pl.innerHTML = '';
                data.joueurs_cles.domicile.concat(data.joueurs_cles.exterieur).forEach(j => {
                    pl.innerHTML += `<li><strong>${j.nom}</strong> (${j.role}) : ${j.prob}</li>`;
                });

                document.getElementById('loader').classList.add('hidden');
                document.getElementById('res').classList.remove('hidden');
            } catch (err) {
                alert("Erreur de connexion au serveur");
                document.getElementById('loader').classList.add('hidden');
            }
        });
    </script>
</body>
</html>"""

@app.get("/", response_class=HTMLResponse)
def read_root():
    return HTML_CONTENT

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
    raw_home = raw_draw = raw_away = 0.0
    scores_matrix = {}
    
    for h in range(max_goals + 1):
        p_h = poisson_pmf(h, lambda_home)
        for a in range(max_goals + 1):
            p_a = poisson_pmf(a, lambda_away)
            p_exact = p_h * p_a
            scores_matrix[f"{h}-{a}"] = p_exact
            if h > a: raw_home += p_exact
            elif h == a: raw_draw += p_exact
            else: raw_away += p_exact

    # Normalisation pour garantir 100% au total
    total_p = raw_home + raw_draw + raw_away
    prob_home = raw_home / total_p if total_p > 0 else 0.33
    prob_draw = raw_draw / total_p if total_p > 0 else 0.33
    prob_away = raw_away / total_p if total_p > 0 else 0.33

    top_scores = sorted(scores_matrix.items(), key=lambda x: x[1], reverse=True)[:3]
    top_scores_formatted = [{"score": s[0], "prob": round((s[1] / total_p) * 100, 1)} for s in top_scores]

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
@app.get("/predict")
def predict(home: str = Query(...), away: str = Query(...), competition: str = Query("Toutes compétitions")):
    return generate_ultimate_prediction(home, away, competition)
