"""Gogo School : page d'accueil + saisie des étudiants et classement par filière."""
from flask import Flask, request, redirect, render_template_string, url_for
import json
import os
import re
import uuid

app = Flask(__name__)

DATA_FILE = os.environ.get("DATA_FILE", "/data/etudiants.json")
os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)


# ------------------------------------------------------------------ Données
def charger():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def sauvegarder(etudiants):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(etudiants, f, ensure_ascii=False, indent=2)


def lire_notes(texte):
    """Transforme '12; 15,5 9' en [12.0, 15.5, 9.0]. Lève ValueError si invalide."""
    morceaux = [m for m in re.split(r"[;\s]+", texte.strip()) if m]
    if not morceaux:
        raise ValueError("Saisis au moins une note.")
    notes = []
    for m in morceaux:
        try:
            n = float(m.replace(",", "."))
        except ValueError:
            raise ValueError(f"Note invalide : {m}")
        if not 0 <= n <= 20:
            raise ValueError(f"La note {m} doit être comprise entre 0 et 20.")
        notes.append(n)
    return notes


# ------------------------------------------------------------------ Calculs
def attribuer_rangs(liste, cle):
    """Trie par moyenne décroissante et attribue le rang (ex æquo = même rang)."""
    liste.sort(key=lambda e: (-e["moyenne"], e["nom"].lower()))
    for i, e in enumerate(liste):
        if i > 0 and e["moyenne"] == liste[i - 1]["moyenne"]:
            e[cle] = liste[i - 1][cle]
        else:
            e[cle] = i + 1


def classement(etudiants, filiere=""):
    """Calcule les moyennes et les rangs. Si une filière est choisie, ne garde qu'elle."""
    liste = []
    for e in etudiants:
        liste.append({**e, "moyenne": round(sum(e["notes"]) / len(e["notes"]), 2)})

    # rang à l'intérieur de chaque filière
    par_filiere = {}
    for e in liste:
        par_filiere.setdefault(e["filiere"], []).append(e)
    for membres in par_filiere.values():
        attribuer_rangs(membres, "rang_filiere")

    if filiere:
        liste = par_filiere.get(filiere, [])
        for e in liste:
            e["rang"] = e["rang_filiere"]
    else:
        attribuer_rangs(liste, "rang")
    return liste


# ------------------------------------------------------------------ Gabarits HTML
STYLE = """
  * { box-sizing: border-box; }
  body { font-family: Arial, sans-serif; background: #f4f6f8; margin: 0; color: #222; }
  header { background: #0d2b5e; color: white; padding: 0 30px; }
  header .barre { max-width: 1000px; margin: auto; display: flex; align-items: center;
                  gap: 8px; padding: 12px 0; flex-wrap: wrap; }
  header .logo { font-weight: bold; font-size: 22px; margin-right: auto; color: white;
                 text-decoration: none; }
  header a.lien { color: #cfe0ff; text-decoration: none; padding: 8px 14px; border-radius: 6px; }
  header a.lien:hover { background: #17408a; color: white; }
  header a.actif { background: #1565c0; color: white; }
  main { max-width: 1000px; margin: 25px auto; padding: 0 20px; }
  .box { background: white; padding: 25px; border-radius: 10px;
         box-shadow: 0 2px 8px rgba(0,0,0,.1); margin-bottom: 25px; }
  h1 { margin-top: 0; font-size: 26px; }
  h2 { margin-top: 0; font-size: 20px; }
  .hero { background: linear-gradient(135deg, #0d2b5e, #1565c0); color: white;
          border-radius: 12px; padding: 55px 35px; margin-bottom: 25px; }
  .hero h1 { font-size: 38px; margin-bottom: 12px; }
  .hero p { font-size: 18px; line-height: 1.6; max-width: 700px; margin: 0 0 28px; }
  .gros-bouton { display: inline-block; background: #f9a825; color: #222; font-weight: bold;
                 font-size: 18px; padding: 14px 28px; border-radius: 8px; text-decoration: none; }
  .gros-bouton:hover { background: #ffb938; }
  .atouts { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 20px; }
  .atout { background: white; border-radius: 10px; padding: 22px; border-top: 5px solid #1565c0;
           box-shadow: 0 2px 8px rgba(0,0,0,.1); }
  .atout h2 { color: #0d2b5e; margin-bottom: 8px; }
  .atout p { color: #555; margin: 0; line-height: 1.5; }
  form.ajout { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
  form.ajout .large { grid-column: span 2; }
  input, select { padding: 10px; font-size: 15px; border: 1px solid #ccc;
                  border-radius: 6px; width: 100%; }
  button { padding: 10px 14px; font-size: 15px; border: none; border-radius: 6px;
           cursor: pointer; color: white; }
  .ajouter { background: #2e7d32; }
  .supprimer { background: #c62828; padding: 6px 12px; font-size: 14px; }
  .filtre { display: flex; gap: 10px; align-items: center; margin-bottom: 15px; flex-wrap: wrap; }
  .filtre select { width: auto; min-width: 180px; }
  .filtre button { background: #1565c0; }
  table { width: 100%; border-collapse: collapse; }
  th, td { text-align: left; padding: 10px 8px; border-bottom: 1px solid #eee; }
  th { background: #fafafa; }
  .scroll { overflow-x: auto; }
  .rang { font-weight: bold; text-align: center; }
  .moy { font-weight: bold; }
  .ok { color: #2e7d32; }
  .ko { color: #c62828; }
  .vide, .aide { color: #888; font-size: 14px; }
  .erreur { background: #fdecea; color: #c62828; padding: 10px; border-radius: 6px; margin-bottom: 15px; }
  .resume { margin-bottom: 15px; color: #444; }
  @media (max-width: 600px) {
    form.ajout { grid-template-columns: 1fr; } form.ajout .large { grid-column: span 1; }
  }
"""

ENTETE = """
<header><div class="barre">
  <a class="logo" href="/">Gogo School</a>
  <a class="lien {{ 'actif' if page == 'accueil' }}" href="/">Accueil</a>
  <a class="lien {{ 'actif' if page == 'classement' }}" href="/classement">Notes et classement</a>
</div></header>
"""

PAGE_ACCUEIL = """<!DOCTYPE html>
<html lang="fr"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Gogo School</title><style>""" + STYLE + """</style></head>
<body>""" + ENTETE + """
<main>
  <div class="hero">
    <h1>Bienvenue à Gogo School</h1>
    <p>Gogo School accompagne ses étudiants vers la réussite. Cette plateforme permet de saisir
    les notes de chaque étudiant, de calculer automatiquement les moyennes et de consulter
    le classement de chaque filière.</p>
    <a class="gros-bouton" href="/classement">Accéder aux notes et au classement →</a>
  </div>
  <div class="atouts">
    <div class="atout"><h2>Saisie simple</h2>
      <p>Renseigne le nom, les prénoms, la filière et les notes de chaque étudiant en quelques secondes.</p></div>
    <div class="atout"><h2>Moyennes automatiques</h2>
      <p>La moyenne de chaque étudiant est calculée à partir de ses notes sur 20.</p></div>
    <div class="atout"><h2>Classement par filière</h2>
      <p>Un filtre permet d'afficher le classement d'une filière en particulier.</p></div>
  </div>
</main></body></html>
"""

PAGE_CLASSEMENT = """<!DOCTYPE html>
<html lang="fr"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Notes et classement - Gogo School</title><style>""" + STYLE + """</style></head>
<body>""" + ENTETE + """
<main>
  <div class="box">
    <h1>Ajouter un étudiant</h1>
    {% if erreur %}<div class="erreur">{{ erreur }}</div>{% endif %}
    <form class="ajout" method="POST" action="/ajouter">
      <input type="text" name="nom" placeholder="Nom" maxlength="50" required>
      <input type="text" name="prenoms" placeholder="Prénoms" maxlength="100" required>
      <input class="large" type="text" name="filiere" placeholder="Filière (ex : Informatique)"
             list="filieres" maxlength="60" required>
      <datalist id="filieres">
        {% for f in filieres %}<option value="{{ f }}">{% endfor %}
      </datalist>
      <input class="large" type="text" name="notes" placeholder="Notes sur 20 (ex : 12 15,5 9 14)" required>
      <p class="aide large">Sépare les notes par un espace ou un point-virgule. La moyenne est la moyenne simple des notes.</p>
      <button class="ajouter large" type="submit">Ajouter</button>
    </form>
  </div>

  <div class="box">
    <h2>Classement</h2>
    <form class="filtre" method="GET" action="/classement">
      <label for="filiere">Filtrer par filière :</label>
      <select name="filiere" id="filiere">
        <option value="">Toutes les filières</option>
        {% for f in filieres %}
        <option value="{{ f }}" {% if f == filiere_choisie %}selected{% endif %}>{{ f }}</option>
        {% endfor %}
      </select>
      <button type="submit">Filtrer</button>
    </form>

    {% if etudiants %}
    <p class="resume">
      {{ etudiants|length }} étudiant(s){% if filiere_choisie %} en {{ filiere_choisie }}{% endif %}
      · Moyenne : <strong>{{ moyenne_generale }}</strong> / 20
    </p>
    <div class="scroll"><table>
      <tr>
        <th>Rang</th><th>Nom</th><th>Prénoms</th><th>Filière</th><th>Notes</th><th>Moyenne</th>
        {% if not filiere_choisie %}<th>Rang filière</th>{% endif %}<th></th>
      </tr>
      {% for e in etudiants %}
      <tr>
        <td class="rang">{{ e.rang }}</td>
        <td>{{ e.nom }}</td>
        <td>{{ e.prenoms }}</td>
        <td>{{ e.filiere }}</td>
        <td>{{ e.notes|join(" ; ") }}</td>
        <td class="moy {{ 'ok' if e.moyenne >= 10 else 'ko' }}">{{ e.moyenne }}</td>
        {% if not filiere_choisie %}<td class="rang">{{ e.rang_filiere }}</td>{% endif %}
        <td>
          <form method="POST" action="/supprimer/{{ e.id }}" onsubmit="return confirm('Supprimer cet étudiant ?')">
            <button class="supprimer" type="submit">Supprimer</button>
          </form>
        </td>
      </tr>
      {% endfor %}
    </table></div>
    {% else %}
      <p class="vide">Aucun étudiant à afficher.</p>
    {% endif %}
  </div>
</main></body></html>
"""


# ------------------------------------------------------------------ Routes
@app.route("/")
def accueil():
    return render_template_string(PAGE_ACCUEIL, page="accueil")


@app.route("/classement")
def page_classement():
    tous = charger()
    filieres = sorted({e["filiere"] for e in tous})
    choisie = request.args.get("filiere", "")
    liste = classement(tous, choisie)
    moyenne_generale = round(sum(e["moyenne"] for e in liste) / len(liste), 2) if liste else 0
    return render_template_string(
        PAGE_CLASSEMENT, page="classement", etudiants=liste, filieres=filieres,
        filiere_choisie=choisie, moyenne_generale=moyenne_generale,
        erreur=request.args.get("erreur"),
    )


@app.route("/ajouter", methods=["POST"])
def ajouter():
    nom = request.form.get("nom", "").strip()
    prenoms = request.form.get("prenoms", "").strip()
    filiere = request.form.get("filiere", "").strip()
    if not nom or not prenoms or not filiere:
        return redirect(url_for("page_classement", erreur="Merci de remplir le nom, les prénoms et la filière."))
    try:
        notes = lire_notes(request.form.get("notes", ""))
    except ValueError as err:
        return redirect(url_for("page_classement", erreur=str(err)))

    etudiants = charger()
    etudiants.append({"id": uuid.uuid4().hex, "nom": nom, "prenoms": prenoms,
                      "filiere": filiere, "notes": notes})
    sauvegarder(etudiants)
    return redirect(url_for("page_classement"))


@app.route("/supprimer/<id>", methods=["POST"])
def supprimer(id):
    sauvegarder([e for e in charger() if e["id"] != id])
    return redirect(url_for("page_classement"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)