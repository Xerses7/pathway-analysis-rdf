# Pathway Enrich — EYS (RP gene panel)

> **Skill ottimizzata per pathway enrichment nel contesto di Retinitis Pigmentosa.**
> Include un set di riferimento predefinito di geni RP noti. Interpreta i risultati con focus su pathway retinici: fototransduction, ciliopatia, visual cycle, RPE metabolism.
> Per pathway enrichment generico su qualsiasi gene set usa `/pathway-enrich GENE1,GENE2,...`.

Identifica i pathway WikiPathways rilevanti per un gene set retinico/RP, con confronto rispetto al pannello di geni RP noti e interpretazione nel contesto della degenerazione retinica.

## Come usare
`/eys-pathway-enrich [GENE1,GENE2,...]`

Esempi:
- `/eys-pathway-enrich EYS,AIPL1,DAG1,POMGNT1,GRK7,PDE6D` (interattori EYS da letteratura)
- `/eys-pathway-enrich` (usa il pannello RP completo come default)
- `/eys-pathway-enrich RHO,RPGR,PRPF31,ABCA4,CNGA1,CNGB1`

## Istruzioni per Claude

La lista di geni da analizzare è: $ARGUMENTS

Se `$ARGUMENTS` è vuoto, usa il **pannello RP di default**:
```
EYS,RHO,RPGR,PRPF31,ABCA4,AIPL1,CRB1,CNGA1,CNGB1,CRX,IMPDH1,
NR2E3,NRL,PDE6A,PDE6B,RDS,RLBP1,RP1,RP2,TULP1,USH2A,CERKL,
SNRNP200,PRPF8,PRPF3,PRPF6,RP9,TOPORS,KLHL7,FAM161A,DHDDS,
IDH3B,RBP3,LRAT,RPE65,BEST1
```

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

### Step 2: Calcola coverage e prioritizza pathway retinici

Per ciascun pathway restituito, calcola:
- **Hit**: geni dell'input trovati nel pathway
- **Coverage**: Hit ÷ totale geni input × 100

Poi **prioritizza** i pathway in base alla rilevanza per RP usando questi pesi:

| Categoria pathway | Rilevanza RP | Peso |
|-------------------|-------------|------|
| Phototransduction | Massima | ★★★★★ |
| Visual cycle / retinoid metabolism | Massima | ★★★★★ |
| Ciliopathy / cilium assembly | Alta | ★★★★ |
| Photoreceptor / retinal degeneration | Alta | ★★★★ |
| RNA splicing / spliceosome | Alta (RP11,17,18…) | ★★★ |
| Glycosylation / ER stress / UPR | Media | ★★★ |
| ECM / cell adhesion | Media (EYS) | ★★★ |
| Metabolismo energetico | Bassa | ★★ |
| Altro | Bassa | ★ |

### Step 3: Confronto con altri geni RP non nel set

Cerca i pathway trovati per verificare se contengono **altri geni RP noti** non presenti nell'input — indica potenziali candidati per interazione funzionale.

Geni RP di riferimento da verificare nei pathway trovati:
`EYS, RHO, RPGR, PRPF31, ABCA4, AIPL1, CRB1, CNGA1, CNGB1, PDE6A, PDE6B, TULP1, USH2A, CERKL`

### Step 4: Analisi pathway ciliopatia (se rilevante)

Se il gene set include geni ciliari (RPGR, CEP290, NPHP, BBS…), esegui anche:

```sparql
PREFIX wp: <http://vocabularies.wikipathways.org/wp#>
PREFIX dc: <http://purl.org/dc/elements/1.1/>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT DISTINCT ?wpid ?pathwayTitle
WHERE {
  ?pathway a wp:Pathway ;
           dc:title ?pathwayTitle ;
           dcterms:identifier ?wpid ;
           wp:organismName "Homo sapiens" .
  FILTER (
    CONTAINS(LCASE(?pathwayTitle), "cili") ||
    CONTAINS(LCASE(?pathwayTitle), "photoreceptor") ||
    CONTAINS(LCASE(?pathwayTitle), "retinal") ||
    CONTAINS(LCASE(?pathwayTitle), "visual")
  )
}
```

### Step 5: Report strutturato

#### A. Ranking Pathway con Peso RP
Tabella: WP ID | Titolo | Hit | Coverage (%) | Rilevanza RP (★) | Geni trovati

#### B. Core Pathway Retinici (coverage ≥ 30%, rilevanza ★★★+)
Dettaglio per pathway: lista geni trovati + geni RP noti già presenti nel pathway ma non nell'input.

#### C. Pathway Esclusivi per il Gene Set
Pathway trovati con coverage 100% — tutti i geni del set co-partecipano a questi pathway — altamente specifici.

#### D. Geni RP non connessi a pathway noti
Geni del set con 0 hit in WikiPathways — probabili gap nella curation, o geni con funzione non ancora assegnata a pathway noti.

#### E. Interpretazione per Retinitis Pigmentosa
Tema biologico dominante del gene set:
- **Fototransduction pura**: segnale luce → fotorecettori → bipolare
- **Splicing machinery**: geni PRPF — RP per difetto splicing RNA
- **Ciliopatia**: difetto trasporto cigliare → degenerazione secondaria
- **ECM/adesione**: EYS-like — perdita di supporto strutturale IPM
- **Visual cycle**: retinoid metabolism — accumulo tossico all-trans-retinal
- **Misto**: coinvolge più pathway — fenotipo probabilmente eterogeneo

### Note EYS-specifiche
- EYS **non è presente** in molti pathway WikiPathways perché il gene è assente nel topo (modello comune per costruire i pathway)
- I pathway contenenti EYS in WikiPathways tendono a essere basati su dati umani o Drosophila (spacemaker)
- Per analisi interattori EYS con letteratura: `/eys-ppi-compare EYS GRK7,AIPL1,DAG1,POMGNT1,POMT2,PROM1,KIF19,PDE6D`
- Per costruire il grafo RDF dei pathway retinici: `/eys-rdf-turtle EYS`
