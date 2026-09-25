# Stats Enterprise — fonctions 3, 7 & 9 du CDC

Les fonctions 7 et 9 attribuées à Clément gardent leurs signatures publiques :

```python
def ecart_type(nombres: list[float]) -> float | None
def variance_population(nombres: list[float]) -> float | None
```

Les fonctions ne font aucun `print`, ne modifient pas `nombres` et retournent `None` si la liste est vide. La variance est une variance de **population** (division par `n`).

La moyenne propose deux beans sélectionnables : le calcul standard et la fonction Python `moyenne(lst, n)` chargée depuis le fichier d'Ilian. Pour lancer l'API hors Docker, configure son chemin local avant de démarrer :

```bash
export ILIAN_MOYENNE_FILE=/chemin/vers/PD/rendu/ilian.py
```

Dans Docker Compose depuis ce dossier, le fichier `rendu/ilian.py` du dépôt est monté en lecture seule dans les deux services API et `ILIAN_MOYENNE_FILE` pointe vers `/app/ilian.py`.

Depuis le programme :

```python
from app.statistiques import moyenne_population

moyenne = moyenne_population(nombres)  # mode standard
moyenne_ilian = moyenne_population(nombres, utiliser_code_ilian=True)
```

Les deux renvoient `None` pour une liste vide. Le menu peut alors afficher `La liste est vide.` ; sinon, afficher `Moyenne : {moyenne:.2f}`.

## Test de référence

Pour `[12.0, 4.5, 3.0]` :

- moyenne = `6.50`
- variance = `15.5`
- écart type = `sqrt(15.5)` ≈ `3.937003937...`, soit `3.94` à l'affichage

## Tests locaux

```bash
python -m pytest -q
```

## Docker Compose

```bash
docker compose up --build
```

Services :

- Load balancer Nginx : http://localhost:8080
- Swagger FastAPI : http://localhost:8080/docs
- Prometheus : http://localhost:9090
- Grafana : http://localhost:3000 (`admin` / `admin`, dev uniquement)
- Redis : réseau backend interne uniquement

Exemple :

```bash
curl -X POST http://localhost:8080/variance \
  -H 'content-type: application/json' \
  -d '{"nombres":[12,4.5,3]}'
```

La moyenne standard ou le bean chargé depuis le fichier d'Ilian :

```bash
curl -X POST 'http://localhost:8080/moyenne?mode=ilian' \
  -H 'content-type: application/json' \
  -d '{"nombres":[12,4.5,3]}'
```

## Kubernetes

Construire d'abord l'image :

```bash
docker build -t stats-enterprise:1.0.0 .
```

Puis :

```bash
kubectl apply -f k8s/all.yaml
```

Le `Service` `statistics-lb` est de type `LoadBalancer`. Les `NetworkPolicy` constituent le pare-feu réseau intra-cluster, sous réserve d'un CNI qui les applique (Calico, Cilium, etc.). Le pare-feu périmétrique cloud/host reste dépendant de l'environnement d'exécution.

## OpenAPI

Le contrat demandé est dans `openapi.yaml`.

## Intégration dans le programme du groupe

Le menu peut importer les fonctions qui lui sont nécessaires :

```python
from app.statistiques import ecart_type, moyenne_population, variance_population

moyenne = moyenne_population(nombres)  # standard
moyenne_avec_ilian = moyenne_population(nombres, utiliser_code_ilian=True)
```

Le `main.py` expose aussi `moyenne_population_enterprise(nombres, mode="ilian")` pour appeler l'API. Le bean extrait et charge uniquement `moyenne(lst, n)` au premier appel du mode Ilian ; le fichier complet n'est pas importé, car il lance le pipeline C/C++ et Docker au niveau global et sa conversion en entiers perd la précision des décimaux. Ne pointe `ILIAN_MOYENNE_FILE` que vers le fichier source de confiance d'Ilian. Dans Kubernetes, il faut aussi monter ce fichier dans les pods API pour activer le mode Ilian.
