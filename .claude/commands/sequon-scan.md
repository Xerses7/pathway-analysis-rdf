# Sequon Scan

Scarica la sequenza proteica da UniProt e scansiona programmaticamente tutti i sequon N-X-S/T (siti potenziali di glicosilazione N-linked), confrontando con siti confermati e varianti patologiche per identificare siti a rischio non ancora annotati.

## Come usare
`/sequon-scan GENE_SYMBOL`

Esempi:
- `/sequon-scan TP53`
- `/sequon-scan EGFR`
- `/sequon-scan BRCA1`

## Istruzioni per Claude

Il gene da analizzare è: $ARGUMENTS

### Step 1: Scarica la sequenza FASTA da UniProt

Prima ottieni l'UniProt ID del gene:
```
https://sparql.uniprot.org/sparql?format=json&query=
PREFIX up: <http://purl.uniprot.org/core/>
PREFIX taxon: <http://purl.uniprot.org/taxonomy/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
SELECT ?protein ?uniprotId
WHERE {
  ?protein a up:Protein ;
           up:organism taxon:9606 ;
           up:encodedBy ?gene ;
           up:reviewed true .
  ?gene skos:prefLabel "GENE_SYMBOL" .
  BIND(STRAFTER(STR(?protein), "uniprot/") AS ?uniprotId)
}
LIMIT 1
```

Poi scarica la sequenza:
```
https://www.uniprot.org/uniprot/UNIPROT_ID.fasta
```

### Step 2: Scansiona la sequenza con Python

Crea ed esegui questo script nella cartella del progetto:

```python
import re
import urllib.request

def download_fasta(uniprot_id):
    url = f"https://www.uniprot.org/uniprot/{uniprot_id}.fasta"
    with urllib.request.urlopen(url) as r:
        fasta = r.read().decode()
    # Rimuovi header e newlines
    lines = fasta.strip().split('\n')
    sequence = ''.join(lines[1:])
    return sequence

def find_sequons(sequence):
    """Trova tutti i sequon N-X-S/T (X != Pro)"""
    sequons = []
    pattern = re.compile(r'N[^P][ST]')
    for match in pattern.finditer(sequence):
        pos = match.start() + 1  # 1-based
        sequons.append({
            'position': pos,
            'asparagine': pos,
            'motif': match.group(),
            'x_residue': match.group()[1],
            'st_residue': match.group()[2]
        })
    return sequons

def find_extended_sequons(sequence):
    """Trova sequon estesi N-X-X-S/T (sequon a distanza)"""
    sequons = []
    for i in range(len(sequence) - 3):
        if sequence[i] == 'N' and sequence[i+1] != 'P':
            if sequence[i+2] in 'ST':
                sequons.append({'position': i+1, 'type': 'NXS/T', 'motif': sequence[i:i+3]})
    return sequons

# Esegui per il gene richiesto
uniprot_id = "UNIPROT_ID"  # sostituisci
seq = download_fasta(uniprot_id)
sequons = find_sequons(seq)

print(f"Lunghezza sequenza: {len(seq)} aa")
print(f"Sequon N-X-S/T trovati: {len(sequons)}")
for s in sequons:
    print(f"  pos {s['position']:4d}: {s['motif']}  (X={s['x_residue']}, S/T={s['st_residue']})")
```

### Step 3: Confronto con siti UniProt confermati

Dopo aver ottenuto i siti predetti, recupera i siti confermati da UniProt (via SPARQL come in `/ptm-analyze`) e confronta:

Crea una tabella con tre categorie:

| Categoria | Descrizione |
|-----------|-------------|
| **Confermati** | Sito nel sequon predetto E annotato in UniProt |
| **Predetti non confermati** | Sito nel sequon predetto ma NON in UniProt (potenziale, non validato) |
| **Confermati ma no sequon** | In UniProt ma sequon non trovato (raro, possibile errore o sequon atipico) |

### Step 4: Incrocia con varianti patologiche

Per ogni sequon predetto, verifica se c'è una variante patologica nelle posizioni critiche:

```
Sequon N(pos)-X(pos+1)-S/T(pos+2):

- Variante a pos   → Asn → altro: SITO PERSO
- Variante a pos+1 → X → Pro:    SEQUON ROTTO (Pro blocca glicosilazione)
- Variante a pos+2 → S/T → altro: SEQUON ROTTO
```

### Step 5: Report finale

#### A. Statistiche
```
Gene: GENE_SYMBOL (UNIPROT_ID)
Lunghezza proteina: N aa
Sequon N-X-S/T predetti: N
  - di cui confermati in UniProt: N
  - di cui NON confermati (potenziali): N
Sequon a rischio (con variante vicina): N
```

#### B. Siti ad Alto Rischio (variante nel sequon)
Tabella dettagliata ordinata per rischio:
- Posizione Asn
- Motivo (es. NAS, NTS)
- Variante sovrapposta
- Patologia associata alla variante
- Effetto predetto: perdita sito / distruzione sequon

#### C. Siti Predetti non Ancora Confermati
Lista di sequon con alta probabilità di essere glicosilati ma non ancora validati sperimentalmente:
- Posizione
- Motivo
- Contesto (dominio strutturale)
- Suggerimento: "Candidato per validazione con mutagenesi N→Q"

#### D. Implicazione per il Modello RDF
Suggerisci triple RDF da aggiungere per i nuovi siti:
```turtle
pn:GENE pn:predictedGlycosylationSite [
    pn:position "POS"^^xsd:integer ;
    pn:sequon "NXS/T"^^xsd:string ;
    pn:status "predicted"^^xsd:string ;
    pn:confirmedInUniProt "false"^^xsd:boolean
] .
```

### Note importanti
- Il sequon N-X-S/T è necessario ma **non sufficiente**: non tutti i sequon vengono glicosilati in vivo
- Il contesto 3D conta: sequon sepolti nella proteina non sono accessibili
- Usa la rule of thumb: sequon nelle regioni di loop/disordered → più probabilmente glicosilati
- Il sequon N-X-T è generalmente più efficiente di N-X-S
- Pro in posizione -1 rispetto ad Asn riduce anche l'efficienza
- Salva i risultati come: `GENE_sequon_analysis.json` nella cartella del progetto
- Per l'analisi dell'impatto delle varianti, usa `/ptm-variant-impact GENE`
