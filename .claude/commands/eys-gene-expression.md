# Gene Expression — EYS (Retina)

> **Skill ottimizzata per geni espressi nella retina, con focus su fotorecettori, RPE e ciglio retinico.**
> L'analisi biologica interpreta l'espressione nel contesto di rod/cone photoreceptors, matrice interphotoreceptor (IPM) e pathway di Retinitis Pigmentosa.
> Per profilo di espressione generico su qualsiasi gene usa `/gene-expression GENE`.

Recupera il profilo di espressione retinica, la localizzazione subcellulare nei fotorecettori e la partecipazione ai pathway retinici per geni associati a RP.

## Come usare
`/eys-gene-expression GENE_SYMBOL`

Esempi:
- `/eys-gene-expression EYS`
- `/eys-gene-expression AIPL1`
- `/eys-gene-expression RHO`

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

### Step 3: Recupera pathway retinici da WikiPathways

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

### Step 4: Analisi dell'espressione nel contesto retinico

Interpreta i dati con focus sulla biologia della retina:

**Mappa di espressione nei tipi cellulari retinici:**
```
Retina — Strati cellulari e tipi esprimenti GENE:

  [Segmenti esterni rod/cone] ← EYS, RHO, AIPL1 (localizzazione attesa)
  [Ciglio di connessione]      ← RPGR, CEP290, CNGB1
  [Corpo cellulare fotorecettore]
  [Sinapsi fotorecettore]
  [Cellule bipolari]
  [Cellule gangliari]
  [RPE (Retinal Pigment Epithelium)] ← BEST1, RPE65, ABCA4

  IPM (Matrice interphotoreceptor):   ← EYS, SPACR, IMPG1/2
```

**Per il gene richiesto**, verifica in quale compartimento retinico si localizza e quale funzione svolge:
- **Rod vs Cone specifico**: interessa principalmente visione scotopica o fotopica?
- **Ciglio di connessione**: implicato in ciliopatia? Trasporto IFT?
- **IPM**: ruolo strutturale nella matrice che circonda i segmenti esterni?
- **Sinapsi**: ruolo nella trasmissione del segnale visivo?

### Step 5: Confronto con altri geni RP correlati

Crea una tabella comparativa con i principali geni RP per localizzazione e funzione:

| Gene | Localizzazione principale | Tipo RP | Funzione chiave |
|------|--------------------------|---------|-----------------|
| EYS | IPM + segmenti esterni | RP25 (AR) | Adesione extracellulare, organizzazione IPM |
| RHO | Dischi segmenti esterni rod | RP4 (AD) | Fototransduction (opsina rod) |
| AIPL1 | Fotorecettori (rod > cone) | LCA4 (AR) | Chaperone PDE6 |
| RPGR | Ciglio di connessione | RP3 (XL) | Trasporto cigliare, localizzazione opsine |
| ABCA4 | Dischi segmenti esterni rod/cone | RP19 (AR) | Clearance all-trans-retinal |
| PRPF31 | Nucleo fotorecettori | RP11 (AD) | Splicing RNA |

Posiziona il gene richiesto in questo schema.

### Step 6: Report strutturato

#### A. Profilo di Espressione Tessutale e Retinica
- Espressione sistemica (da UniProt: tessuti extra-retinici se presenti)
- Espressione retinica: rod-specifica / cone-specifica / ubiquitaria nella retina / RPE
- Onset di espressione: fetale, neonatale, adulta?

#### B. Localizzazione Subcellulare nei Fotorecettori
Lista compartimenti con interpretazione funzionale nel contesto retinico:
- Ciglio → implicato in ciliopatia
- Segmenti esterni → struttura dei dischi, fototransduction
- IPM → adesione, organizzazione extracellulare
- Membrana basale → interazione RPE-fotorecettori

#### C. Pathway Retinici (WikiPathways)
Tabella pathway con focus su:
- Fototransduction
- Retinal degeneration
- Visual cycle
- Ciliopathy pathways
- RPE metabolism

#### D. Pattern di Degenerazione Atteso
In base all'espressione (rod-specifica vs cone-specifica vs ubiquitaria):
- **Rod-specifica**: perdita visione notturna prima → RP classica (rod-cone dystrophy)
- **Cone-specifica**: perdita visione centrale prima → cone-rod dystrophy
- **Ubiquitaria nella retina**: perdita generalizzata
- **RPE-specifica**: degenerazione secondaria dei fotorecettori per mancanza di supporto trofico

### Note sul gene EYS
EYS è espresso specificamente nei segmenti esterni dei fotorecettori e nella matrice IPM.
- **Rod e cone**: espresso in entrambi, ma perdita rod-predominante in RP25
- **IPM**: proteina extracellulare con domini LamG — funzione adesiva/strutturale
- **Ciglio**: non direttamente localizzato nel ciglio, ma influenza indirettamente la sua integrità
- **Assenza in topo**: il gene EYS è assente nel genoma murino — modelli animali limitati (zebrafish, Drosophila)
- Per analisi PPI dei geni retinici correlati: `/eys-ppi-compare EYS GRK7,AIPL1,DAG1,POMGNT1`
