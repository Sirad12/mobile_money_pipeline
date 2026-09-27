--- Nettoyage 
SELECT
    transaction_id,
    date_heure::timestamp AS date_transaction,
    type_transaction,
    montant::numeric AS montant,
    operateur,
    destinataire_id,
    expediteur_id,
    statut
FROM {{source('raw', 'transactions')}}