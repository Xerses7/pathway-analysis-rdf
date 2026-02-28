# PPI Compare

Confronta gli interattori di un gene tra letteratura e database, identificando gap di conoscenza e candidati per validazione sperimentale.

## Come usare
`/ppi-compare GENE_SYMBOL INTERACTOR1,INTERACTOR2,...`

Esempio: `/ppi-compare EYS GRK7,AIPL1,DAG1,POMGNT1,POMT2,PROM1,KIF19,PDE6D`

Se non vengono forniti interattori, usa quelli di default del gene EYS dal PDF.

## Istruzioni per Claude

Analizza gli argomenti: $ARGUMENTS

- Il primo token è il GENE (es. EYS)
- Il secondo token (se presente) è la lista di interattori da letteratura separati da virgola

Se manca la lista interattori e il gene è EYS, usa: GRK7,AIPL1,DAG1,POMGNT1,POMT2,PROM1,KIF19,PDE6D

Esegui questi passi:

1. **Esegui lo script**:
   ```
   cd "C:\Users\d_pir\Documents\Prog\Pathway retina RDF\ppi_analyzer"
   python main.py --gene GENE --literature INTERACTORS
   ```

2. **Presenta il report di confronto** strutturato in tre sezioni:

   ### Interattori Confermati (overlap)
   - Lista geni presenti sia in letteratura che nei database
   - Per ognuno: score STRING e tipo di evidenza
   - Commento: "Questi sono i più affidabili perché confermati da più fonti"

   ### Gap nei Database (solo in letteratura)
   - Lista geni documentati in letteratura ma assenti da STRING
   - Per ognuno: spiegazione biologica del perché l'interazione è nota
   - Azione suggerita: submission a IntAct/STRING, o ricerca bibliografica

   ### Nuove Interazioni da Database (non in letteratura)
   - Top 10 per score, con evidenza
   - Evidenzia quelli con evidenza sperimentale (escore > 0)
   - Commento biologico: perché potrebbero essere interessanti?

3. **Gap Analysis**:
   - Calcola e mostra la Jaccard similarity tra le due fonti
   - Identifica i top 3 candidati per validazione sperimentale
   - Spiega cosa significherebbe validare queste interazioni

4. **Genera export Cytoscape**:
   ```
   python main.py --gene GENE --literature INTERACTORS --cytoscape GENE_network.json
   ```
   Notifica all'utente i file CSV generati (nodi + archi) pronti per import in Cytoscape.

Nota: distingui sempre tra interazione FISICA (Co-IP, Y2H) e FUNZIONALE (coexpression, textmining).
