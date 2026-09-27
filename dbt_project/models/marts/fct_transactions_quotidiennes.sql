SELECT
    DATE(date_transaction) AS jour,
    type_transaction,
    operateur,
    COUNT(*) FILTER (WHERE statut = 'reussi') AS nombre_transactions,
    SUM(montant) FILTER (WHERE statut = 'reussi') AS montant_total,
    ROUND(AVG(montant) FILTER (WHERE statut = 'reussi'), 2) AS montant_moyen,
    COUNT(*) FILTER (WHERE statut = 'echoue') AS nombre_echecs
FROM {{ ref('stg_transactions') }}
GROUP BY DATE(date_transaction), type_transaction, operateur
ORDER BY jour, type_transaction