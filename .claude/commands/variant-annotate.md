# Variant Annotate

Recupera e classifica tutte le varianti genetiche di un gene umano da UniProt: tipo di mutazione (missense, frameshift, nonsense, splicing), posizione sulla proteina, patologia associata e distribuzione sulle regioni funzionali.

## Come usare
`/variant-annotate GENE_SYMBOL`

Esempi:
- `/variant-annotate TP53`
- `/variant-annotate BRCA1`
- `/variant-annotate CFTR`

## Istruzioni per Claude

Il gene da analizzare è: $ARGUMENTS

### Step 1: Recupera tutte le varianti da UniProt

Esegui su `https://sparql.uniprot.org/sparql`:

```sparql
PREFIX up: <http://purl.uniprot.org/core/>
PREFIX taxon: <http://purl.uniprot.org/taxonomy/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX faldo: <http://biohackathon.org/resource/faldo#>

SELECT ?comment ?begin
WHERE {
  ?protein a up:Protein ;
           up:organism taxon:9606 ;
           up:encodedBy ?gene ;
           up:annotation ?annotation .
  ?gene skos:prefLabel ?geneName .
  ?annotation a up:Natural_Variant_Annotation ;
              rdfs:comment ?comment ;
              up:range ?range .
  ?range faldo:begin ?beginPos .
  ?beginPos faldo:position ?begin .
  FILTER (?geneName = "GENE_SYMBOL")
}
ORDER BY ?begin
```

### Step 2: Recupera le patologie associate alla proteina

Esegui su `https://sparql.uniprot.org/sparql`:

```sparql
PREFIX up: <http://purl.uniprot.org/core/>
PREFIX taxon: <http://purl.uniprot.org/taxonomy/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?diseaseComment
WHERE {
  ?protein a up:Protein ;
           up:organism taxon:9606 ;
           up:encodedBy ?gene ;
           up:annotation ?annotation .
  ?gene skos:prefLabel ?geneName .
  ?annotation a up:Disease_Annotation ;
              rdfs:comment ?diseaseComment .
  FILTER (?geneName = "GENE_SYMBOL")
}
```

### Step 3: Classifica le varianti per tipo

Analizza il campo `comment` di ciascuna variante usando questi pattern:

| Tipo | Pattern da cercare nel comment | Effetto atteso |
|------|-------------------------------|----------------|
| **Missense** | "X → Y" dove X,Y sono aminoacidi (es. "Ala → Val") | Sostituzione aa, effetto variabile |
| **Nonsense** | "→ Stop" oppure "→ *" | Troncamento prematuro, perdita di funzione |
| **Frameshift** | contiene "frameshift" | Cambio reading frame, LOF quasi certo |
| **Delezione in-frame** | "del" senza "frameshift" | Perdita aa, impatto sul dominio |
| **Inserzione in-frame** | "ins" senza "frameshift" | Aggiunta aa, alterazione strutturale |
| **Splicing** | contiene "splice" o "aberrant" | Isoforma aberrante |
| **VUS** | contiene "uncertain" o "unknown" | Significato incerto, serve validazione |

Conta le varianti per tipo e calcola le percentuali.

### Step 4: Mappa le varianti sulla struttura proteica

Distribuisci le varianti lungo la sequenza proteica con una rappresentazione testuale:

```
Proteina GENE (N aa totali):
|─────────────────────────────────────────────────────|
0                                                     N

Varianti LOF (nonsense + frameshift):
  ▼        ▼  ▼     ▼         ▼   ▼
  pos1     pos2     pos3       ...

Missense:
  ·   ·  · ·      ·   ··  ·
  pos1          ...

Densità (hotspot): regione con > 2 varianti/50 aa
```

Se disponibili in UniProt, annota anche i domini sulla stessa mappa.

### Step 5: Report strutturato

#### A. Riepilogo statistico
```
Gene:             GENE_SYMBOL
Varianti totali:  N
  Missense:       N (XX%)
  Nonsense:       N (XX%)
  Frameshift:     N (XX%)
  Delezione:      N (XX%)
  Inserzione:     N (XX%)
  Splicing:       N (XX%)
  VUS/altro:      N (XX%)

Loss-of-Function (LOF) totali: N (nonsense + frameshift + splicing)
```

#### B. Varianti associate a patologia
Tabella: posizione | sostituzione | tipo | patologia associata

#### C. Hotspot mutazionali
Regioni con densità di varianti superiore alla media — indicatori di funzione essenziale.

#### D. Varianti LOF prioritarie
Lista completa nonsense + frameshift: massima probabilità di effetto patologico, ideali per studi funzionali.

### Note tecniche
- UniProt riporta solo varianti con evidenza sperimentale o curata (Swiss-Prot reviewed)
- Il tipo di variante si inferisce dal testo del campo `comment`: parsare manualmente
- Per varianti ClinVar non ancora in UniProt, consultare direttamente clinvar.ncbi.nlm.nih.gov
- Per analisi di impatto PTM su queste varianti: `/ptm-variant-impact $ARGUMENTS`
- Per analisi di sequon N-glicosilazione a rischio: `/sequon-scan $ARGUMENTS`
