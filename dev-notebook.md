# Ultimate-GUI-YouTube-Downloader

# Étapes de développement du projet

## GitHub & GitKraken

Pour synchroniser votre dossier local **"Ultimate-GUI-YouTube-downloader"** avec le dépôt GitHub existant en utilisant GitKraken, voici les étapes détaillées :

**Étape 1 : Vérifier que le projet local est un dépôt Git**

1. **Ouvrez GitKraken.**

2. Cliquez sur **"Open a Repository"** (Ouvrir un dépôt) dans la barre latérale.

3. Naviguez jusqu'à votre dossier local "Ultimate-GUI-YouTube-downloader" et ouvrez-le.

   - Si GitKraken affiche une erreur indiquant qu'il ne s'agit pas d'un dépôt Git :

     - Initialisez Git en ouvrant un terminal dans le dossier et exécutez :

       ```bash
       git init
       ```

     - Ensuite, rechargez le dossier dans GitKraken.

**Étape 2 : Connecter votre projet local au dépôt GitHub**

1. **Assurez-vous que votre dépôt GitHub est prêt** :
   - Le dépôt **"Ultimate-GUI-YouTube-downloader"** doit déjà exister sur GitHub.
   - Copiez l'URL HTTPS ou SSH de ce dépôt GitHub (par exemple : `https://github.com/votre-utilisateur/Ultimate-GUI-YouTube-downloader.git`).
2. **Ajoutez l'URL distante dans GitKraken** :
   - Une fois votre dépôt local ouvert dans GitKraken :
     1. Accédez à l'onglet **Remotes** dans la barre latérale droite.
     2. Cliquez sur l'icône **+** à côté de "Remotes".
     3. Collez l'URL du dépôt GitHub (ou sélectionnez "GitHub" si votre compte est lié à GitKraken ou qu'il n'existe pas de dépôt sur GitHub).
     4. Donnez un nom à votre remote (par défaut, "origin").
     5. Cliquez sur **Save**.

**Étape 3 : Préparer le contenu local pour le push**

1. Ajoutez les fichiers locaux au suivi Git :
   - Cliquez sur l'onglet **Working Directory**.
   - Si vous voyez vos fichiers listés dans la section **Unstaged Files**, cliquez sur **Stage All Changes** pour les ajouter à l'index.
2. Effectuez le commit :
   - Ajoutez un message dans la section **Commit** (par exemple, "Initial commit").
   - Cliquez sur **Stage Changes to Commit**.

**Étape 4 : Pusher le contenu vers GitHub**

1. Cliquez sur le bouton **Push** dans la barre supérieure.
2. Si vous recevez un message indiquant que la branche distante n'existe pas encore :
   - Sélectionnez **Push to Remote**.
   - Confirmez la création de la branche distante (par exemple, "main" ou "master").
3. GitKraken synchronisera alors vos fichiers locaux avec le dépôt GitHub.

**Étape 5 : Vérifiez la synchronisation**

1. Rendez-vous sur votre dépôt GitHub et assurez-vous que les fichiers sont correctement ajoutés.
2. Vous pouvez maintenant utiliser GitKraken pour gérer les modifications futures (pull, push, merge, etc.).

**Conseils pratiques**

- Si vous voulez remplacer le contenu GitHub existant par votre version locale :
  - Cochez l'option **Force Push** lors du push (uniquement si vous êtes sûr de vouloir écraser l'historique existant).
  - Pour activer Force Push :
    1. Cliquez sur le menu à côté de **Push**.
    2. Sélectionnez **Force Push**.

## Initialisation du projet

### Création de la structure du projet

### Création de l'environnement virtuel Python

```bash
# Créer un environnement virtuel dans un dossier appelé 'venv'
python3 -m venv venv

# Activer l'environnement virtuel
source venv/bin/activate  # Sur Linux/Mac

# Installer les dépendances
pip install -r requirements.txt
```

### Installation des packages requis

```bash
# Installer customtkinter
pip install customtkinter

# Installer pytubefix
pip install pytubefix

# Actualiser le fichier requirements.txt
pip freeze > requirements.txt
```

