# =========================================================================
# Deuxieme methode : lst -> ce fichier .py -> AST -> C -> binaire
#                        -> qui recrache du Python -> exec() -> resultat
# Chacune de ces fleches est inutile.
# =========================================================================

import ast, subprocess, tempfile, os

DECIMALES = 17


# La version innocente. Elle ne sera jamais executee par Python.
def moyenne(lst, n):
    somme = 0
    for i in range(n):
        somme += lst[i]
    return somme / n


# --- Etape 1 : relire sur le disque le fichier qu'on est deja en train de lire
def etape1_lire():
    with open(__file__) as f:
        arbre = ast.parse(f.read())
    fn = next(n for n in arbre.body if isinstance(n, ast.FunctionDef) and n.name == "moyenne")
    print(f"[1] '{fn.name}' relu depuis {os.path.basename(__file__)}")
    return fn


# --- Etape 2 : compiler l'AST en C, en le rendant pire
def etape2_vers_c(fn, lst):
    boucle = next(n for n in fn.body if isinstance(n, ast.For))
    accu = boucle.body[0].target.id                       # "somme"
    retour = next(n for n in fn.body if isinstance(n, ast.Return))
    assert isinstance(retour.value.op, ast.Div), "on ne gere que la division"

    valeurs = ", ".join(str(int(x)) for x in lst)
    print(f"[2] accumulateur '{accu}' -> recursion ; division -> division posee")

    return f"""#include <stdio.h>

/* la boucle for est devenue de la recursion, parce que pourquoi pas */
long long {accu}(long long *lst, int n) {{
    if (n == 0) return 0;
    return lst[n - 1] + {accu}(lst, n - 1);
}}

int main(void) {{
    long long lst[] = {{{valeurs}}};
    int n = {len(lst)};
    long long reste = {accu}(lst, n);

    /* division posee : que des soustractions, comme au CE2 */
    long long entier = 0;
    while (reste >= n) {{ reste -= n; entier++; }}

    /* on n'imprime pas le resultat, on imprime du Python qui le reconstruit */
    printf("chiffres = [(%lld, 0)", entier);
    for (int k = 1; k <= {DECIMALES}; k++) {{
        int d = 0;
        reste *= 10;
        while (reste >= n) {{ reste -= n; d++; }}
        printf(", (%d, -%d)", d, k);
    }}
    printf("]\\n");
    printf("resultat = sum(c * 10.0 ** e for c, e in chiffres)\\n");
    return 0;
}}
"""


# --- Etapes 3 et 4 : compiler, puis executer pour obtenir... du Python
def etapes34_compiler_et_lancer(code_c):
    d = tempfile.mkdtemp()
    c_file, binaire = os.path.join(d, "m.c"), os.path.join(d, "m")

    with open(c_file, "w") as f:
        f.write(code_c)

    subprocess.run(["cc", "-O2", "-o", binaire, c_file], check=True)
    print("[3] compile :", binaire)

    sortie = subprocess.run([binaire], capture_output=True, text=True, check=True).stdout
    print("[4] le binaire C a produit du Python :")
    for ligne in sortie.splitlines():
        print("      ", ligne[:70] + ("..." if len(ligne) > 70 else ""))
    return sortie


# --- Etape 5 : exec() du Python ne par le C
def etape5_exec(code_python):
    espace = {}
    exec(code_python, espace)
    print("[5] exec() termine")
    return espace["resultat"]


def moyenne_absurde(lst):
    fn = etape1_lire()
    code_c = etape2_vers_c(fn, lst)
    return etape5_exec(etapes34_compiler_et_lancer(code_c))


# =========================================================================
# Troisieme methode : maintenant qu'on a la reponse, on la met dans un
# conteneur Docker, on genere des bindings C++ depuis son schema OpenAPI,
# on les compile, et le binaire va rechercher la reponse en HTTP.
# =========================================================================

import json, socket, time, urllib.request, urllib.error

IMAGE = "moyenne-absurde"
CONTENEUR = "moyenne-absurde-srv"


# Le serveur qui tournera dans le conteneur. __RESULTAT__ sera remplace.
SERVEUR = '''
import json
from http.server import BaseHTTPRequestHandler, HTTPServer

RESULTAT = __RESULTAT__

OPENAPI = {
    "openapi": "3.0.0",
    "info": {"title": "API Moyenne", "version": "1.0.0"},
    "paths": {
        "/moyenne": {
            "get": {
                "operationId": "get_moyenne",
                "responses": {"200": {"content": {"application/json": {"schema": {
                    "type": "object",
                    "properties": {"moyenne": {"type": "number"}},
                }}}}},
            }
        }
    },
}


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/openapi.json":
            corps = OPENAPI
        elif self.path == "/moyenne":
            corps = {"moyenne": RESULTAT}
        else:
            self.send_response(404)
            self.end_headers()
            return
        donnees = json.dumps(corps).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(donnees)))
        self.end_headers()
        self.wfile.write(donnees)

    def log_message(self, *args):
        pass


HTTPServer(("0.0.0.0", 8000), Handler).serve_forever()
'''


DOCKERFILE = """FROM python:3.13-alpine
COPY serveur.py /serveur.py
EXPOSE 8000
CMD ["python", "-u", "/serveur.py"]
"""


# Les bindings C++. __METHODES__ et __PORT__ seront remplaces.
CLIENT_CPP = '''#include <iostream>
#include <string>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>

// --- bindings generes automatiquement depuis /openapi.json ---
class ApiMoyenne {
    std::string hote_;
    int port_;

    // HTTP/1.1 a la main sur une socket brute, parce qu'une lib ce serait tricher
    std::string requete(const std::string& chemin) {
        int fd = socket(AF_INET, SOCK_STREAM, 0);
        sockaddr_in adr{};
        adr.sin_family = AF_INET;
        adr.sin_port = htons(port_);
        inet_pton(AF_INET, hote_.c_str(), &adr.sin_addr);
        if (connect(fd, (sockaddr*)&adr, sizeof adr) < 0) {
            std::cerr << "connexion impossible" << std::endl;
            return "";
        }
        std::string req = "GET " + chemin + " HTTP/1.1\\r\\nHost: " + hote_ +
                          "\\r\\nConnection: close\\r\\n\\r\\n";
        send(fd, req.c_str(), req.size(), 0);

        std::string rep;
        char tampon[1024];
        ssize_t n;
        while ((n = recv(fd, tampon, sizeof tampon, 0)) > 0) rep.append(tampon, n);
        close(fd);

        auto p = rep.find("\\r\\n\\r\\n");
        return p == std::string::npos ? "" : rep.substr(p + 4);
    }

    // parseur JSON de 3 lignes, strictement suffisant et pas une de plus
    static double champ(const std::string& j, const std::string& nom) {
        auto p = j.find("\\"" + nom + "\\"");
        if (p == std::string::npos) throw std::runtime_error("champ absent");
        return std::stod(j.substr(j.find(':', p) + 1));
    }

public:
    ApiMoyenne(std::string hote, int port) : hote_(hote), port_(port) {}

__METHODES__
};

int main() {
    ApiMoyenne api("127.0.0.1", __PORT__);
    std::cout.precision(17);
    std::cout << api.get_moyenne() << std::endl;
    return 0;
}
'''


def port_libre():
    s = socket.socket()
    s.bind(("", 0))
    port = s.getsockname()[1]
    s.close()
    return port


# --- Etape 6 : enfermer la reponse dans une image Docker
def etape6_docker(resultat, dossier):
    with open(os.path.join(dossier, "serveur.py"), "w") as f:
        f.write(SERVEUR.replace("__RESULTAT__", repr(resultat)))
    with open(os.path.join(dossier, "Dockerfile"), "w") as f:
        f.write(DOCKERFILE)

    subprocess.run(["docker", "build", "-q", "-t", IMAGE, dossier],
                   check=True, capture_output=True)
    print(f"[6] image '{IMAGE}' construite, la reponse est dedans")

    subprocess.run(["docker", "rm", "-f", CONTENEUR], capture_output=True)
    port = port_libre()
    subprocess.run(["docker", "run", "-d", "--name", CONTENEUR,
                    "-p", f"{port}:8000", IMAGE], check=True, capture_output=True)

    base = f"http://127.0.0.1:{port}"
    for _ in range(100):
        try:
            with urllib.request.urlopen(base + "/openapi.json", timeout=1) as r:
                schema = json.load(r)
            print(f"[6] conteneur en ecoute sur {base}")
            return schema, port
        except (urllib.error.URLError, ConnectionError, TimeoutError):
            time.sleep(0.2)
    raise RuntimeError("le conteneur n'a jamais repondu")


# --- Etape 7 : generer des bindings C++ a partir du schema OpenAPI
def etape7_bindings(schema, port):
    methodes = []
    for chemin, operations in schema["paths"].items():
        for op in operations.values():
            nom = op["operationId"]
            corps = op["responses"]["200"]["content"]["application/json"]["schema"]
            attribut = next(iter(corps["properties"]))
            methodes.append(
                f'    double {nom}() {{ return champ(requete("{chemin}"), "{attribut}"); }}'
            )
            print(f"[7] binding genere : double {nom}()  ->  GET {chemin}")

    return CLIENT_CPP.replace("__METHODES__", "\n".join(methodes)) \
                     .replace("__PORT__", str(port))


# --- Etape 8 : compiler le C++, le lancer, et reparser sa sortie
def etape8_interroger(code_cpp, dossier):
    cpp_file = os.path.join(dossier, "client.cpp")
    binaire = os.path.join(dossier, "client")

    with open(cpp_file, "w") as f:
        f.write(code_cpp)

    subprocess.run(["c++", "-std=c++17", "-O2", "-o", binaire, cpp_file], check=True)
    print("[8] bindings C++ compiles")

    sortie = subprocess.run([binaire], capture_output=True, text=True, check=True).stdout
    print(f"[8] le client C++ a interroge le conteneur et repond : {sortie.strip()}")
    return float(sortie)


def moyenne_par_docker(resultat):
    dossier = tempfile.mkdtemp()
    try:
        schema, port = etape6_docker(resultat, dossier)
        return etape8_interroger(etape7_bindings(schema, port), dossier)
    finally:
        subprocess.run(["docker", "rm", "-f", CONTENEUR], capture_output=True)
        print("[8] conteneur supprime")


lst = [1, 2, 3, 4, 5]
print(f"\nliste : {lst}\n")
resultat = moyenne_absurde(lst)
resultat = moyenne_par_docker(resultat)
print(f"\nresultat : {resultat}")
print(f"attendu  : {sum(lst) / len(lst)}")