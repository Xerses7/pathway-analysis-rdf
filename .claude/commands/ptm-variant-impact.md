# PTM Variant Impact

Incrocia le varianti patologiche di un gene con i siti di modificazione post-traduzionale (PTM), identificando quali mutazioni possono distruggere siti PTM, alterare sequon o compromettere la funzione proteica.

## Come usare
`/ptm-variant-impact GENE_SYMBOL`

Esempi:
- `/ptm-variant-impact EYS`
- `/ptm-variant-impact RHO`
- `/ptm-variant-impact RPGR`

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
Es: N166 → D166 (asparagina → acido aspartico)
    Effetto: sito glicosilazione N166 completamente perso
    Conseguenza: mancato folding nel RE → degradazione ERAD
```

**ALTO RISCHIO** - Variante nel sequon (posizione ±1 o ±2 dall'Asn):
```
Es: variante a pos 168 (posizione S/T del sequon N166-X-S168)
    Effetto: sequon N-X-S/T → N-X-A (non glicosilabile)
    Conseguenza: sito N166 non più riconosciuto dall'oligosaccaril-transferasi
```

**MEDIO RISCHIO** - Variante nel dominio ma distante dal sito:
```
Es: variante a pos 2139, sito PTM a pos 2170
    Distanza: 31 aa
    Effetto: possibile alterazione del folding locale nel dominio LamG
    Conseguenza: sito N2170 fisicamente accessibile ma contesto alterato
```

**INDIRETTO** - Troncamento/frameshift a monte del sito:
```
Es: c.8648_8655del → frameshift a pos ~2883
    Siti PTM impattati: tutti i siti > pos 2883
    Conseguenza: perdita completa dei siti distali
```

### Step 5: Genera report strutturato

Presenta i risultati in tre sezioni:

#### A. Siti PTM a Rischio Critico/Alto
Tabella con: sito PTM | posizione | tipo PTM | variante più vicina | distanza | classificazione rischio | meccanismo probabile

#### B. Mappa visiva di overlap
```
Proteina (N aa):
|─────────────────────────────────────────|

PTM:      [G]  [G][G] [G][G] [G]  [G]        [G]
          166  269272 311343 506  566         2170

Varianti: V         V  V     V    V   V    ... V  V  V ...
          135       618 745 1110 1176 1232    2139 2189 2211

          [G] = glicosilazione N-linked
          V   = variante RP25
          ↕   = overlap diretto
          ~   = prossimità (<30 aa)
```

#### C. Implicazioni Biologiche

Per ogni sito a rischio, spiega:
- Quale PTM è compromessa
- Quale processo biologico ne risente (folding, localizzazione, interazione ECM...)
- Quale pathway è impattato (fototrasduzione, ciglio, matrice IPM...)
- Se esiste un effetto dominante o recessivo atteso

#### D. Suggerimenti per Validazione Sperimentale

Top 3 esperimenti suggeriti:
1. Mutagenesi sito-diretta: convertire l'Asn del sito glicosilazione → Gln (N→Q, conserva carica ma non è glicosilabile)
2. Western blot con/senza PNGasi F (deglicosila N-linked) per verificare peso molecolare
3. Microscopia confocale per confrontare localizzazione WT vs mutante

### Note
- Prioritizza varianti associate a RP25 o altra patologia confermata
- Distingui sempre varianti missense (singolo aa) da frameshift/troncamento
- Indica esplicitamente se una variante ha "uncertain significance" (annotata in UniProt)
- Proponi: "Per analizzare sequon predetti non ancora in UniProt, usa `/sequon-scan GENE`"
