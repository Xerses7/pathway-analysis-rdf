# PTM Analyze

Recupera e analizza tutte le modificazioni post-traduzionali (PTM) di qualsiasi proteina umana da UniProt, con posizioni esatte nella sequenza, tipo di modifica e contesto biologico.

## Come usare
`/ptm-analyze GENE_SYMBOL`

Esempi:
- `/ptm-analyze TP53`
- `/ptm-analyze EGFR`
- `/ptm-analyze BRCA1`

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
| **Lipidazione** | Lipidation_Annotation | Miristoilazione, Palmitoilazione, Geranilgeranilazione |
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

Indica i domini strutturali noti recuperati da UniProt se disponibili.

### Step 4: Analisi biologica

Per ogni tipo di PTM trovata, spiega nel contesto funzionale specifico della proteina analizzata:

1. **Glicosilazione N-linked** (se presente):
   - Verifica il sequon N-X-S/T per ogni sito
   - Indica il compartimento subcellulare dove avviene (reticolo endoplasmatico vs Golgi)
   - Funzione: folding, stabilità, secrezione, interazioni extracellulari

2. **Ponti disolfuro** (se presenti):
   - Frequenti nei domini extracellulari (EGF-like, immunoglobulin-like, LDL-receptor)
   - Stabilizzano la struttura 3D
   - Sensibili allo stress ossidativo e all'ambiente redox cellulare

3. **Lipidazione** (se presente):
   - Miristoilazione / Palmitoilazione: ancora la proteina al doppio strato lipidico
   - Geranilgeranilazione / Farnesilazione: membrane targeting, spesso per GTPasi
   - Indica il compartimento subcellulare di destinazione

4. **Fosforilazione** (se presente):
   - Regolazione dell'attività enzimatica o delle interazioni proteina-proteina
   - Identifica possibili kinasi coinvolte in base ai motivi consensus (es. [ST]-x-x-[DE] per CK2)

5. **Ubiquitinazione / Acetilazione** (se presente):
   - Ubiquitinazione: regola stabilità e degradazione proteasomale
   - Acetilazione: modula interazioni con cromatina o attività catalitica

### Step 5: Considerazioni patologiche

- Indica quali PTM sono nella regione N-terminale vs C-terminale
- Commenta se i siti PTM sono in domini funzionali noti (recupera struttura dominio da UniProt)
- Suggerisci quali PTM potrebbero essere impattate da varianti patologiche note
- Proponi: "Per analizzare l'impatto delle varianti sulle PTM, usa `/ptm-variant-impact $ARGUMENTS`"

### Note tecniche
- La query usa FALDO (Feature Annotation Location Description Ontology) per le posizioni
- UniProt annota solo PTM **sperimentalmente confermate** — i siti predetti in silico non sono inclusi
- Per sequon N-X-S/T predetti usa `/sequon-scan $ARGUMENTS`
