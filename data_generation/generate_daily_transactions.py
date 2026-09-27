import uuid #Genere des id uniques
import numpy as np  #Pour les distributions statisiques
import pandas as pd #Pour construire le dataframe et l'exporter en csv
from faker import Faker #Genere des donnees fictives realistes
from datetime import datetime, timedelta
import random

faker = Faker()

TYPES_TRANSACTION = ["depot", "retrait", "transfert", "paiement_marchand", "recharge"]
OPERATEURS = ["Orange Money", "Wave"]

# Cette fonction permet de génèrer un nombre suivant 
# la distribution log-normale. Les paramètres mean=8.5 
# et sigma=1.0 sont choisis empiriquement pour que la majorité 
# des montants tombent dans une fourchette réaliste (quelques milliers de XOF), 
# avec quelques valeurs plus élevées de temps en temps.
def generer_montant():
    montant = np.random.lognormal(mean=8.5, sigma=1.0)
    return round(min(montant, 200000), 0)



def generer_transaction(date_transaction):
    return {
        "transaction_id": str(uuid.uuid4()),
        "date_heure": date_transaction,
        "type_transaction": random.choices(TYPES_TRANSACTION, weights=[15,15,35,25,10])[0], #On encode les frequences realiste (transferts 35% etc)
        "montant": generer_montant(),
        "operateur": random.choices(OPERATEURS),
        "expediteur_id": faker.uuid4(), #pour les IDs expéditeur/destinataire — simule des identifiants clients uniques, sans utiliser de vraies données personnelles
        "destinataire_id": faker.uuid4(),
        "statut": random.choices(["reussi", "echoue"], weights=[96,4])[0]
    }

# Au lieu de répartir les transactions uniformément sur 24h, 
# on veut simuler une activité qui suit un rythme réaliste : peu d'activité 
# la nuit (0h-6h), pic en journée (8h-20h), avec éventuellement un pic plus
# fort certains jours (fin de mois, vendredi).
def generer_heure_realiste():
    heure = np.random.normal(loc=14, scale=4) #sécurité pour éviter qu'une valeur générée dépasse 23h ou descende sous 0h
    heure = max(0, min(23, heure))
    minute = random.randint(0, 59)
    seconde = random.randint(0, 59)
    return int(heure), minute, seconde


def generer_transactions_du_jour(date_jour, nb_transactions_base=500):
    est_fin_du_mois = date_jour.day >= 28 #j'ai approximé la fin de mois par day >= 28 pour que ça fonctionne quel que soit le mois, plutôt que de gérer chaque cas particulier.
    est_vendredi = date_jour.weekday() == 4

    nb_transactions = nb_transactions_base
    if est_fin_du_mois:
        nb_transactions = int(nb_transactions * 1.4)
    if est_vendredi:
        nb_transactions = int(nb_transactions * 1.2)

    transactions = []
    for _ in range(nb_transactions):
        h, m, s = generer_heure_realiste()
        date_heure = date_jour.replace(hour=h, minute=m, second=s)
        transactions.append(generer_transaction(date_heure))
    
    return pd.DataFrame(transactions)

# est_fin_de_mois / est_vendredi — deux booléens qui détectent 
# des jours "spéciaux". date_jour.weekday() == 4 correspond au vendredi (en Python, weekday() retourne 0 pour lundi, donc 4 = vendredi)

# Les multiplicateurs (* 1.4, * 1.2) — c'est ici qu'on simule les pics : 
# +40% de transactions en fin de mois (salaires), +20% le vendredi. 
# Ces chiffres sont arbitraires mais défendables.

def generer_historique(date_debut, nb_jours, nb_transactions_base=500):
    toutes_transactions = []

    for i in range(nb_jours):
        date_jour = date_debut + timedelta(days=i)
        df_jour = generer_transactions_du_jour(date_jour, nb_transactions_base)
        toutes_transactions.append(df_jour)
    
    return pd.concat(toutes_transactions, ignore_index=True)

if __name__ == "__main__":
    #ça donne un historique de 3 mois d'un coup
    date_debut = datetime(2026, 6, 1)
    nb_jours = 90
    
    df_historique = generer_historique(date_debut, nb_jours)
    
    df_historique.to_csv("transactions_historique.csv", index=False)
    print(f"{len(df_historique)} transactions générées sur {nb_jours} jours")
    print(df_historique.head())
