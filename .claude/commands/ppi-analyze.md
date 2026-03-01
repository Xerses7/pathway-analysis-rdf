# PPI Analyze

Analizza le interazioni proteina-proteina per qualsiasi gene umano, aggregando dati da UniProt, STRING e WikiPathways.

## Come usare
`/ppi-analyze GENE_SYMBOL`

Esempi: `/ppi-analyze TP53` oppure `/ppi-analyze BRCA1` oppure `/ppi-analyze EGFR`

## Istruzioni per Claude

L'utente vuole analizzare il gene: $ARGUMENTS

Esegui questi passi in sequenza:

1. **Esegui lo script** dalla cartella del progetto:
   ```
   python ppi_analyzer/main.py --gene $ARGUMENTS
   ```

2. **Interpreta l'output** e presenta all'utente:
   - ID UniProt e nome completo della proteina
   - Top 5 GO terms con categoria (Molecular Function / Biological Process / Cellular Component)
   - Malattie associate in forma leggibile
   - Top 10 interattori STRING con score e tipo di evidenza, ordinati per score decrescente
   - Pathway WikiPathways se presenti

3. **Aggiungi un commento biologico**: spiega brevemente il ruolo del gene nel contesto della sua funzione principale e delle patologie associate, basandoti sui dati restituiti (non assumere contesto retinico o specifico).

4. **Suggerisci un prossimo passo**: "Vuoi confrontare questi interattori con la letteratura? Usa `/ppi-compare $ARGUMENTS INTERACTOR1,INTERACTOR2,...`"

Nota: lo script usa solo librerie standard Python, non richiede installazioni aggiuntive.
