# PTM Variant Impact

Incrocia le varianti patologiche di qualsiasi gene umano con i siti di modificazione post-traduzionale (PTM), identificando quali mutazioni possono distruggere siti PTM, alterare sequon o compromettere la funzione proteica.

## Come usare
`/ptm-variant-impact GENE_SYMBOL`

Esempi:
- `/ptm-variant-impact TP53`
- `/ptm-variant-impact BRCA1`
- `/ptm-variant-impact EGFR`

## Istruzioni per Claude

Il gene da analizzare è: $ARGUMENTS

### Step 1: Recupera siti PTM con posizioni

Esegui su `https://sparql.uniprot.org/sparql`:

```sparql
PREFIX up: <http://purl.uniprot.org/core/>
PREFIX taxon: <http://purl.uniprot.org/taxonomy/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX faldo: <http://biohackathon.org/resource/faldo#>

SELECT ?annotType ?comment ?begin
WHERE {
  ?protein a up:Protein ;
           up:organism taxon:9606 ;
           up:encodedBy ?gene ;
           up:annotation ?annotation .
  ?gene skos:prefLabel ?geneName .
  ?annotation a ?annotType ;
              rdfs:comment ?comment ;
              up:range ?range .
  ?range faldo:begin ?beginPos .
  ?beginPos faldo:position ?begin .
  FILTER (?geneName = "GENE_SYMBOL")
  FILTER (?annotType IN (
    up:Glycosylation_Annotation,
    up:Modified_Residue_Annotation,
    up:Lipidation_Annotation,
    up:Disulfide_Bond_Annotation
  ))
}
ORDER BY ?begin
```

### Step 2: Recupera varianti patologiche con posizioni

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

### Step 3: Analisi di overlap e prossimità

Per ogni sito PTM, cerca varianti nelle seguenti finestre di rischio:

| Finestra | Distanza | Rischio | Meccanismo |
|----------|----------|---------|------------|
| **Diretta** | 0 aa | CRITICO | La variante è esattamente sul residuo PTM |
| **Sequon ±1** | 1-2 aa | ALTO | Per glicosilazione N-linked: distrugge N-X-S/T |
| **Sequon ±3** | 3-5 aa | MEDIO | Può alterare accessibilità al sito |
| **Dominio locale** | 6-30 aa | BASSO | Può alterare folding locale che espone il sito |

### Step 4: Classifica ogni interazione variante-PTM

Per ogni overlap trovato, assegna una classificazione:

**CRITICO** - Variante sul residuo PTM stesso:
```
Es: N[POS] → D[POS] (asparagina → acido aspartico)
    Effetto: sito di glicosilazione N[POS] completamente perso
    Conseguenza: possibile mancato folding nel RE → degradazione ERAD
```

**ALTO RISCHIO** - Variante nel sequon (posizione ±1 o ±2 dall'Asn):
```
Es: variante a pos N+2 (posizione S/T del sequon N-X-S/T)
    Effetto: sequon N-X-S/T → N-X-A (non glicosilabile)
    Conseguenza: sito non più riconosciuto dall'oligosaccaril-transferasi
```

**MEDIO RISCHIO** - Variante nel dominio ma distante dal sito:
```
Es: variante a pos P, sito PTM a pos P+N (distanza: N aa)
    Effetto: possibile alterazione del folding locale nel dominio
    Conseguenza: sito fisicamente accessibile ma contesto strutturale alterato
```

**INDIRETTO** - Troncamento/frameshift a monte del sito:
```
Es: frameshift a pos F
    Siti PTM impattati: tutti i siti > pos F
    Conseguenza: perdita completa dei siti distali alla troncatura
```

### Step 5: Genera report strutturato

Presenta i risultati in quattro sezioni:

#### A. Siti PTM a Rischio Critico/Alto
Tabella: sito PTM | posizione | tipo PTM | variante più vicina | distanza | classificazione rischio | meccanismo probabile

#### B. Mappa visiva di overlap
```
Proteina GENE (N aa):
|─────────────────────────────────────────|

PTM:      [G]  [P]  [G]  [S-S]  [G]
          posA posB posC  posD   posE

Varianti:  V         V     V      V
          var1      var2  var3   var4

          [G]   = glicosilazione N-linked
          [P]   = fosforilazione
          [S-S] = ponte disolfuro
          V     = variante patologica
          ↕     = overlap diretto
```

#### C. Implicazioni Biologiche

Per ogni sito a rischio, spiega:
- Quale PTM è compromessa
- Quale processo biologico ne risente (folding, localizzazione, attività enzimatica, interazioni…)
- Se esiste un effetto dominante o recessivo atteso in base alla patologia associata

#### D. Suggerimenti per Validazione Sperimentale

Top 3 esperimenti suggeriti in base al tipo di PTM impattata:
- Glicosilazione: mutagenesi N→Q + Western blot con/senza PNGasi F
- Fosforilazione: mutagenesi S/T→A (non fosforilabile) o S/T→D (fosfo-mimic)
- Ponte disolfuro: mutagenesi C→A + analisi SDS-PAGE in condizioni riducenti vs non riducenti

### Note
- Prioritizza varianti con significato patologico confermato (ClinVar: pathogenic / likely pathogenic)
- Distingui sempre varianti missense (singolo aa) da frameshift/nonsenso/troncamento
- Indica esplicitamente se una variante ha "uncertain significance" (VUS) annotata in UniProt
- Proponi: "Per analizzare sequon predetti non ancora in UniProt, usa `/sequon-scan $ARGUMENTS`"
