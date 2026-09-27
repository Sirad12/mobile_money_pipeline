# Mobile Money Data Pipeline (Sénégal)

Pipeline de data engineering batch/ELT simulant l'ingestion et le traitement quotidien de transactions mobile money (Orange Money, Wave) au Sénégal, orchestré avec **Apache Airflow** et transformé avec **dbt**, sur un entrepôt **PostgreSQL**, avec visualisation dans **Metabase**.

## Objectif du projet

Ce projet fait partie de mon portfolio en Intelligence Artificielle et Big Data (DIT, Dakar). Après un premier projet de pipeline temps réel/streaming (surveillance météo et qualité de l'air avec Kafka), j'ai voulu approfondir l'autre grande famille d'architectures data engineering : le **traitement batch/incrémental**, avec une stack orientée ELT moderne (Airflow + dbt).

Le domaine du mobile money a été choisi pour :
- rester dans un contexte de données financières sans nécessiter de connaissances boursières,
- proposer un angle « données africaines/sénégalaises », peu représenté dans les portfolios data,
- offrir suffisamment de richesse (montants, types de transaction, patterns temporels) pour construire de vraies transformations et de vrais tests de qualité de données.

## Architecture

```
generate_daily_transactions.py (simulation de données)
        ↓
Airflow DAG — tâche generer_et_charger_transactions
        ↓
PostgreSQL — schéma "raw" (données brutes)
        ↓
dbt run (staging → marts)
        ↓
PostgreSQL — schéma "staging" (vue nettoyée + table agrégée)
        ↓
Metabase (dashboard : tendance temporelle, répartition par type, répartition par opérateur)
```

## Pourquoi des données simulées

Il n'existe pas d'API publique pour Orange Money ou Wave. Les transactions sont donc générées par un script Python, avec des distributions statistiques choisies pour rester réalistes plutôt qu'aléatoires :

- **Montants** : distribution log-normale (`numpy.random.lognormal`) — beaucoup de petites transactions, peu de grosses, jamais de valeur négative.
- **Heures de transaction** : distribution normale centrée sur 14h — activité concentrée en journée, plus rare la nuit.
- **Types de transaction** : pondérés par fréquence réaliste (transferts 35%, paiements marchands 25%, dépôts/retraits 15% chacun, recharges 10%).
- **Opérateurs** : répartition équiprobable entre Orange Money et Wave (confirmé ~50/50 dans le dashboard final).
- **Jours particuliers** : hausse du volume en fin de mois (+40%, salaires) et le vendredi (+20%).
- **Taux d'échec** : ~4% des transactions, pour refléter les erreurs réseau/solde insuffisant réelles.

## Stack technique

| Composant | Rôle |
|---|---|
| Python (pandas, numpy, Faker) | Génération des données simulées |
| Apache Airflow | Orchestration du pipeline (planification, dépendances entre tâches) |
| PostgreSQL | Entrepôt de données (schémas raw / staging) |
| dbt | Transformation SQL, tests de qualité de données, documentation |
| Docker / docker-compose | Environnement reproductible (image Airflow personnalisée avec dépendances) |
| Metabase | Dashboard de visualisation (conteneurisé, connecté à PostgreSQL) |

## Structure du dépôt

```
mobile-money-pipeline/
├── dags/
│   └── pipeline_dag.py    # DAG Airflow (génération + chargement quotidien)
├── data_generation/
│   ├── generate_daily_transactions.py  # Simulation des transactions
│   └── load_to_postgres.py             # Chargement dans PostgreSQL
├── dbt_project/
│   ├── models/
│   │   ├── staging/
│   │   │   ├── sources.yml             # Déclaration de la source raw.transactions
│   │   │   ├── schema.yml              # Tests de qualité de données
│   │   │   └── stg_transactions.sql    # Nettoyage/typage des données brutes
│   │   ├── intermediate/               # Réservé pour de futures transformations
│   │   └── marts/
│   │       └── fct_transactions_quotidiennes.sql  # Agrégation par jour/type/opérateur
│   ├── dbt_project.yml
├── postgres_init/
│   └── create_databases.sql            # Création automatique des bases et schémas
├── docker-compose.yml
├── Dockerfile                          # Image Airflow étendue avec les dépendances Python
├── requirements.txt
└── README.md
```

## Installation et exécution

### Prérequis
- Docker et Docker Compose installés
- Python 3.x (pour le développement local du script de génération et de dbt)

### 1. Cloner le dépôt
```bash
git clone https://github.com/Sirad12/mobile-money-pipeline.git
cd mobile-money-pipeline
```

### 2. Environnement Python local
```bash
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

### 3. Démarrer l'infrastructure Docker
```bash
docker-compose build
docker-compose up -d postgres
docker-compose run --rm airflow-webserver airflow db init
docker-compose run --rm airflow-webserver airflow users create \
  --username admin --firstname <prenom> --lastname <nom> \
  --role Admin --email <email> --password admin
docker-compose up -d
```

### 4. Charger un premier jeu de données (optionnel, hors Airflow)
```bash
cd data_generation
python generate_daily_transactions.py
python test_chargement.py
cd ..
```

### 5. Exécuter les transformations dbt
```bash
cd dbt_project
dbt run
dbt test
cd ..
```

### 6. Accéder aux interfaces
- Airflow : [http://localhost:8080](http://localhost:8080)
- Metabase : [http://localhost:3000](http://localhost:3000) — configurer la connexion PostgreSQL avec host `postgres`, base `mobile_money_db`, utilisateur/mot de passe `airflow`/`airflow`

## Limitation connue

Le script `postgres_init/create_databases.sql` ne s'exécute qu'au premier démarrage d'un volume PostgreSQL vide. Toute suppression du volume (`docker volume rm ... postgres_data`) efface l'intégralité des données déjà chargées (raw comme dbt) — il faut alors relancer les étapes 4 et 5 pour repeupler la base. Une piste d'amélioration serait un script de seed automatique déclenché au démarrage.

## État d'avancement

- [x] Environnement Docker (PostgreSQL + Airflow webserver/scheduler, image personnalisée)
- [x] Script de génération de transactions simulées (distributions réalistes)
- [x] DAG Airflow (génération + chargement PostgreSQL quotidien)
- [x] Projet dbt (modèle staging avec tests + modèle mart agrégé)
- [x] Tests de qualité de données dbt (unicité, valeurs non nulles, valeurs acceptées)
- [x] Dashboard Metabase (tendance temporelle, répartition par type de transaction, répartition par opérateur)

## Pistes d'amélioration futures

- Séparer proprement les schémas `staging` et `marts` (actuellement regroupés dans `staging` pour simplifier la configuration dbt)
- Ajouter un modèle `intermediate` pour des calculs plus complexes (ex. solde net par client)
- Automatiser le repeuplement des données après un reset du volume PostgreSQL
- Connecter directement Airflow à dbt (actuellement deux étapes manuelles séparées)

## Auteure

**Ndeye Sira Dia** — Étudiante en Licence 3 Intelligence Artificielle et Big Data, Dakar Institute of Technology (DIT)
