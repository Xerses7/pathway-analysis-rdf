# RDF Turtle

Genera un file RDF in formato Turtle (.ttl) per qualsiasi gene umano e i suoi interattori, combinando dati da UniProt e STRING in un grafo semantico riutilizzabile.

## Come usare
`/rdf-turtle GENE_SYMBOL`

Esempi: `/rdf-turtle TP53` oppure `/rdf-turtle EGFR` oppure `/rdf-turtle BRCA1`

## Istruzioni per Claude

Il gene da modellare è: $ARGUMENTS

Segui questi passi:

1. **Aggrega i dati** eseguendo lo script:
   ```
   python ppi_analyzer/main.py --gene $ARGUMENTS --output $ARGUMENTS_data.json --format json
   ```

2. **Costruisci il file Turtle** con questa struttura:

   ### Prefissi standard da usare:
   ```turtle
   @prefix rdf:   <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
   @prefix rdfs:  <http://www.w3.org/2000/01/rdf-schema#> .
   @prefix owl:   <http://www.w3.org/2002/07/owl#> .
   @prefix xsd:   <http://www.w3.org/2001/XMLSchema#> .
   @prefix up:    <http://purl.uniprot.org/core/> .
   @prefix taxon: <http://purl.uniprot.org/taxonomy/> .
   @prefix go:    <http://purl.obolibrary.org/obo/> .
   @prefix hgnc:  <http://www.genenames.org/data/gene-symbol-report/#!/hgnc_id/> .
   @prefix pn:    <http://example.org/protein-network/> .
   @prefix string: <https://string-db.org/network/> .
   ```

   ### Triple da generare:

   **Identità proteina:**
   ```turtle
   pn:GENE a up:Protein ;
       hgnc:symbol "GENE"^^xsd:string ;
       rdfs:label "FULL_PROTEIN_NAME"^^xsd:string ;
       up:organism taxon:9606 ;
       up:mnemonic "UNIPROT_ID"^^xsd:string .
   ```

   **GO terms (separati per categoria):**
   ```turtle
   pn:GENE go:cellular_component go:GO_XXXXXXX ;
           go:molecular_function go:GO_XXXXXXX ;
           go:biological_process go:GO_XXXXXXX .
   ```

   **Malattie associate:**
   ```turtle
   pn:GENE pn:associatedDisease pn:DISEASE_NAME .
   pn:DISEASE_NAME rdfs:label "Disease description"^^xsd:string .
   ```

   **Interazioni fisiche (da letteratura):**
   ```turtle
   pn:GENE pn:physicallyInteractsWith pn:INTERACTOR ;
       pn:interactionEvidence "Co-IP"^^xsd:string ;
       pn:interactionSource "Literature"^^xsd:string .
   ```

   **Interazioni funzionali (da STRING):**
   ```turtle
   pn:GENE pn:functionallyAssociatedWith pn:INTERACTOR ;
       pn:stringScore "0.856"^^xsd:decimal ;
       pn:stringEvidence "textmining, coexpression"^^xsd:string .
   ```

   **Pathway:**
   ```turtle
   pn:GENE pn:isPartOfPathway pn:PATHWAY_ID .
   pn:PATHWAY_ID rdfs:label "Pathway title"^^xsd:string .
   ```

3. **Distingui chiaramente** interazioni fisiche vs funzionali:
   - `pn:physicallyInteractsWith` → confermato sperimentalmente (Co-IP, Y2H, pull-down)
   - `pn:functionallyAssociatedWith` → da database (STRING/WikiPathways, coexpression, textmining)

4. **Salva il file** nella cartella del progetto:
   ```
   ./output/$ARGUMENTS_ontology.ttl
   ```

5. **Valida la sintassi** verificando che:
   - Tutti i prefissi siano dichiarati
   - Ogni triple termini con `.` o `;` correttamente
   - Gli URI siano ben formati
   - I literal abbiano il tipo xsd corretto (string, decimal, integer)

6. **Mostra un riepilogo** delle triple generate:
   - N triple totali
   - N interazioni fisiche
   - N interazioni funzionali
   - N GO terms
   - N patologie associate

7. **Suggerisci** come caricare il file in un triple store locale (es. Apache Jena Fuseki) o come interrogarlo con rdflib in Python:
   ```python
   from rdflib import Graph
   g = Graph()
   g.parse("$ARGUMENTS_ontology.ttl", format="turtle")
   print(f"Triple caricate: {len(g)}")
   ```
