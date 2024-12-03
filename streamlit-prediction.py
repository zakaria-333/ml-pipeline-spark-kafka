import streamlit as st
import numpy as np
import joblib

# Chemin vers le modèle sauvegardé
MODEL_PATH = "./sgd1.joblib"

# Charger le modèle
try:
    model = joblib.load(MODEL_PATH)
    st.success("Modèle chargé avec succès !")
except Exception as e:
    st.error("Erreur lors du chargement du modèle :")
    st.error(e)
    st.stop()

# Titre de l'application
st.title("Prédiction des émissions de CO2")

# Description
st.write("""
Cette application utilise un modèle de régression pour prédire les émissions de CO2
d'un véhicule en fonction de ses caractéristiques.
""")

# Formulaire pour entrer les données
st.header("Entrer les caractéristiques du véhicule")

engine_size = st.number_input("Taille du moteur (L)", min_value=0.0, value=1.5, step=0.1)
cylinders = st.number_input("Nombre de cylindres", min_value=1, value=4, step=1)
fuel_city = st.number_input("Consommation de carburant en ville (L/100km)", min_value=0.0, value=8.0, step=0.1)
fuel_hwy = st.number_input("Consommation de carburant sur autoroute (L/100km)", min_value=0.0, value=6.0, step=0.1)
fuel_comb = st.number_input("Consommation de carburant combinée (L/100km)", min_value=0.0, value=7.0, step=0.1)

# Sélection du type de carburant
fuel_type = st.selectbox("Type de carburant", ["D", "E", "N", "X", "Z"])

# Convertir le type de carburant en variables booléennes
fuel_types = {"D": [1, 0, 0, 0, 0], "E": [0, 1, 0, 0, 0], "N": [0, 0, 1, 0, 0], "X": [0, 0, 0, 1, 0], "Z": [0, 0, 0, 0, 1]}
fuel_type_encoded = fuel_types[fuel_type]

# Bouton pour prédire
if st.button("Prédire les émissions de CO2"):
    # Préparer les caractéristiques pour le modèle
    features = np.array([[
        engine_size, cylinders, fuel_city, fuel_hwy, fuel_comb, *fuel_type_encoded
    ]])
    
    # Faire la prédiction
    try:
        prediction = model.predict(features)
        st.success(f"Émissions de CO2 prédites : {prediction[0]:.2f} g/km")
    except Exception as e:
        st.error("Erreur lors de la prédiction :")
        st.error(e)
