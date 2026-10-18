# Monétiser le Dossier Maître (prédiction / décision)

## Verdict

Le dossier est une **carte de recherche**, pas un produit. 76 sections, ~200 projets : personne n'achète ça, et le construire en entier prendrait des années.
Ce qui se vend, c'est **une douleur précise résolue avec un chiffre**. Le dossier le dit lui-même (§72) : « 99 % de sophistication pour 1 % de valeur = mauvais choix ».

Règle de monétisation : **vendre le résultat (cash sauvé / impayés évités), pas la science.** Les briques du dossier (calibration, abstention, baselines, approval-gating) sont l'avantage concurrentiel *derrière* le produit, pas l'argument de vente.

## Où est l'argent (classé par rapidité de cash)

| # | Offre | Cible | Brique du dossier | Prix indicatif | Délai 1er euro |
|---|-------|-------|-------------------|----------------|----------------|
| 1 | **Audit prévision trésorerie / impayés** (service) | TPE/PME, e-commerçants, agences | §3, 13, 14, 31 | 500–3 000 € / audit | 1–2 semaines |
| 2 | **Alerte « facture qui va être payée en retard »** (SaaS) | Freelances, PME B2B | §14 survival, §13 conformal | 29–99 €/mois | 4–8 semaines |
| 3 | **Alerte seuil de trésorerie à 7/30/90 j** | PME, e-commerçants | §5 collision, §19 CVaR, §35 | 49–199 €/mois | 6–10 semaines |
| 4 | **Churn / refroidissement client** | Shopify, abonnements | §44 multi-state, §14 | 49–149 €/mois | 6–10 semaines |
| 5 | **Newsletter / formation « prévoir sans se mentir »** | Data/finance/ops | tout le dossier | 0 → 19 €/mois, cours 99–299 € | 2–4 semaines |
| 6 | **API de prévision calibrée** (white-label) | Éditeurs de compta/ERP | §13, 28, 31 | usage / licence | 3–6 mois |

## Recommandation : la séquence

1. **Semaine 1–2 — Service d'abord (offre #1).** Prendre 3–5 PME, exporter leurs factures + relevés, produire un rapport : délai de paiement prévu par client, risque de trou de trésorerie, intervalle d'incertitude, comparé à une baseline naïve. Facturer. Cela valide la douleur *et* fournit les données pour construire le produit.
2. **Semaine 3–6 — Productiser (offre #2).** Un seul cas : import CSV/Qonto/Pennylane → prédiction du retard de paiement par facture + relance suggérée (approval-gated, §37). Pas de causalité, pas de fédération, pas de POMDP.
3. **Semaine 6–12 — Ajouter #3** (cash à 30/90 jours avec scénarios Monte Carlo), vendu en palier supérieur.
4. **En parallèle — contenu (offre #5)** : publier chaque brique en vulgarisation (« pourquoi votre intervalle à 80 % ne couvre que 60 % »). C'est le canal d'acquisition des offres 1–4.
5. **Plus tard seulement** : API white-label (#6), causalité, apprentissage inter-entreprises (§58–62, avec le moat données).

## MVP technique (V1 du dossier, réduit)

- **Entrée** : CSV factures + paiements (puis connecteurs).
- **Modèle** : `lifelines` (survie du délai de paiement) + baseline (médiane par client) + MAPIE (intervalle conformal).
- **Arena** (§31) : le modèle ne sort que s'il bat la baseline en validation walk-forward ; sinon le produit affiche « insuffisamment prévisible » (§11, §73.7).
- **Sortie** : probabilité de paiement à J+7/15/30 + intervalle + action suggérée, jamais exécutée sans validation humaine.
- **Boucle** (§67) : chaque prédiction est loggée, comparée à la réalité, score de calibration affiché au client → c'est la preuve commerciale.

## Positionnement et pitch

> « On ne prédit pas l'avenir. On vous dit quelles factures seront probablement en retard, avec quelle fiabilité mesurée, et quand ne pas se fier à nous. »

La calibration publique et l'abstention honnête sont un **différenciateur** face aux outils qui promettent « 95 % de précision ».

## À éviter (pour l'argent *et* le risque)

- **Trading / paris / prédictions de marché pour soi** : le dossier lui-même (§4) montre que l'overfit est le piège central. Aucun edge démontré ici ; pas de promesse de rendement, pas de signaux vendus comme garantis (aussi un risque réglementaire AMF).
- **Vendre « le moteur »** : trop abstrait, cycle de vente interminable.
- **Licences** : vérifier code *et poids* avant usage commercial des PFN (§29), ForecastPFN, etc. ; préférer lifelines/MAPIE/sktime (licences permissives) pour le MVP.
- **Données clients (RGPD)** : hébergement UE, minimisation, DPA signé dès le premier client ; la fédération (§61) est hors périmètre tant qu'il n'y a pas de volume.

## Indicateurs de validation (go / no-go à 6 semaines)

- ≥ 3 clients payants sur l'audit ou ≥ 10 inscrits à la bêta payante.
- Modèle battant la baseline d'au moins ~10 % en erreur, couverture d'intervalle dans ±5 pts de la cible.
- ≥ 1 client qui dit avoir agi sur une alerte (relance, report d'achat) avec un montant identifiable.

Si aucun des trois : pivoter vers contenu/consulting plutôt que construire plus.

## Prochaines décisions (à toi)

1. Marché cible : France/UE francophone (Pennylane, Qonto) ou international ?
2. Tu as déjà accès à des données réelles (ton activité, des clients) pour l'audit n°1 ?
3. Service d'abord (recommandé) ou produit SaaS direct ?

## Statut (mis à jour)

Décisions prises : marché **international** (anglais), **pas de données réelles** disponibles, **service d'abord** pour obtenir des données.
MVP disponible dans `latepay/` (voir `README.md`) : prévision de retard par facture, intervalle conforme, arène walk-forward avec abstention. Testé uniquement sur données synthétiques.
Prochaine étape : démarcher 10 PME/agences (US/UK/UE) avec l'offre « audit gratuit de 20 factures en échange d'un cas d'étude », puis facturer l'audit suivant.

## Site (cheldon.fr)

Code dans `site/` (page de vente, formulaire de pilote → Cloudflare Pages Function + KV, notice de confidentialité à compléter). Déploiement : donner `CODEX_PROMPT.md` à Codex.
Avant la mise en ligne : compléter `site/privacy.html` (responsable de traitement, durées). Paiement Stripe à ajouter après le premier pilote réussi.
