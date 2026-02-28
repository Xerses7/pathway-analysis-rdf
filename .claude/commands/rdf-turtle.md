# RDF Turtle

Genera un file RDF in formato Turtle (.ttl) per un gene e i suoi interattori, combinando dati da UniProt, STRING e dal PDF di riferimento del progetto.

## Come usare
`/rdf-turtle GENE_SYMBOL`

Esempio: `/rdf-turtle EYS` oppure `/rdf-turtle AIPL1`

## Istruzioni per Claude

Il gene da modellare è: $ARGUMENTS

Segui questi passi:

1. **Aggrega i dati** eseguendo lo script e interrogando gli endpoint:
   ```
   cd "C:\Users\d_pir\Documents\Prog\Pathway retina RDF\ppi_analyzer"
   python main.py --gene $ARGUMENTS --output $ARGUMENTS_data.json --format json
   ```

2. **Costruisci il file Turtle** con questa struttura:

   ### Prefissi standard da usare:
   ```turtle
   @prefix rdf:     <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
   @prefix rdfs:    <http://www.w3.org/2000/01/rdf-schema#> .
   @prefix owl:     <http://www.w3.org/2002/07/owl#> .
   @prefix xsd:     <http://www.w3.org/2001/XMLSchema#> .
   @prefix up:      <http://purl.uniprot.org/core/> .
   @prefix taxon:   <http://purl.uniprot.org/taxonomy/> .
   @prefix go:      <http://purl.obolibrary.org/obo/> .
   @prefix hgnc:    <http://www.genenames.org/data/gene-symbol-report/#!/hgnc_id/> .
   @prefix bio:     <http://purl.org/obo/owlapi/> .
   @prefix retina:  <http://example.org/retina-pathway/> .
   @prefix string:  <https://string-db.org/network/> .
   ```

   ### Triple da generare:

   **Identità proteina:**
   ```turtle
   retina:GENE a up:Protein ;
       hgnc:symbol "GENE"^^xsd:string ;
       rdfs:label "FULL_PROTEIN_NAME"^^xsd:string ;
       up:organism taxon:9606 ;
       up:mnemonic "UNIPROT_ID"^^xsd:string .
   ```

   **GO terms (separati per categoria):**
   ```turtle
   retina:GENE go:cellular_component go:GO_XXXXXXX ;   # component
               go:molecular_function go:GO_XXXXXXX ;   # function
               go:biological_process go:GO_XXXXXXX .   # process
   ```

   **Malattie associate:**
   ```turtle
   retina:GENE retina:associatedDisease retina:DISEASE_NAME .
   retina:DISEASE_NAME rdfs:label "Disease description"^^xsd:string .
   ```

   **Interazioni fisiche (da letteratura, alta confidenza):**
   ```turtle
   retina:GENE retina:physicallyInteractsWith retina:INTERACTOR ;
       retina:interactionEvidence "Co-IP"^^xsd:string ;
       retina:interactionSource "Literature"^^xsd:string .
   ```

   **Interazioni funzionali (da STRING):**
   ```turtle
   retina:GENE retina:functionallyAssociatedWith retina:INTERACTOR ;
       retina:stringScore "0.856"^^xsd:decimal ;
       retina:stringEvidence "textmining, coexpression"^^xsd:string .
   ```

   **Pathway:**
   ```turtle
   retina:GENE retina:isPartOfPathway retina:PATHWAY_ID .
   retina:PATHWAY_ID rdfs:label "Pathway title"^^xsd:string .
   ```

3. **Distingui chiaramente** interazioni fisiche (letteratura) vs funzionali (database):
   - `retina:physicallyInteractsWith` → confermato sperimentalmente
   - `retina:functionallyAssociatedWith` → da database (STRING/WikiPathways)
   - `retina:transportRegulates` → relazione di trasporto (es. EYS → GRK7)
   - `retina:regulatesLocalizationOf` → regolazione indiretta

4. **Salva il file**:
   ```
   C:\Users\d_pir\Documents\Prog\Pathway retina RDF\GENE_ontology.ttl
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
   - N patologie

7. **Suggerisci** come caricare il file in un triple store locale (es. Apache Jena Fuseki) o come usarlo con rdflib in Python.

### Nota sul gene EYS
Se il gene è EYS, includi anche le varianti genetiche dal PDF:
```turtle
retina:EYS_Variant_1 a retina:GeneticVariant ;
    retina:hgvsNotation "c.8648_8655del"^^xsd:string ;
    retina:variantType "deletion"^^xsd:string ;
    retina:affectsGene retina:EYS .
```
