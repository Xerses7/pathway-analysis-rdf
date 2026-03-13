# Gene Expression

Recupera il profilo di espressione tessutale, la localizzazione subcellulare e il contesto di pathway per qualsiasi proteina umana, integrando dati da UniProt e WikiPathways.

## Come usare
`/gene-expression GENE_SYMBOL`

Esempi:
- `/gene-expression TP53`
- `/gene-expression EGFR`
- `/gene-expression CFTR`

## Istruzioni per Claude

Il gene da analizzare è: $ARGUMENTS

### Step 1: Recupera espressione tessutale da UniProt

Esegui su `https://sparql.uniprot.org/sparql`:

```sparql
PREFIX up: <http://purl.uniprot.org/core/>
PREFIX taxon: <http://purl.uniprot.org/taxonomy/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?comment
WHERE {
  ?protein a up:Protein ;
           up:organism taxon:9606 ;
           up:encodedBy ?gene ;
           up:annotation ?annotation .
  ?gene skos:prefLabel ?geneName .
  ?annotation a up:Tissue_Specificity_Annotation ;
              rdfs:comment ?comment .
  FILTER (?geneName = "GENE_SYMBOL")
}
```

### Step 2: Recupera localizzazione subcellulare da UniProt

Esegui su `https://sparql.uniprot.org/sparql`:

```sparql
PREFIX up: <http://purl.uniprot.org/core/>
PREFIX taxon: <http://purl.uniprot.org/taxonomy/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?locComment
WHERE {
  ?protein a up:Protein ;
           up:organism taxon:9606 ;
           up:encodedBy ?gene ;
           up:annotation ?annotation .
  ?gene skos:prefLabel ?geneName .
  ?annotation a up:Subcellular_Location_Annotation ;
              rdfs:comment ?locComment .
  FILTER (?geneName = "GENE_SYMBOL")
}
```

### Step 3: Recupera pathway WikiPathways

Esegui su `https://sparql.wikipathways.org/sparql`:

```sparql
PREFIX wp: <http://vocabularies.wikipathways.org/wp#>
PREFIX dc: <http://purl.org/dc/elements/1.1/>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT DISTINCT ?wpid ?pathwayTitle
WHERE {
  ?geneProduct a wp:GeneProduct ;
               rdfs:label ?geneLabel ;
               dcterms:isPartOf ?pathway .
  ?pathway a wp:Pathway ;
           dc:title ?pathwayTitle ;
           dcterms:identifier ?wpid ;
           wp:organismName "Homo sapiens" .
  FILTER (UCASE(?geneLabel) = UCASE("GENE_SYMBOL"))
}
ORDER BY ?pathwayTitle
```

### Step 4: Analisi biologica integrata

Combina i dati dei tre step e interpreta:

1. **Espressione tessutale**: in quali tessuti è espressa la proteina? Alta/media/bassa? Espressione ubiquitaria vs tessuto-specifica?
2. **Compartimento subcellulare**: dove si trova la proteina? Il compartimento implica funzioni specifiche:
   - Membrana plasmatica → recettore, canale, adesione
   - Nucleo → trascrizione, riparazione DNA
   - Mitocondrio → metabolismo energetico, apoptosi
   - Reticolo endoplasmatico → sintesi/folding proteine, segnalazione Ca²⁺
   - Citoplasma → segnalazione, metabolismo
   - Secreted / extracellulare → matrice, segnalazione paracrina
3. **Pathway membership**: quali processi biologici coinvolgono questa proteina?
4. **Coerenza dati**: l'espressione tessutale è coerente con i pathway e la localizzazione?

### Step 5: Report strutturato

#### A. Profilo di Espressione Tessutale
Tabella con: tessuto | livello espressione (inferito dal testo UniProt) | note

Categorie di espressione da UniProt (inferire dal testo):
- **Ubiquitaria**: "widely expressed", "expressed in all tissues"
- **Tessuto-specifica**: indicato esplicitamente ("expressed in liver", "brain-specific")
- **Inducibile**: "expressed upon stimulation", "upregulated in..."

#### B. Localizzazione Subcellulare
Lista dei compartimenti con note su eventuali condizioni di traslocazione (es. "nucleare in risposta a danno DNA").

#### C. Pathway Membership (WikiPathways)
Tabella: WP_ID | Titolo pathway | Categoria (segnalazione / metabolismo / immunità / altro)

#### D. Implicazioni per la Patologia
In base all'espressione tessutale e alla localizzazione:
- Quali tessuti sono più vulnerabili a varianti LOF?
- Quale tipo di patologia ci si aspetta (tissutale, metabolica, oncologica)?

Proponi: "Per vedere le varianti patologiche del gene, usa `/variant-annotate $ARGUMENTS`"
Per analisi di pathway su un set di geni correlati, usa `/pathway-enrich GENE1,GENE2,...`"

### Note tecniche
- `up:Tissue_Specificity_Annotation` contiene testo libero (parsare per estrarre tessuti)
- Se il gene non ha annotazioni di espressione in UniProt, è probabile che sia poco caratterizzato: suggerire Human Protein Atlas (proteinatlas.org)
- WikiPathways copre 1057+ pathway umani curati dalla community
