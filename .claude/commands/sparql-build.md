# SPARQL Build

Genera ed esegue query SPARQL personalizzate sugli endpoint bioinformatici (UniProt, STRING, WikiPathways) partendo da una descrizione in linguaggio naturale.

## Come usare
`/sparql-build DESCRIZIONE IN LINGUAGGIO NATURALE`

Esempi:
- `/sparql-build proteine umane associate a Retinitis Pigmentosa con GO term cilio`
- `/sparql-build interattori di RPGR con score STRING maggiore di 0.8`
- `/sparql-build pathway WikiPathways che contengono EYS e PRPF31`
- `/sparql-build varianti genetiche di EYS e loro effetto`

## Istruzioni per Claude

La richiesta dell'utente è: $ARGUMENTS

Segui questi passi:

1. **Analizza la richiesta** e determina:
   - Quale endpoint è più adatto (UniProt / STRING API / WikiPathways)
   - Quali entità biologiche sono coinvolte (geni, proteine, patologie, GO terms)
   - Che tipo di risultato si aspetta l'utente (lista proteine, interazioni, pathway, varianti)

2. **Consulta i template** nel file di riferimento:
   `C:\Users\d_pir\Documents\Prog\Pathway retina RDF\sparql_endpoints_bioinformatics.md`
   Usa i prefissi e pattern già documentati.

3. **Costruisci la query SPARQL** (o API call per STRING):
   - Aggiungi sempre LIMIT 100 per query esplorative
   - Usa FILTER con LCASE() per ricerche case-insensitive
   - Mostra la query completa con tutti i prefissi
   - Spiega ogni clausola con un commento inline

4. **Esegui la query** via WebFetch sull'endpoint appropriato:
   - UniProt: `https://sparql.uniprot.org/sparql?format=json&query=ENCODED_QUERY`
   - WikiPathways: `https://sparql.wikipathways.org/sparql?format=json&query=ENCODED_QUERY`
   - STRING: `https://string-db.org/api/json/ENDPOINT?identifiers=GENE&species=9606`

5. **Presenta i risultati** in formato tabellare leggibile:
   - Massimo 20 risultati mostrati
   - Aggiungi interpretazione biologica dei risultati
   - Se la query non restituisce risultati, suggerisci varianti alternative

6. **Offri di salvare** la query in un file .sparql per uso futuro:
   ```
   C:\Users\d_pir\Documents\Prog\Pathway retina RDF\queries\NOME_QUERY.sparql
   ```

### Endpoint e prefissi di riferimento

**UniProt:**
```sparql
PREFIX up: <http://purl.uniprot.org/core/>
PREFIX taxon: <http://purl.uniprot.org/taxonomy/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
# Homo sapiens = taxon:9606
```

**WikiPathways:**
```sparql
PREFIX wp: <http://vocabularies.wikipathways.org/wp#>
PREFIX dc: <http://purl.org/dc/elements/1.1/>
PREFIX dcterms: <http://purl.org/dc/terms/>
```

**STRING API:**
```
https://string-db.org/api/json/network?identifiers=GENE&species=9606&required_score=700
https://string-db.org/api/json/interaction_partners?identifiers=GENE&species=9606
```
