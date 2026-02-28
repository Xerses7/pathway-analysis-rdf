# SPARQL Endpoints per Bioinformatica

Guida completa agli endpoint SPARQL per lavorare con pathway genici (cellule retiniche), interazioni proteina-proteina e proteina-ligando, trascrizione/traduzione di geni.

## Indice
- [Endpoint SPARQL Disponibili](#endpoint-sparql-disponibili)
- [Configurazione RDF Explorer](#configurazione-rdf-explorer)
- [Setup per Claude Code](#setup-per-claude-code)
- [Esempi di Query SPARQL](#esempi-di-query-sparql)
- [Query Federate](#query-federate)
- [Risorse Aggiuntive](#risorse-aggiuntive)

---

## Endpoint SPARQL Disponibili

### 1. UniProt SPARQL Endpoint ⭐ **CONSIGLIATO**

**URL:** `https://sparql.uniprot.org/sparql`

**Caratteristiche:**
- **Il più grande endpoint pubblico SPARQL**: 217+ miliardi di triple (release 2025_04)
- **Timeout:** 45 minuti per query
- **Accesso:** Gratuito, supporta SPARQL 1.1 Standard
- **22 named graphs** disponibili

**Dati coperti:**
- Pathway genici e annotazioni
- Interazioni proteina-proteina
- Annotazioni di trascrizione/traduzione
- Gene expression e varianti di sequenza
- Disease annotations
- Cross-reference a pathway databases (Reactome, KEGG, etc.)
- Modificazioni post-traduzionali
- Localizzazione cellulare
- Funzioni molecolari (GO annotations)

**Databases integrati:**
- PDB (strutture proteiche)
- OMIM (malattie genetiche)
- Ensembl, NCBI Gene
- ChEBI (small molecules)
- Reactome, KEGG pathways

**Link:**
- Interface web: https://sparql.uniprot.org/
- Documentazione: https://www.uniprot.org/help/sparql
- Esempi query: https://sparql.uniprot.org/.well-known/sparql-examples/

---

### 2. STRING Database SPARQL Endpoint

**URL:** `https://string-db.org/sparql`

**Caratteristiche:**
- **Specializzato in interazioni proteina-proteina**
- Network funzionali e fisici
- Livelli di confidence: highest, high, medium, any
- Supporta query federate con UniProt
- Simplified RDF representation per performance

**Tipi di network:**
- Functional interactions
- Physical interactions

**Livelli di confidence:**
- highest confidence cutoff
- high confidence cutoff
- medium confidence cutoff
- any confidence cutoff

**Predicati disponibili:**
8 combinazioni (2 network types × 4 confidence levels)

**Link:**
- Documentazione: https://string-db.org/help/rdf/
- Query editor: https://string-db.org/sparql

**Note:**
- Per >20 risultati o use cases complessi, considera l'uso della STRING API
- Ottimo per query federate con UniProt e altri endpoint

---

### 3. WikiPathways SPARQL Endpoint

**URL:** `https://sparql.wikipathways.org/sparql`

**Caratteristiche:**
- Database di pathway biologici collaborativo e open-source
- Curato dalla comunità scientifica
- Pathway metabolici, signaling, regolazione trascrizionale
- 29 specie supportate (forte focus su Homo sapiens)
- Creative Commons 0 license (completamente open)

**Contenuto:**
- Pathways (1057+ pathways umani)
- Metaboliti, proteine, geni, complessi
- Interazioni molecolari
- Disease associations
- PubMed references

**Comunità specializzate disponibili:**
- Lipids
- Rare Diseases
- COVID19
- IEM (Inborn Errors of Metabolism)
- Altri

**Formati disponibili:**
- GPML (GraphML Pathway Markup Language)
- BioPAX
- RDF/SPARQL
- SBML

**Link:**
- Interface SPARQL: https://sparql.wikipathways.org/
- Query examples: https://www.wikipathways.org/sparql.html
- SPARQL Book: https://www.wikipathways.org/WikiPathways-SPARQL-book/
- API REST: disponibile
- R package: rWikiPathways

---

### 4. Reactome Pathway Database

**Formato:** BioPAX Level 3 (RDF/OWL)
**SPARQL:** Disponibile via download, non endpoint pubblico stabile

**Caratteristiche:**
- Pathway curati manualmente da esperti PhD
- Peer-reviewed
- Focus su processi biologici umani
- Signaling, metabolism, transcriptional regulation, apoptosis

**Contenuto:**
- 5272+ proteine umane
- 3504+ complessi macromolecolari
- 3847+ reazioni
- 1057+ pathways

**Accesso:**
- Download BioPAX: https://reactome.org/download-data
- Pathway Browser: https://reactome.org
- Analysis tools integrati
- Neo4j GraphDB format disponibile

**Cross-references:**
- UniProt
- Ensembl, NCBI Gene
- ChEBI, KEGG Compound
- PubMed
- GO vocabularies

**Link:**
- Homepage: https://reactome.org/
- Documentazione: https://reactome.org/documentation

---

### 5. Protein Ontology (PRO) SPARQL Endpoint

**URL:** Accessibile via YASGUI interface

**Caratteristiche:**
- Ontologia delle proteine e entità correlate
- Protein families, proteoforms, complexes
- Modificazioni post-traduzionali
- Associazioni con malattie e drug targets
- FAIR compliant
- Top 5 endpoints per Umaka Score

**Applicazioni:**
- Orthology mapping
- Kinase modifications
- Cancer-associated modifications
- Named entity recognition

**Link:**
- SPARQL GUI: Disponibile via YASGUI
- RESTful APIs: Disponibili per accesso programmatico
- Pubblicazione: https://www.nature.com/articles/s41597-020-00679-9

---

### 6. Pathway Commons

**URL:** `https://rdf.pathwaycommons.org/sparql/`

**Caratteristiche:**
- Aggregatore di pathway databases
- BioPAX Level 3
- Supporta query federate (con alcune limitazioni tecniche)
- Integra dati da multiple sorgenti

**Note:**
- Potrebbero esserci issues con alcune query federate
- Verifica documentazione per backend tecnici

---

### 7. OrthoDB SPARQL Endpoint

**URL:** `https://sparql.orthodb.org/`

**Caratteristiche:**
- Database di ortologia tra specie
- Orthologous groups across species
- Utile per pathway conservati evolutivamente
- Supporta query federate con UniProt, STRING, RHEA

**Applicazioni:**
- Trovare ortologhi tra specie
- Phyletic profiles
- Gene families evolution
- Cross-species pathway analysis

**Esempi:**
- Ortologhi zebrafish di geni umani disease-associated
- Distribution di reazioni attraverso taxa
- STRING-annotated interacting genes

---

## Configurazione RDF Explorer

### Installazione Base

```bash
# Clona il repository
git clone https://github.com/emekaokoye/mcp-rdf-explorer
cd mcp-rdf-explorer

# Crea ambiente virtuale
python -m venv venv

# Attiva ambiente virtuale
# Su Linux/Mac:
source venv/bin/activate
# Su Windows:
venv\Scripts\activate

# Installa dipendenze
pip install -r requirements.txt
```

### Configurazione per Endpoint Remoti

RDF Explorer supporta due modalità:
1. **Local File Mode**: per file Turtle (.ttl) locali
2. **SPARQL Endpoint Mode**: per endpoint remoti (quello che ti serve)

---

## Setup per Claude Code

### Configurazione Endpoint Multipli

```bash
# 1. UniProt - Endpoint principale per dati proteici completi
claude mcp add-json "rdf_uniprot" '{
  "command": "python",
  "args": [
    "/path/to/mcp-rdf-explorer/server.py",
    "--sparql-endpoint",
    "https://sparql.uniprot.org/sparql"
  ]
}'

# 2. STRING - Interazioni proteina-proteina
claude mcp add-json "rdf_string" '{
  "command": "python",
  "args": [
    "/path/to/mcp-rdf-explorer/server.py",
    "--sparql-endpoint",
    "https://string-db.org/sparql"
  ]
}'

# 3. WikiPathways - Pathway biologici
claude mcp add-json "rdf_wikipathways" '{
  "command": "python",
  "args": [
    "/path/to/mcp-rdf-explorer/server.py",
    "--sparql-endpoint",
    "https://sparql.wikipathways.org/sparql"
  ]
}'

# 4. OrthoDB - Ortologia (opzionale)
claude mcp add-json "rdf_orthodb" '{
  "command": "python",
  "args": [
    "/path/to/mcp-rdf-explorer/server.py",
    "--sparql-endpoint",
    "https://sparql.orthodb.org/"
  ]
}'
```

**Nota:** Sostituisci `/path/to/` con il percorso effettivo dove hai installato mcp-rdf-explorer.

### Verifica Configurazione

Dopo aver aggiunto gli endpoint, riavvia Claude Code e verifica che gli endpoint siano disponibili.

---

## Esempi di Query SPARQL

### UniProt - Geni e Proteine Retinali

#### Query 1: Proteine umane associate alla retina

```sparql
PREFIX up: <http://purl.uniprot.org/core/>
PREFIX taxon: <http://purl.uniprot.org/taxonomy/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?protein ?geneName ?proteinName ?function
WHERE {
  ?protein a up:Protein ;
           up:organism taxon:9606 ;  # Homo sapiens
           up:encodedBy ?gene ;
           up:recommendedName ?recName .
  
  ?gene skos:prefLabel ?geneName .
  ?recName up:fullName ?proteinName .
  
  # Cerca annotazioni relative alla retina
  ?protein up:annotation ?annotation .
  ?annotation rdfs:comment ?function .
  
  FILTER (
    CONTAINS(LCASE(?function), "retina") || 
    CONTAINS(LCASE(?proteinName), "retina") ||
    CONTAINS(LCASE(?function), "photoreceptor") ||
    CONTAINS(LCASE(?function), "rod") ||
    CONTAINS(LCASE(?function), "cone")
  )
}
LIMIT 100
```

#### Query 2: Proteine con varianti associate a Retinitis Pigmentosa

```sparql
PREFIX up: <http://purl.uniprot.org/core/>
PREFIX taxon: <http://purl.uniprot.org/taxonomy/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

SELECT ?protein ?geneName ?diseaseText
WHERE {
  ?protein a up:Protein ;
           up:organism taxon:9606 ;
           up:encodedBy ?gene ;
           up:annotation ?annotation .
  
  ?gene skos:prefLabel ?geneName .
  ?annotation a up:Disease_Annotation ;
              rdfs:comment ?diseaseText .
  
  FILTER CONTAINS(LCASE(?diseaseText), "retinitis pigmentosa")
}
```

#### Query 3: Pathway di trasduzione del segnale visivo

```sparql
PREFIX up: <http://purl.uniprot.org/core/>
PREFIX taxon: <http://purl.uniprot.org/taxonomy/>

SELECT ?protein ?pathway ?pathwayName
WHERE {
  ?protein a up:Protein ;
           up:organism taxon:9606 ;
           up:annotation ?annotation .
  
  ?annotation a up:Pathway_Annotation ;
              rdfs:comment ?pathwayName .
  
  FILTER (
    CONTAINS(LCASE(?pathwayName), "visual") ||
    CONTAINS(LCASE(?pathwayName), "phototransduction") ||
    CONTAINS(LCASE(?pathwayName), "retina")
  )
}
```

#### Query 4: Interazioni proteina-proteina per rhodopsin

```sparql
PREFIX up: <http://purl.uniprot.org/core/>
PREFIX uniprotkb: <http://purl.uniprot.org/uniprot/>

SELECT ?protein1 ?protein2 ?interaction
WHERE {
  # Rhodopsin (esempio)
  ?protein1 a up:Protein ;
            up:encodedBy ?gene1 .
  ?gene1 skos:prefLabel "RHO" .
  
  # Cerca interazioni
  ?protein1 up:interaction ?interactionNode .
  ?interactionNode up:participant ?protein2 .
  
  FILTER (?protein1 != ?protein2)
}
LIMIT 50
```

---

### STRING - Interazioni Proteina-Proteina

#### Query 1: Partner di interazione per CDK2 (esempio generico)

```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX protein: <http://string-db.org/network/>
PREFIX ip_high: <http://string-db.org/rdf/interaction/physical-high-confidence-cutoff>

SELECT ?partner 
WHERE {
  ?protein rdfs:label "CDK2" .
  ?protein ip_high: ?partner
}
LIMIT 100
```

#### Query 2: Interazioni fisiche ad alta confidenza per gene specifico

```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX protein: <http://string-db.org/network/>
PREFIX ip_high: <http://string-db.org/rdf/interaction/physical-high-confidence-cutoff>
PREFIX taxon: <http://string-db.org/taxonomy/>

SELECT ?geneSymbol ?partner ?partnerLabel
WHERE {
  # Specifica organismo (9606 = Homo sapiens)
  ?protein rdfs:label ?geneSymbol .
  ?protein ip_high: ?partner .
  ?partner rdfs:label ?partnerLabel .
  
  FILTER(CONTAINS(STR(?protein), "9606"))
  FILTER(?geneSymbol = "RHO")
}
LIMIT 100
```

#### Query 3: Network funzionale con diversi livelli di confidence

```sparql
PREFIX protein: <http://string-db.org/network/>
PREFIX if_any: <http://string-db.org/rdf/interaction/functional-any-confidence-cutoff>

SELECT ?partner 
WHERE {
  protein:511145.b1260 if_any: ?partner
}
```

---

### WikiPathways - Pathway Biologici

#### Query 1: Pathway umani contenenti "retina"

```sparql
PREFIX wp: <http://vocabularies.wikipathways.org/wp#>
PREFIX dc: <http://purl.org/dc/elements/1.1/>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT DISTINCT ?wpid ?title ?description
WHERE {
  ?pathway a wp:Pathway ;
           dc:title ?title ;
           dcterms:identifier ?wpid ;
           wp:organismName "Homo sapiens" .
  
  OPTIONAL { ?pathway dc:description ?description }
  
  FILTER (
    regex(?title, "retina", "i") ||
    regex(?description, "retina", "i") ||
    regex(?title, "vision", "i") ||
    regex(?title, "photoreceptor", "i")
  )
}
ORDER BY ?wpid
```

#### Query 2: Proteine in pathway specifici per organismo

```sparql
PREFIX wp: <http://vocabularies.wikipathways.org/wp#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT DISTINCT ?pathway ?proteinLabel
WHERE {
  ?protein a wp:Protein ;
           rdfs:label ?proteinLabel ;
           dcterms:isPartOf ?pathway .
  
  ?pathway a wp:Pathway ;
           wp:organismName "Homo sapiens" .
  
  FILTER regex(?proteinLabel, "RHO", "i")
}
```

#### Query 3: Pathway con annotazioni disease

```sparql
PREFIX wp: <http://vocabularies.wikipathways.org/wp#>
PREFIX dc: <http://purl.org/dc/elements/1.1/>

SELECT DISTINCT ?pathway ?title ?diseaseTag
WHERE {
  ?pathway a wp:Pathway ;
           dc:title ?title ;
           wp:ontologyTag ?diseaseTag .
  
  FILTER CONTAINS(STR(?diseaseTag), "Disease")
}
```

#### Query 4: Metaboliti in pathway lipidici

```sparql
PREFIX wp: <http://vocabularies.wikipathways.org/wp#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT DISTINCT ?pathway ?metabolite ?lipidMapsID
WHERE {
  ?metabolite a wp:Metabolite ;
              dcterms:identifier ?id ;
              dcterms:isPartOf ?pathway ;
              wp:bdbLipidMaps ?lipidMapsID .
  
  ?pathway a wp:Pathway ;
           wp:organismName "Homo sapiens" .
  
  FILTER regex(STR(?lipidMapsID), "FA")  # Fatty acids
}
ORDER BY ?pathway
```

#### Query 5: Geni che codificano per proteine CYP

```sparql
PREFIX wp: <http://vocabularies.wikipathways.org/wp#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT DISTINCT ?pathway (str(?label) as ?geneProduct)
WHERE {
  ?geneProduct a wp:GeneProduct ;
               rdfs:label ?label ;
               dcterms:isPartOf ?pathway .
  
  ?pathway a wp:Pathway .
  
  FILTER regex(str(?label), "CYP")
}
```

---

## Query Federate

Le query federate permettono di combinare dati da endpoint multipli in una singola query usando la clausola `SERVICE`.

### Esempio 1: Combinare UniProt e WikiPathways

```sparql
PREFIX up: <http://purl.uniprot.org/core/>
PREFIX wp: <http://vocabularies.wikipathways.org/wp#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?protein ?geneName ?pathway ?pathwayTitle
WHERE {
  # Da UniProt: proteine umane
  ?protein a up:Protein ;
           up:organism <http://purl.uniprot.org/taxonomy/9606> ;
           up:encodedBy ?gene .
  ?gene skos:prefLabel ?geneName .
  
  # Da WikiPathways: pathway correlati
  SERVICE <https://sparql.wikipathways.org/sparql> {
    ?datanode wp:bdbEnsembl ?ensembl ;
              dcterms:isPartOf ?pathway .
    ?pathway dc:title ?pathwayTitle .
  }
  
  FILTER (?geneName = "RHO")
}
```

### Esempio 2: UniProt + STRING per network di interazioni

```sparql
PREFIX up: <http://purl.uniprot.org/core/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?protein ?partner ?confidence
WHERE {
  # Da UniProt
  ?protein a up:Protein ;
           up:encodedBy ?gene .
  ?gene skos:prefLabel "GNGT1" .  # Gene transducina retinale
  
  # Da STRING
  SERVICE <https://string-db.org/sparql> {
    ?stringProtein rdfs:label "GNGT1" .
    ?stringProtein ?confidencePredicate ?partner .
    
    FILTER(CONTAINS(STR(?confidencePredicate), "high-confidence"))
  }
}
```

### Esempio 3: Pathway Commons + UniProt (Wnt signaling)

```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX bp: <http://www.biopax.org/release/biopax-level3.owl#>
PREFIX up: <http://purl.uniprot.org/core/>

SELECT ?pathway ?protein ?uniprotEntry
WHERE {
  SERVICE <https://rdf.pathwaycommons.org/sparql/> {
    ?protein rdf:type bp:Protein .
    ?protein bp:entityReference ?eref .
    ?assembly bp:left ?protein .
    ?pathway bp:pathwayComponent ?assembly ;
             rdf:type bp:Pathway ;
             bp:displayName ?pathwayName .
    
    FILTER regex(?pathwayName, "^Wnt")
  }
  
  # Arricchisci con dati UniProt
  ?uniprotEntry a up:Protein .
  # ... mapping logic
}
LIMIT 100
```

---

## Best Practices per Query SPARQL

### 1. Limitazioni e Performance

- **Usa sempre LIMIT** per query esplorative (es. LIMIT 100)
- **Filtra early**: metti i filtri più restrittivi all'inizio
- **Evita SELECT ***: specifica solo le variabili necessarie
- **Timeout**: UniProt ha 45 min, altri endpoint potrebbero avere limiti più bassi

### 2. Prefissi Standard

Definisci sempre i prefissi all'inizio:

```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX up: <http://purl.uniprot.org/core/>
PREFIX taxon: <http://purl.uniprot.org/taxonomy/>
```

### 3. Debugging

- Inizia con query semplici e aggiungi complessità gradualmente
- Usa LIMIT 10 durante il testing
- Verifica i predicati disponibili prima:

```sparql
SELECT DISTINCT ?predicate
WHERE {
  ?subject a up:Protein ;
           ?predicate ?object .
}
LIMIT 100
```

### 4. Case Sensitivity

SPARQL è **case-sensitive** per:
- URI e prefissi
- Nomi di variabili
- Valori letterali (a meno di usare funzioni come LCASE)

### 5. Gestione Stringhe

Per ricerche case-insensitive:

```sparql
FILTER (
  CONTAINS(LCASE(?text), "retina") ||
  regex(?text, "retina", "i")
)
```

---

## Troubleshooting Comuni

### Problema: Query timeout
**Soluzione:**
- Riduci lo scope con filtri più restrittivi
- Usa LIMIT più basso
- Spezza la query in parti più piccole

### Problema: Nessun risultato
**Soluzione:**
- Verifica i prefissi siano corretti
- Controlla che le proprietà esistano (usa query esplorative)
- Verifica organism/taxon ID (9606 per Homo sapiens)

### Problema: Query federate falliscono
**Soluzione:**
- Alcuni endpoint hanno limitazioni su SERVICE
- Prova a invertire l'ordine (SERVICE principale vs secondario)
- Considera di fare query separate e unire i risultati

### Problema: Troppi risultati
**Soluzione:**
- Aggiungi filtri più specifici
- Usa DISTINCT per eliminare duplicati
- Limita a species/organism specifico

---

## Risorse Aggiuntive

### Documentazione SPARQL
- W3C SPARQL 1.1: https://www.w3.org/TR/sparql11-query/
- SPARQL by Example: http://www.cambridgesemantics.com/blog/semantic-university/learn-sparql/

### Tool Online
- YASGUI (SPARQL IDE): https://yasgui.triply.cc/
- SPARQL Visualizer: varie librerie JavaScript disponibili

### Librerie per Programmazione

#### Python
```bash
pip install SPARQLWrapper rdflib
```

#### R
```r
install.packages("SPARQL")
install.packages("rrdf")
```

#### JavaScript
```javascript
// Usa fetch API o librerie come @comunica/query-sparql
```

### Papers di Riferimento

1. **WikiPathways Semantic Web**
   - Waagmeester et al., PLoS Comput Biol 2016
   - DOI: 10.1371/journal.pcbi.1004989

2. **Protein Ontology**
   - Natale et al., Scientific Data 2020
   - DOI: 10.1038/s41597-020-00679-9

3. **UniProt RDF**
   - Documentazione ufficiale UniProt

4. **STRING Database**
   - Documentazione RDF/SPARQL: https://string-db.org/help/rdf/

---

## Pathway Retinali Specifici

### Geni Chiave per Retinitis Pigmentosa
Basato su ricerca recente (PMC8999418):

- **RHO** (Rhodopsin) - fotopigmento essenziale
- **RHOA** - GTPase signaling
- **GNGT1** - Transducin gamma subunit
- **GNG2** - G protein gamma subunit
- **GART** - IMP synthesis pathway
- **ABCA4** - stress ossidativo
- Altri 161+ geni identificati nella Retinal Information Network (RetNet)

### Pathway di Interesse

1. **Phototransduction**
   - Trasformazione segnale luminoso in elettrico
   - Rhodopsin → Transducin → Phosphodiesterase → cGMP

2. **Visual Cycle**
   - Rigenerazione rhodopsin
   - Retinoid metabolism

3. **Photoreceptor Cell Death**
   - ER stress
   - Accumulo Ca2+
   - Stress ossidativo (ABCA4)
   - Cascate infiammatorie

4. **G-Protein Signaling**
   - RHOA, GNG2, GNGT1
   - GTPase activity

---

## Note Finali

### Endpoint Limits e Rate Limiting

- **UniProt**: Nessun rate limit esplicito, ma query molto grandi potrebbero essere limitate
- **STRING**: Preferisci API per molte query ripetute
- **WikiPathways**: Endpoint pubblico senza limiti stringenti documentati

### Data Updates

Gli endpoint si aggiornano con frequenze diverse:
- **UniProt**: Release trimestrali
- **WikiPathways**: Aggiornamenti continui dalla community
- **STRING**: Release periodiche
- **Reactome**: Release trimestrali

### Citazioni

Se usi questi dati nelle tue ricerche, ricorda di citare:
- UniProt Consortium
- STRING database
- WikiPathways
- Reactome
- Protein Ontology Consortium

---

## Contatti e Supporto

- **UniProt Help**: https://www.uniprot.org/help/
- **STRING**: https://string-db.org/help/
- **WikiPathways Forum**: https://www.wikipathways.org/
- **Reactome Help**: help@reactome.org

---

**Creato:** Gennaio 2026  
**Versione:** 1.0  
**Maintainer:** Documentazione per uso con Claude Code + RDF Explorer

