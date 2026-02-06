# Pipeline de Données RTE (Data Lake & Monitoring)

Ce projet implémente un pipeline de données complet : Ingestion (Airflow) -> Datalake (MongoDB) -> Traitement (Spark) -> Stockage Final (PostgreSQL) -> Monitoring (Grafana/pgAdmin).

## 🚀 Démarrage Rapide

### Prerequis

1. Clone le projet
``git clone https://github.com/IMT-Ales/BigData``

1. Avoir le deamon docker de lancé

### Démarrage

Pour lancer toute la stack :

```bash
docker compose up -d
```

Pour arrêter : `docker compose down`.

## 🛠️ Accès aux Services

| Service | URL | Login | Mot de passe | Description |
| :--- | :--- | :--- | :--- | :--- |
| **Airflow** | `http://localhost:8080` | `airflow` | `airflow` | Orchestration des DAGs. |
| **Grafana** | `http://localhost:3000` | `admin` | `admin` | Visualisation des métriques & logs. |
| **pgAdmin** | `http://localhost:5050` | `admin@admin.com` | `root` | Interface web pour PostgreSQL. |
| **Postgres** | `localhost:5433` | `airflow` | `airflow` | Base de données finale (Port Docker). |
| **Mongo** | `localhost:27017` | `admin` | `password` | Data Lake brut. |

### Configuration pgAdmin (Ajout Serveur)
Une fois connecté à pgAdmin, ajoutez un nouveau serveur avec :
*   **Host API** : `postgres` (Réseau Docker interne)
*   **Username** : `airflow`
*   **Password** : `airflow`
*   **Maintenance DB** : `airflow` (ou `rte_data`)

## 📊 Données & Traitement

### 1. Source (API RTE)
Récupération des données **éCO2mix régionales temps réel** via l'API OpenDataSoft de RTE.
*   **Données** : Consommation, Echanges physiques, Production par filière.
*   **Fréquence** : Ingestion quotidienne (`@daily`).

### 2. Pipeline de Traitement (Spark)
Un job PySpark est déclenché automatiquement après l'ingestion.
*   **Lecture** : Depuis MongoDB.
*   **Transformation** :
    *   Agrégation par `Région`, `Filière` et `Date/Heure`.
    *   Calcul des moyennes de consommation et échanges physiques.
    *   Ajout d'un horodatage de traitement (`processed_at`).
*   **Ecriture** : Dans PostgreSQL (Table `regional_energy_stats`), en mode **Append** (ajout sans écraser l'historique).

## 📈 Monitoring
*   **Grafana** : Un dashboard "PostgreSQL Overview" est pré-chargé pour surveiller la santé de la base de données (TPS, Taille, Connexions).
*   **Logs** : Les logs Postgres sont collectés par Promtail et visibles dans Grafana (Explore -> Loki).

## 🙍‍♂️ Groupes

* Maxence Tourniayre (Xamez)
* Thomas Nalix 
* Rohart Yoann