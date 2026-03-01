# PPI Compare

Confronta gli interattori di un gene tra letteratura e database, identificando gap di conoscenza e candidati per validazione sperimentale.

## Come usare
`/ppi-compare GENE_SYMBOL INTERACTOR1,INTERACTOR2,...`

Esempi:
- `/ppi-compare TP53 MDM2,ATM,CHEK2,BRCA1`
- `/ppi-compare EGFR SRC,GRB2,SHC1,PIK3R1,STAT3`

## Istruzioni per Claude

Analizza gli argomenti: $ARGUMENTS

- Il primo token è il GENE_SYMBOL
- Il secondo token (se presente) è la lista CSV degli interattori da letteratura

Se manca la lista interattori, chiedi all'utente:
> "Fornisci gli interattori noti dalla letteratura per **GENE** separati da virgola (es. GENE1,GENE2,GENE3)."

Esegui questi passi:

1. **Esegui lo script**:
   ```
   python ppi_analyzer/main.py --gene GENE --literature INTERACTORS
   ```

2. **Presenta il report di confronto** strutturato in tre sezioni:

   ### Interattori Confermati (overlap)
   - Lista geni presenti sia in letteratura che nei database
   - Per ognuno: score STRING e tipo di evidenza
   - Commento: "Questi sono i più affidabili perché confermati da più fonti"

   ### Gap nei Database (solo in letteratura)
   - Lista geni documentati in letteratura ma assenti da STRING
   - Per ognuno: possibile spiegazione (bassa espressione, contesto tissutale specifico, interazione debole o transiente)
   - Azione suggerita: submission a IntAct/STRING, o ricerca bibliografica aggiuntiva

   ### Nuove Interazioni da Database (non in letteratura)
   - Top 10 per score, con tipo di evidenza
   - Evidenzia quelli con evidenza sperimentale diretta (escore > 0)
   - Commento biologico: perché potrebbero essere rilevanti nel contesto del gene?

3. **Gap Analysis**:
   - Calcola e mostra la Jaccard similarity tra le due fonti
   - Identifica i top 3 candidati per validazione sperimentale
   - Spiega cosa significherebbe validare queste interazioni (metodo suggerito: Co-IP, Y2H, proximity ligation)

4. **Genera export Cytoscape**:
   ```
   python ppi_analyzer/main.py --gene GENE --literature INTERACTORS --cytoscape GENE_network.json
   ```
   Notifica all'utente i file CSV generati (nodi + archi) pronti per import in Cytoscape.

Nota: distingui sempre tra interazione FISICA (Co-IP, Y2H, pull-down) e FUNZIONALE (coexpression, textmining, pathway co-membership).
