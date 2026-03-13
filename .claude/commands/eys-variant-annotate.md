# Variant Annotate — EYS (RP25)

> **Skill calibrata per il gene EYS e per geni di Retinitis Pigmentosa autosomica recessiva.**
> Integra il contesto genetico di RP25: ereditarietà AR, compound heterozygosity, correlazione genotipo-fenotipo nell'ophthalmologia.
> Per annotazione varianti generica su qualsiasi gene usa `/variant-annotate GENE`.

Recupera e classifica tutte le varianti di EYS da UniProt, con classificazione per tipo, distribuzione sui domini EYS-specifici (EGF-like, LamG), correlazione con RP25 e prioritizzazione per compound heterozygosity.

## Come usare
`/eys-variant-annotate GENE_SYMBOL`

Esempi:
- `/eys-variant-annotate EYS`
- `/eys-variant-annotate RHO`
- `/eys-variant-annotate RPGR`

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

### Step 2: Recupera la patologia associata

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

Analizza il campo `comment` con questi pattern:

| Tipo | Pattern | Rilevanza RP |
|------|---------|-------------|
| **Missense** | "X → Y" | Variabile — dipende dal dominio colpito |
| **Nonsense** | "→ Stop" o "→ *" | Alta — quasi sempre patologica in AR |
| **Frameshift** | "frameshift" | Alta — LOF certo |
| **Delezione in-frame** | "del" | Alta se in dominio EGF-like o LamG |
| **Splicing** | "splice" | Alta — può abolire esone funzionale |
| **VUS** | "uncertain" | Richiedono segregazione familiare |

### Step 4: Mappa le varianti sui domini EYS (se il gene è EYS)

La proteina EYS ha 2888 aa con la seguente struttura di domini approssimativa:
```
EYS (2888 aa):
|──[LamG_1]──[EGF×2]──[LamG_2]──[EGF×7]──[LamG_3]──[EGF×12]──[LamG_4/5]──|
   ~1-200      ~200     ~400       ~450      ~900       ~1000      ~1800-2888

Distribuzione varianti:
  ▼   ▼     ▼   ▼  ▼    ▼   ▼    ▼▼  ▼     ▼    ▼▼   ▼▼ ▼
  [LamG_1 ]  [EGF]  [ LamG_2 ]  [EGF clusters]  [LamG_3-5]

  ▼ = missense
  ▼▼ = nonsense/frameshift (LOF)
```

Per altri geni RP (RHO, RPGR…), usa la struttura dominio disponibile in UniProt.

### Step 5: Analisi per Retinitis Pigmentosa autosomica recessiva

Per geni RP a ereditarietà AR (come EYS → RP25):

**Compound Heterozygosity:**
Identifica coppie di varianti biallelic plausibili. In AR, il paziente porta tipicamente:
- 2 alleli LOF (più grave, fenotipo precoce)
- 1 LOF + 1 missense (intermedio)
- 2 missense (più lieve, spesso onset tardivo)

**Correlazione genotipo-fenotipo RP:**
```
Tipo combinazione         → Gravità fenotipica attesa
LOF + LOF                 → Esordio precoce (<15 anni), perdita visiva rapida
LOF + Missense grave      → Esordio intermedio (15-30 anni)
LOF + Missense lieve      → Esordio tardivo, decorso lento
Missense + Missense       → Variabile, spesso decorso più lento
Frameshift + qualsiasi    → Dipende da posizione: se a monte di tutti i domini → grave
```

### Step 6: Report strutturato

#### A. Riepilogo statistico
```
Gene:             GENE_SYMBOL (RP associata: PATOLOGIA)
Varianti totali:  N
  LOF (nonsense + frameshift + splicing): N (XX%)
  Missense: N (XX%)
  Delezione/inserzione: N (XX%)
  VUS: N (XX%)
```

#### B. Varianti LOF — Massima Priorità
Tabella completa: posizione | variante | tipo | dominio colpito | note RP

#### C. Distribuzione per Dominio Funzionale
Per ogni dominio (es. LamG, EGF-like): numero varianti missense + LOF — indica domini hot-spot.

#### D. Varianti candidate per Compound Heterozygosity
Coppie di varianti LOF presenti nel database UniProt che, se co-segregate in trans, causerebbero RP25.

#### E. VUS — Varianti a Significato Incerto
Lista VUS con posizione e dominio colpito — richiedono segregazione familiare o studi funzionali.

### Note cliniche RP
- EYS causa RP25: autosomica recessiva, perdita progressiva dei fotorecettori (rod-cone dystrophy)
- Frequenza portatori EYS: ~1:80 nella popolazione europea
- Diagnosi molecolare: panel NGS RP o WES con focus su 60+ geni RP noti
- Per analisi PTM impattate dalle varianti: `/eys-ptm-variant-impact $ARGUMENTS`
- Per sequon a rischio N-glicosilazione: `/sequon-scan $ARGUMENTS`
