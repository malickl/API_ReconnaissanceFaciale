from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import os, face_recognition

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'uploads'

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/compare', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Récupération des deux images (même si vide, on aura un objet, mais .filename peut être '')
        img1 = request.files.get('img1')
        img2 = request.files.get('img2')

        # Vérifier si les clés sont bien présentes dans request.files
        if 'img1' not in request.files or 'img2' not in request.files:
            message = "Veuillez sélectionner 2 fichiers avant de soumettre."
            return render_template('index.html', message=message)

        # Vérifier si les noms de fichier ne sont pas vides
        if img1.filename == '' or img2.filename == '':
            message = "Veuillez sélectionner 2 fichiers valides (non vides)."
            return render_template('index.html', message=message)

        # Sécuriser le nom des fichiers et construire le chemin
        filename1 = secure_filename(img1.filename)
        filename2 = secure_filename(img2.filename)
        save_path1 = os.path.join(app.config['UPLOAD_FOLDER'], filename1)
        save_path2 = os.path.join(app.config['UPLOAD_FOLDER'], filename2)

        # Sauvegarder les fichiers
        img1.save(save_path1)
        img2.save(save_path2)

        try:
            # Charger les images via face_recognition
            img1_data = face_recognition.load_image_file(save_path1)
            img2_data = face_recognition.load_image_file(save_path2)

            # Vérifier si des visages sont détectés
            img1_encodings = face_recognition.face_encodings(img1_data)
            img2_encodings = face_recognition.face_encodings(img2_data)

            if img1_encodings and img2_encodings:
                # Extraire les encodages (on prend le premier visage trouvé)
                img1_encoding = img1_encodings[0]
                img2_encoding = img2_encodings[0]

                # Comparer les visages
                results = face_recognition.compare_faces([img1_encoding], img2_encoding)

                if results[0]:
                    message = "C'est la même personne."
                else:
                    message = "Ce ne sont pas les même personne."
            else:
                message = "Aucun visage détecté dans l'une (ou les deux) des images."
            
            return render_template('index.html', message=message)

        finally:
            # Supprimer les fichiers sauvegardés après traitement
            os.remove(save_path1)
            os.remove(save_path2)

    # Si on arrive ici autrement qu'en POST
    return redirect(url_for('index', message=message))

if __name__ == '__main__':
    app.run(debug=True)
