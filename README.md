# ⚰ Registre National des Décès — Cameroun
## TP INF232 EC2 · Application Flask de Collecte de Données

---

## 🏗️ Architecture
```
deces-cm/
├── app.py                  ← Backend Flask (API REST + Authentification)
├── requirements.txt        ← Dépendances Python
├── vercel.json             ← Configuration déploiement Vercel
└── templates/
    ├── login.html          ← Page de connexion (split-screen institutionnel)
    ├── base.html           ← Layout commun (sidebar + topbar)
    ├── dashboard.html      ← Dashboard KPIs + 6 graphiques Chart.js
    ├── deces.html          ← Registre CRUD complet + filtres + export CSV
    └── rapport.html        ← Analyses avancées + tableau croisé causes×régions
```

---

## 🚀 Déploiement sur Vercel (3 étapes)

### Étape 1 — GitHub
```bash
cd deces-cm
git init
git add .
git commit -m "TP INF232 EC2 — Registre National des Décès"
git branch -M main
git remote add origin https://github.com/VOTRE_USER/deces-cm.git
git push -u origin main
```

### Étape 2 — Vercel
1. Aller sur **https://vercel.com/new**
2. Cliquer **"Import Git Repository"**
3. Sélectionner votre repo `deces-cm`
4. Cliquer **Deploy** ✅

### Étape 3 — URL obtenue
Vercel génère automatiquement : `https://deces-cm-xxxx.vercel.app`

---

## 🔑 Comptes de démonstration
| Rôle         | Email                          | Mot de passe |
|--------------|--------------------------------|--------------|
| Administrateur|idriss.kuepouo@facsciences-uy1 | Admin@2024   |
| Agent terrain | paul.atangana@deces-cm.cm     | Agent@2024   |

---

## 📊 Fonctionnalités

### Backend (app.py)
- **API REST** : GET/POST/PUT/DELETE sur `/api/deces`
- **Filtres** : région, cause, lieu, sexe, date min/max, recherche texte
- **Statistiques** : `/api/stats` — causes, lieux, régions, tranches d'âge, mensuel
- **Auth** : Sessions Flask + hash SHA-256 des mots de passe
- **Export** : `/api/export` — JSON complet
- **60 enregistrements** de démonstration pré-chargés

### Frontend
- **Dashboard** : 4 KPIs + 6 graphiques (ligne, donut, barres, polaire, barres horizontales)
- **Registre** : Tableau filtrable, formulaire complet (identité, lieu, cause, déclarant), export CSV
- **Rapports** : Filtrage par période, ranking causes, tableau croisé causes×régions, comparaison H/F
- **Design** : Thème sombre institutionnel, typographie Playfair Display + Karla
- **Responsive** : Mobile-first, sidebar rétractable

### Données collectées
- Identité du défunt (nom, âge, sexe, profession)
- Lieu géographique (région, arrondissement)
- Lieu de décès (hôpital, domicile, route, etc.)
- Cause principale + cause secondaire (21 causes)
- Date et heure du décès
- Déclarant (médecin, famille, autorité, etc.)
- Observations libres

---

## 🎓 Informations académiques
- **Cours** : INF232
- **TP** : EC2
- **Framework** : Python Flask
- **Hébergement** : Vercel (serverless Python)
- **Base de données** : In-memory (compatible Vercel sans BD externe)
