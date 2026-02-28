# PPI Analyze

Analizza le interazioni proteina-proteina per un gene, aggregando dati da UniProt, STRING e WikiPathways.

## Come usare
`/ppi-analyze GENE_SYMBOL`

Esempio: `/ppi-analyze EYS` oppure `/ppi-analyze AIPL1`

## Istruzioni per Claude

L'utente vuole analizzare il gene: $ARGUMENTS

Esegui questi passi in sequenza:

1. **Esegui lo script** nella cartella del progetto:
   ```
   cd "C:\Users\d_pir\Documents\Prog\Pathway retina RDF\ppi_analyzer"
   python main.py --gene $ARGUMENTS
   ```

2. **Interpreta l'output** e presenta all'utente:
   - ID UniProt e nome della proteina
   - Top 5 GO terms con categoria (Molecular Function / Biological Process / Cellular Component)
   - Malattie associate in forma leggibile
   - Top 10 interattori STRING con score e tipo di evidenza, ordinati per score decrescente
   - Pathway WikiPathways se presenti

3. **Aggiungi un commento biologico**: spiega brevemente il ruolo del gene nel contesto della retina o della patologia associata, basandoti sui dati restituiti.

4. **Suggerisci un prossimo passo**: es. "Vuoi confrontare questi interattori con la letteratura? Usa /ppi-compare"

Nota: lo script usa librerie standard Python, non richiede installazioni.
