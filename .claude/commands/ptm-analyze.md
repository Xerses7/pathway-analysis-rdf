# PTM Analyze

Recupera e analizza tutte le modificazioni post-traduzionali (PTM) di una proteina da UniProt, con posizioni esatte nella sequenza, tipo di modifica e contesto biologico.

## Come usare
`/ptm-analyze GENE_SYMBOL`

Esempi:
- `/ptm-analyze EYS`
- `/ptm-analyze AIPL1`
- `/ptm-analyze RHO`

## Istruzioni per Claude

Il gene da analizzare è: $ARGUMENTS

### Step 1: Recupera tutti i siti PTM da UniProt via SPARQL

Esegui questa query sull'endpoint `https://sparql.uniprot.org/sparql`:

```sparql
PREFIX up: <http://purl.uniprot.org/core/>
PREFIX taxon: <http://purl.uniprot.org/taxonomy/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX faldo: <http://biohackathon.org/resource/faldo#>

SELECT ?annotType ?comment ?begin ?end
WHERE {
  ?protein a up:Protein ;
           up:organism taxon:9606 ;
           up:encodedBy ?gene ;
           up:annotation ?annotation .
  ?gene skos:prefLabel ?geneName .
  ?annotation a ?annotType ;
              rdfs:comment ?comment ;
              up:range ?range .
  ?range faldo:begin ?beginPos ;
         faldo:end ?endPos .
  ?beginPos faldo:position ?begin .
  ?endPos faldo:position ?end .
  FILTER (?geneName = "GENE_SYMBOL")
  FILTER (?annotType IN (
    up:Glycosylation_Annotation,
    up:Modified_Residue_Annotation,
    up:Lipidation_Annotation,
    up:Disulfide_Bond_Annotation,
    up:Cross_Link_Annotation,
    up:PTM_Annotation
  ))
}
ORDER BY ?begin
```

Sostituisci `GENE_SYMBOL` con il gene richiesto.

### Step 2: Raggruppa per tipo di PTM

Organizza i risultati in categorie:

| Categoria | Tipo UniProt | Esempi |
|-----------|-------------|--------|
| **Glicosilazione N-linked** | Glycosylation_Annotation | N-GlcNAc su Asn (sequon N-X-S/T) |
| **Glicosilazione O-linked** | Glycosylation_Annotation | O-GalNAc su Ser/Thr |
| **Fosforilazione** | Modified_Residue_Annotation | Phosphoserine, Phosphothreonine, Phosphotyrosine |
| **Lipidazione** | Lipidation_Annotation | Geranilgeranilazione, Miristoilazione, Palmitoilazione |
| **Ponti disolfuro** | Disulfide_Bond_Annotation | Cys-Cys |
| **Altri residui modificati** | Modified_Residue_Annotation | Metilazione, Acetilazione, Ubiquitinazione |

### Step 3: Mostra mappa posizionale

Costruisci una rappresentazione testuale della distribuzione delle PTM lungo la proteina:

```
Proteina GENE (N aa totali):
|─────────────────────────────────────────────────────|
0                                                     N

Glicosilazioni (N):  |  N    N  N  N   N     N         N  |
                       pos1  ...                      posN

Disolfuri (S-S):     |    SS      SS        SS          |

Fosforilazioni (P):  |        P       P  P              |
```

Indica anche i domini strutturali se noti (EGF-like, LamG, etc.).

### Step 4: Analisi biologica

Per ogni tipo di PTM trovata, spiega:

1. **Glicosilazione N-linked** (se presente):
   - Verifica il sequon N-X-S/T per ogni sito
   - Indica se il sito è nel reticolo endoplasmatico (N-terminale) o nel Golgi
   - Funzione: folding, stabilità, secrezione, interazione ECM

2. **Ponti disolfuro** (se presenti):
   - Fondamentali nei domini EGF-like (ogni dominio EGF ha 3 ponti disolfuro tipici)
   - Stabilizzano la struttura 3D
   - Sensibili allo stress ossidativo (rilevante per ABCA4 e RP)

3. **Lipidazione** (se presente):
   - Geranilgeranilazione: ancora la proteina alla membrana (es. GRK7 ha questo tipo)
   - Indica traffico verso i segmenti esterni dei fotorecettori

4. **Fosforilazione** (se presente):
   - Regolazione dell'attività
   - Possibili kinasi coinvolte (es. GRK7 fosforila opsine)

### Step 5: Considerazioni patologiche

- Indica quali PTM sono nella regione N-terminale vs C-terminale
- Commenta se i siti PTM sono in domini funzionali noti
- Suggerisci quali PTM potrebbero essere impattate da varianti patologiche note
- Proponi: "Per analizzare l'impatto delle varianti sulle PTM, usa `/ptm-variant-impact GENE`"

### Note tecniche
- La query usa FALDO (Feature Annotation Location Description Ontology) per le posizioni
- UniProt annota solo PTM **sperimentalmente confermate** - i siti predetti in silico non sono inclusi
- Per sequon N-X-S/T predetti usa `/sequon-scan GENE`
