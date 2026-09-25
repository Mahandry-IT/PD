# Stats Enterprise — fonctions 7 & 9 du CDC

Ce dépôt respecte strictement les signatures publiques attribuées à Clément :

```python
def ecart_type(nombres: list[float]) -> float | None
def variance_population(nombres: list[float]) -> float | None
```

Les fonctions ne font aucun `print`, ne modifient pas `nombres`, retournent `None` si la liste est vide et utilisent la variance de **population** (division par `n`).

## Test de référence

Pour `[12.0, 4.5, 3.0]` :

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

Le menu n'a besoin d'importer que :

```python
from app.statistiques import ecart_type, variance_population
```

Le reste de la plomberie est volontairement invisible pour respecter le CDC.
