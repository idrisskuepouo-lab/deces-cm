from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from datetime import datetime, timedelta
import uuid, hashlib, os, random
from functools import wraps

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'deces-cm-inf232-ec2-2024')

# ══════════════════════════════════════════════════════
#  BASE DE DONNÉES EN MÉMOIRE (compatible Vercel)
# ══════════════════════════════════════════════════════
DB = {
    "deces": [],
    "users": [
        {
            "id": "admin-001",
            "nom": "ADMINISTRATEUR",
            "prenom": "Système",
            "email": "admin@deces-cm.cm",
            "password": hashlib.sha256("Admin@2024".encode()).hexdigest(),
            "role": "admin",
            "created_at": datetime.now().isoformat()
        },
        {
            "id": "agent-001",
            "nom": "ATANGANA",
            "prenom": "Paul",
            "email": "paul.atangana@deces-cm.cm",
            "password": hashlib.sha256("Agent@2024".encode()).hexdigest(),
            "role": "agent",
            "created_at": datetime.now().isoformat()
        }
    ]
}

CAUSES = [
    "Paludisme", "VIH/SIDA", "Tuberculose", "Accident de la route",
    "Maladie cardiovasculaire", "Cancer", "Pneumonie", "Choléra",
    "Septicémie", "Diabète", "Insuffisance rénale", "Méningite",
    "Hépatite virale", "Mort naturelle (vieillesse)", "Noyade",
    "Brûlures", "Homicide", "Mort maternelle", "Mort néonatale",
    "Maladie inconnue", "Autre"
]

LIEUX = [
    "Hôpital général", "Centre de santé", "Domicile", "Rue / Espace public",
    "Clinique privée", "CHU (Centre Hospitalier Universitaire)", "Maternité",
    "Route / Accident", "Lieu de travail", "Forêt / Zone rurale", "Autre"
]

REGIONS = [
    "Adamaoua", "Centre", "Est", "Extrême-Nord", "Littoral",
    "Nord", "Nord-Ouest", "Ouest", "Sud", "Sud-Ouest"
]

def seed():
    noms = ["MVONDO","BIYA","ATANGANA","NGUELE","EWONDO","MBARGA",
            "TCHOUAKE","FOUDA","NDJOCK","ESSOMBA","BELLO","HAROUNA"]
    prenoms = ["Jean","Marie","Paul","Fatima","Pierre","Aminata",
               "François","Aïcha","Joseph","Ngozi","André","Laetitia"]
    for i in range(1, 61):
        date_deces = datetime.now() - timedelta(days=random.randint(1, 365))
        DB["deces"].append({
            "id": f"DC-{2000+i}",
            "nom": random.choice(noms),
            "prenom": random.choice(prenoms),
            "age": random.randint(0, 95),
            "sexe": random.choice(["M","F"]),
            "region": random.choice(REGIONS),
            "arrondissement": f"Arrondissement {random.randint(1,6)}",
            "cause_principale": random.choice(CAUSES),
            "cause_secondaire": random.choice(CAUSES + [""]),
            "lieu_deces": random.choice(LIEUX),
            "date_deces": date_deces.strftime("%Y-%m-%d"),
            "heure_deces": f"{random.randint(0,23):02d}:{random.randint(0,59):02d}",
            "declare_par": random.choice(["Famille","Médecin","Agent de santé","Autorité locale"]),
            "profession_defunt": random.choice(["Agriculteur","Commerçant","Fonctionnaire","Enseignant","Sans emploi","Retraité","Élève/Étudiant"]),
            "observations": "",
            "created_at": (datetime.now() - timedelta(days=random.randint(0,10))).isoformat(),
            "agent_id": "agent-001"
        })

seed()

# ══════════════════════════════════════════════════════
#  AUTH
# ══════════════════════════════════════════════════════
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        if session.get('user_role') != 'admin':
            return jsonify({"error": "Accès administrateur requis"}), 403
        return f(*args, **kwargs)
    return decorated

# ══════════════════════════════════════════════════════
#  PAGES
# ══════════════════════════════════════════════════════
@app.route('/')
def index():
    return redirect(url_for('dashboard') if 'user_id' in session else url_for('login'))

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        pwd  = hashlib.sha256(data.get('password','').encode()).hexdigest()
        user = next((u for u in DB["users"]
                     if u['email'] == data.get('email') and u['password'] == pwd), None)
        if user:
            session.update({'user_id': user['id'], 'user_role': user['role'],
                            'user_name': f"{user['prenom']} {user['nom']}"})
            return jsonify({"success": True})
        return jsonify({"success": False, "message": "Identifiants incorrects"}), 401
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html',
        user_name=session.get('user_name'), role=session.get('user_role'))

@app.route('/deces')
@login_required
def deces_page():
    return render_template('deces.html',
        user_name=session.get('user_name'), role=session.get('user_role'),
        causes=CAUSES, lieux=LIEUX, regions=REGIONS)

@app.route('/rapport')
@login_required
def rapport():
    return render_template('rapport.html',
        user_name=session.get('user_name'), role=session.get('user_role'))

# ══════════════════════════════════════════════════════
#  API — DÉCÈS
# ══════════════════════════════════════════════════════
@app.route('/api/deces', methods=['GET','POST'])
@login_required
def api_deces():
    if request.method == 'GET':
        data = DB["deces"][:]
        region   = request.args.get('region','')
        cause    = request.args.get('cause','')
        lieu     = request.args.get('lieu','')
        sexe     = request.args.get('sexe','')
        date_min = request.args.get('date_min','')
        date_max = request.args.get('date_max','')
        search   = request.args.get('search','').lower()
        if region:   data = [d for d in data if d['region'] == region]
        if cause:    data = [d for d in data if d['cause_principale'] == cause]
        if lieu:     data = [d for d in data if d['lieu_deces'] == lieu]
        if sexe:     data = [d for d in data if d['sexe'] == sexe]
        if date_min: data = [d for d in data if d['date_deces'] >= date_min]
        if date_max: data = [d for d in data if d['date_deces'] <= date_max]
        if search:
            data = [d for d in data if search in (d['nom']+' '+d['prenom']).lower()
                    or search in d['id'].lower()]
        return jsonify(sorted(data, key=lambda x: x['date_deces'], reverse=True))

    data = request.get_json()
    required = ['nom','prenom','age','sexe','region','cause_principale','lieu_deces','date_deces']
    missing  = [f for f in required if not str(data.get(f,'')).strip()]
    if missing:
        return jsonify({"error": f"Champs manquants: {', '.join(missing)}"}), 400
    record = {
        "id":                f"DC-{uuid.uuid4().hex[:6].upper()}",
        "nom":               data['nom'].upper().strip(),
        "prenom":            data['prenom'].strip().title(),
        "age":               int(data['age']),
        "sexe":              data['sexe'],
        "region":            data['region'],
        "arrondissement":    data.get('arrondissement','').strip(),
        "cause_principale":  data['cause_principale'],
        "cause_secondaire":  data.get('cause_secondaire',''),
        "lieu_deces":        data['lieu_deces'],
        "date_deces":        data['date_deces'],
        "heure_deces":       data.get('heure_deces',''),
        "declare_par":       data.get('declare_par','Agent de santé'),
        "profession_defunt": data.get('profession_defunt',''),
        "observations":      data.get('observations','').strip(),
        "created_at":        datetime.now().isoformat(),
        "agent_id":          session['user_id']
    }
    DB["deces"].append(record)
    return jsonify(record), 201

@app.route('/api/deces/<did>', methods=['GET','PUT','DELETE'])
@login_required
def api_deces_detail(did):
    record = next((d for d in DB["deces"] if d['id'] == did), None)
    if not record:
        return jsonify({"error": "Introuvable"}), 404
    if request.method == 'GET':
        return jsonify(record)
    if request.method == 'PUT':
        data = request.get_json()
        for k in record:
            if k in data:
                record[k] = data[k]
        record['updated_at'] = datetime.now().isoformat()
        return jsonify(record)
    if request.method == 'DELETE':
        if session.get('user_role') != 'admin':
            return jsonify({"error": "Réservé aux administrateurs"}), 403
        DB["deces"].remove(record)
        return jsonify({"message": "Supprimé"})

# ══════════════════════════════════════════════════════
#  API — STATISTIQUES
# ══════════════════════════════════════════════════════
@app.route('/api/stats')
@login_required
def api_stats():
    deces = DB["deces"]
    total = len(deces)
    if total == 0:
        return jsonify({"total": 0})

    causes = {}
    lieux  = {}
    regions = {}
    tranches = {"0-14": 0, "15-24": 0, "25-44": 0, "45-64": 0, "65+": 0}
    monthly  = {}

    for d in deces:
        causes[d['cause_principale']]  = causes.get(d['cause_principale'], 0) + 1
        lieux[d['lieu_deces']]         = lieux.get(d['lieu_deces'], 0) + 1
        regions[d['region']]           = regions.get(d['region'], 0) + 1
        a = int(d['age'])
        if a < 15:   tranches["0-14"]  += 1
        elif a < 25: tranches["15-24"] += 1
        elif a < 45: tranches["25-44"] += 1
        elif a < 65: tranches["45-64"] += 1
        else:        tranches["65+"]   += 1
        m = d['date_deces'][:7]
        monthly[m] = monthly.get(m, 0) + 1

    hommes = sum(1 for d in deces if d['sexe'] == 'M')
    ages   = [int(d['age']) for d in deces]
    now_m  = datetime.now().strftime("%Y-%m")
    ce_mois = sum(1 for d in deces if d['date_deces'].startswith(now_m))

    return jsonify({
        "total":      total,
        "hommes":     hommes,
        "femmes":     total - hommes,
        "age_moyen":  round(sum(ages)/len(ages), 1),
        "ce_mois":    ce_mois,
        "causes":     dict(sorted(causes.items(), key=lambda x: x[1], reverse=True)[:8]),
        "lieux":      dict(sorted(lieux.items(),  key=lambda x: x[1], reverse=True)),
        "regions":    regions,
        "tranches":   tranches,
        "monthly":    dict(sorted(monthly.items())[-6:])
    })

@app.route('/api/export')
@login_required
def api_export():
    return jsonify(DB["deces"])

@app.route('/api/referentiels')
def api_ref():
    return jsonify({"causes": CAUSES, "lieux": LIEUX, "regions": REGIONS})

@app.route('/api/users', methods=['GET','POST'])
@admin_required
def api_users():
    if request.method == 'GET':
        return jsonify([{k:v for k,v in u.items() if k!='password'} for u in DB["users"]])
    data = request.get_json()
    if next((u for u in DB["users"] if u['email']==data.get('email')), None):
        return jsonify({"error": "Email déjà utilisé"}), 409
    user = {
        "id":         f"USR-{uuid.uuid4().hex[:6].upper()}",
        "nom":        data['nom'].upper(),
        "prenom":     data['prenom'].title(),
        "email":      data['email'],
        "password":   hashlib.sha256(data.get('password','Agent@2024').encode()).hexdigest(),
        "role":       data.get('role','agent'),
        "created_at": datetime.now().isoformat()
    }
    DB["users"].append(user)
    return jsonify({k:v for k,v in user.items() if k!='password'}), 201

if __name__ == '__main__':
    app.run(debug=True, port=5000)
