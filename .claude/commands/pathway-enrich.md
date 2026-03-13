# Pathway Enrich

Data una lista di geni umani, identifica i pathway WikiPathways che li contengono, calcola la copertura per pathway e individua i processi biologici rilevanti del gene set.

## Come usare
`/pathway-enrich GENE1,GENE2,GENE3,...`

Esempi:
- `/pathway-enrich TP53,MDM2,ATM,CHEK2,BRCA1`
- `/pathway-enrich EGFR,SRC,PIK3CA,AKT1,MTOR,PTEN`
- `/pathway-enrich BRCA1,BRCA2,RAD51,PALB2,CHEK2`

## Istruzioni per Claude

La lista di geni da analizzare è: $ARGUMENTS

Splitta `$ARGUMENTS` per virgola per ottenere la lista di geni. Normalizza in maiuscolo tutti i simboli.

### Step 1: Query pathway enrichment su WikiPathways

Costruisci la lista quotata in maiuscolo: `"GENE1","GENE2",...`

Esegui su `https://sparql.wikipathways.org/sparql`:

```sparql
PREFIX wp: <http://vocabularies.wikipathways.org/wp#>
PREFIX dc: <http://purl.org/dc/elements/1.1/>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT DISTINCT ?wpid ?pathwayTitle ?geneLabel
WHERE {
  ?geneProduct a wp:GeneProduct ;
               rdfs:label ?geneLabel ;
               dcterms:isPartOf ?pathway .
  ?pathway a wp:Pathway ;
           dc:title ?pathwayTitle ;
           dcterms:identifier ?wpid ;
           wp:organismName "Homo sapiens" .
  FILTER (UCASE(?geneLabel) IN (GENE_LIST))
}
ORDER BY ?wpid ?geneLabel
```

Dove `GENE_LIST` è la lista dei simboli in maiuscolo tra virgolette, separati da virgola.

### Step 2: Calcola coverage per pathway

Per ciascun pathway restituito, calcola:

| Metrica | Formula |
|---------|---------|
| **Hit** | numero di geni dell'input trovati in quel pathway |
| **Coverage** | Hit ÷ totale geni input × 100 |

Ordina per coverage decrescente.

### Step 3: Classifica i pathway per categoria biologica

| Categoria | Parole chiave nel titolo pathway |
|-----------|----------------------------------|
| Segnalazione | signaling, receptor, kinase, cascade |
| Metabolismo | metabolism, biosynthesis, degradation, cycle |
| Ciclo cellulare | cell cycle, DNA repair, apoptosis, checkpoint |
| Immunità | immune, inflammation, cytokine, interferon |
| Trascrizione | transcription, chromatin, epigenetic |
| Trasporto | transport, vesicle, trafficking, secretion |
| Neurologia | neuron, synaptic, neural, brain |
| Sviluppo | development, differentiation, stem cell |

### Step 4: Identifica core pathway e geni hub

**Core pathway**: pathway con coverage > 50% — molto probabilmente funzionalmente rilevanti.

**Gene hub**: geni dell'input che compaiono nel maggior numero di pathway — probabili regolatori centrali del processo biologico.

### Step 5: Report strutturato

#### A. Ranking Pathway (top 20)
Tabella: WP ID | Titolo | Geni trovati | Coverage (%) | Categoria

#### B. Core Pathway (coverage ≥ 50%)
Lista dettagliata con tutti i geni dell'input trovati in ciascun pathway.

#### C. Gene Hub
Tabella: gene | numero di pathway in cui compare | pathway principali

#### D. Gap Analysis — Geni senza pathway
Lista geni dell'input NON trovati in nessun pathway WikiPathways.
Possibili cause: gene poco caratterizzato, pathway non ancora curato, simbolo alternativo usato in WikiPathways.
Suggerimento: verificare simboli alternativi su HGNC o cercare manualmente in WikiPathways.

#### E. Riepilogo funzionale
Interpretazione biologica: quali processi biologici dominano nel gene set? Esiste un tema funzionale coerente (es. "DNA damage response", "receptor tyrosine kinase signaling")?

### Note tecniche
- WikiPathways è case-sensitive per i label geni: usa sempre UCASE() nel FILTER
- Alcuni geni hanno simboli alternativi in WikiPathways (es. HGNC vs Ensembl): in caso di 0 hit, provare varianti del simbolo
- Per approfondire l'espressione di un gene specifico: `/gene-expression GENE`
- Per analisi PPI dei geni del set: `/ppi-analyze GENE`
