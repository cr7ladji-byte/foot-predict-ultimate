document.getElementById('predict-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const home = document.getElementById('home-team').value.trim();
    const away = document.getElementById('away-team').value.trim();
    const competition = document.getElementById('competition').value.trim() || 'Toutes compétitions';

    if (!home || !away) return;

    // Masquer les anciens résultats et afficher le chargement
    document.getElementById('results-area').classList.add('hidden');
    document.getElementById('loader').classList.remove('hidden');

    try {
        const response = await fetch(`/api/predict?home=${encodeURIComponent(home)}&away=${encodeURIComponent(away)}&competition=${encodeURIComponent(competition)}`);
        const data = await response.json();

        // 1. En-tête et probabilités
        document.getElementById('match-title').textContent = `${data.match.domicile} vs ${data.match.exterieur}`;
        document.getElementById('competition-tag').textContent = data.match.competition;
        
        document.getElementById('label-home').textContent = data.match.domicile;
        document.getElementById('prob-home').textContent = `${data.probabilites_1N2.domicile}%`;
        document.getElementById('prob-draw').textContent = `${data.probabilites_1N2.nul}%`;
        document.getElementById('label-away').textContent = data.match.exterieur;
        document.getElementById('prob-away').textContent = `${data.probabilites_1N2.exterieur}%`;

        document.getElementById('xg-home').textContent = data.xg.domicile;
        document.getElementById('xg-away').textContent = data.xg.exterieur;
        document.getElementById('xg-total').textContent = data.xg.total;

        // 2. Opportunités
        const oppContainer = document.getElementById('opportunities-list');
        oppContainer.innerHTML = '';
        data.meilleures_opportunites.forEach(opp => {
            oppContainer.innerHTML += `
                <div class="opp-item">
                    <div>
                        <div class="opp-market">${opp.marche}</div>
                        <div class="opp-choice">${opp.choix}</div>
                    </div>
                    <div class="opp-conf">${opp.confiance}</div>
                </div>
            `;
        });

        // 3. Arbitrage
        document.getElementById('ref-name').textContent = data.arbitrage.nom;
        document.getElementById('ref-style').textContent = data.arbitrage.style;
        document.getElementById('ref-cards').textContent = data.arbitrage.cartons_moyens;
        document.getElementById('ref-fouls').textContent = data.arbitrage.fautes_moyennes;

        // 4. Corners
        document.getElementById('corners-total').textContent = data.corners.total;
        document.getElementById('corners-home').textContent = data.corners.domicile;
        document.getElementById('corners-away').textContent = data.corners.exterieur;
        document.getElementById('corners-tactics').textContent = data.corners.domination;

        // 5. Scores Exacts
        const scoresList = document.getElementById('scores-list');
        scoresList.innerHTML = '';
        data.scores_exacts.forEach(s => {
            scoresList.innerHTML += `<li>Score <strong>${s.score}</strong> — Probabilité : <strong>${s.prob}%</strong></li>`;
        });

        // 6. Mi-temps & Joueurs
        document.getElementById('mt-prob').textContent = `${data.mitemps.mt2}%`;
        const playersList = document.getElementById('players-list');
        playersList.innerHTML = '';
        
        data.joueurs_cles.domicile.concat(data.joueurs_cles.exterieur).forEach(j => {
            playersList.innerHTML += `<li><strong>${j.nom}</strong> (${j.role}) : ${j.prob} probabilité</li>`;
        });

        // 7. Tendances Tactiques
        document.getElementById('tendency-home-title').textContent = data.match.domicile;
        const homeList = document.getElementById('tendency-home-list');
        homeList.innerHTML = '';
        data.tendances_tactiques.domicile.forEach(t => homeList.innerHTML += `<li>${t}</li>`);

        document.getElementById('tendency-away-title').textContent = data.match.exterieur;
        const awayList = document.getElementById('tendency-away-list');
        awayList.innerHTML = '';
        data.tendances_tactiques.exterieur.forEach(t => awayList.innerHTML += `<li>${t}</li>`);

        // Afficher les résultats
        document.getElementById('loader').classList.add('hidden');
        document.getElementById('results-area').classList.remove('hidden');

    } catch (err) {
        alert("Erreur lors de la génération de l'analyse.");
        document.getElementById('loader').classList.add('hidden');
    }
});
