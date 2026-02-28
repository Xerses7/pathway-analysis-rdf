# PPI Analyzer

**SPARQL Aggregator & Enrichment Comparator** per analisi interazioni proteina-proteina.

## Funzionalità

### 1. SPARQL Aggregator
Raccoglie e unifica dati da multipli endpoint:
- **UniProt**: Informazioni proteiche, GO terms, malattie
- **STRING**: Interazioni proteina-proteina con score di confidenza
- **WikiPathways**: Pathway biologici

### 2. Enrichment Comparator
Confronta interattori da fonti diverse:
- Identifica **gap nei database** (presenti solo in letteratura)
- Trova **nuove interazioni** (nei database ma non documentate)
- Suggerisce **candidati per validazione sperimentale**
- Calcola metriche di overlap (Jaccard similarity)

### 3. Export Cytoscape
Esporta dati in formato compatibile con Cytoscape:
- File CSV per nodi e archi
- Attributi per colorazione per fonte (letteratura vs database)

## Installazione

```bash
cd ppi_analyzer
# Nessuna dipendenza esterna richiesta (usa solo librerie standard Python)
```

## Uso

### Modalità Interattiva
```bash
python main.py --interactive
# oppure
python main.py
```

### Demo con Gene EYS
```bash
python main.py --demo
```

### Analisi Gene Specifico
```bash
# Solo aggregazione
python main.py --gene EYS

# Con confronto letteratura
python main.py --gene EYS --literature GRK7,AIPL1,DAG1,POMGNT1

# Export Markdown
python main.py --gene EYS --literature GRK7,AIPL1 --output report.md --format markdown

# Export Cytoscape
python main.py --gene EYS --literature GRK7,AIPL1 --cytoscape network.json
```

## Output

### Report Testuale
```
======================================================================
                 ENRICHMENT COMPARISON REPORT: EYS
======================================================================

                            SUMMARY
----------------------------------------------------------------------
  Interattori da letteratura:  8
  Interattori da database:     12
  Overlap:                     1 (7.1%)
  Gap nei database:            7
  Gap nella letteratura:       11
```

### Report Markdown
Genera tabelle formattate con:
- Summary statistiche
- Lista interattori confermati
- Gap analysis
- Candidati validazione

### Export Cytoscape
- `*_nodes.csv`: Nodi con attributi (id, label, type, source)
- `*_edges.csv`: Archi con attributi (source, target, score, validation)
- `*.json`: Dati completi in JSON

## Struttura File

```
ppi_analyzer/
├── __init__.py
├── config.py              # Configurazione endpoint
├── sparql_aggregator.py   # Modulo aggregazione SPARQL
├── enrichment_comparator.py # Modulo confronto fonti
├── main.py                # CLI principale
├── requirements.txt
└── README.md
```

## Endpoint Supportati

| Endpoint | URL | Dati |
|----------|-----|------|
| UniProt | sparql.uniprot.org | Proteine, GO, Malattie |
| STRING | string-db.org/api | Interazioni PPI |
| WikiPathways | sparql.wikipathways.org | Pathway |

## Esempio: Gene EYS

### Interattori da Letteratura (PDF)
- GRK7, AIPL1, DAG1, POMGNT1, POMT2, PROM1, KIF19, PDE6D

### Interattori da STRING
- CERKL, IMPG2, PRPF31, PCARE, RPGR, ABCA4, PDE6A, RDH12, CNGB1, TULP1, PRPH2, FSCN2

### Gap Analysis
- **7 interattori** presenti solo in letteratura → candidati per submission a database
- **11 interattori** presenti solo nei database → potenziali nuove interazioni da investigare

## Licenza

MIT License
