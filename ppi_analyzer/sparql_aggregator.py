"""
SPARQL Aggregator Module
Raccoglie e unifica dati da multipli endpoint SPARQL (UniProt, WikiPathways, STRING)
"""

import urllib.request
import urllib.parse
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from config import ENDPOINTS, DEFAULT_ORGANISM, DEFAULT_CONFIDENCE, DEFAULT_LIMIT


@dataclass
class ProteinInfo:
    """Informazioni su una proteina"""
    gene_symbol: str
    uniprot_id: str = ""
    protein_name: str = ""
    organism: str = "Homo sapiens"
    go_terms: List[Dict[str, str]] = field(default_factory=list)
    diseases: List[str] = field(default_factory=list)
    domains: List[str] = field(default_factory=list)
    pathways: List[Dict[str, str]] = field(default_factory=list)
    source: str = ""


@dataclass
class Interaction:
    """Interazione proteina-proteina"""
    protein_a: str
    protein_b: str
    score: float = 0.0
    evidence_type: str = ""
    source: str = ""


class SPARQLAggregator:
    """
    Aggregatore di dati da multipli endpoint SPARQL.
    Unifica risultati da UniProt, STRING, WikiPathways.
    """

    def __init__(self, organism: str = DEFAULT_ORGANISM):
        self.organism = organism
        self.cache: Dict[str, Any] = {}

    def _execute_sparql(self, endpoint_url: str, query: str) -> Optional[Dict]:
        """Esegue una query SPARQL e ritorna i risultati JSON"""
        try:
            encoded_query = urllib.parse.quote(query)
            url = f"{endpoint_url}?format=json&query={encoded_query}"

            req = urllib.request.Request(url)
            req.add_header('Accept', 'application/sparql-results+json')
            req.add_header('User-Agent', 'PPI-Analyzer/1.0')

            with urllib.request.urlopen(req, timeout=60) as response:
                return json.loads(response.read().decode('utf-8'))
        except Exception as e:
            print(f"[ERRORE] Query SPARQL fallita: {e}")
            return None

    def _call_string_api(self, endpoint: str, params: Dict) -> Optional[List]:
        """Chiama l'API REST di STRING"""
        try:
            base_url = f"https://string-db.org/api/json/{endpoint}"
            query_string = urllib.parse.urlencode(params)
            url = f"{base_url}?{query_string}"

            req = urllib.request.Request(url)
            req.add_header('User-Agent', 'PPI-Analyzer/1.0')

            with urllib.request.urlopen(req, timeout=30) as response:
                return json.loads(response.read().decode('utf-8'))
        except Exception as e:
            print(f"[ERRORE] STRING API fallita: {e}")
            return None

    # =========================================================================
    # UNIPROT QUERIES
    # =========================================================================

    def get_protein_info_uniprot(self, gene_symbol: str) -> Optional[ProteinInfo]:
        """Recupera informazioni proteiche da UniProt"""

        query = f"""
        PREFIX up: <http://purl.uniprot.org/core/>
        PREFIX taxon: <http://purl.uniprot.org/taxonomy/>
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT ?protein ?geneName ?proteinName ?function
        WHERE {{
          ?protein a up:Protein ;
                   up:organism taxon:{self.organism} ;
                   up:encodedBy ?gene ;
                   up:recommendedName ?recName .
          ?gene skos:prefLabel ?geneName .
          ?recName up:fullName ?proteinName .
          OPTIONAL {{
            ?protein up:annotation ?ann .
            ?ann a up:Function_Annotation ;
                 rdfs:comment ?function .
          }}
          FILTER (?geneName = "{gene_symbol}")
        }}
        LIMIT 1
        """

        result = self._execute_sparql(ENDPOINTS["uniprot"]["url"], query)

        if result and result.get("results", {}).get("bindings"):
            binding = result["results"]["bindings"][0]
            protein = ProteinInfo(
                gene_symbol=gene_symbol,
                uniprot_id=binding.get("protein", {}).get("value", "").split("/")[-1],
                protein_name=binding.get("proteinName", {}).get("value", ""),
                source="UniProt"
            )
            return protein
        return None

    def get_go_terms_uniprot(self, gene_symbol: str) -> List[Dict[str, str]]:
        """Recupera termini GO da UniProt"""

        query = f"""
        PREFIX up: <http://purl.uniprot.org/core/>
        PREFIX taxon: <http://purl.uniprot.org/taxonomy/>
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT ?goTerm ?goLabel
        WHERE {{
          ?protein a up:Protein ;
                   up:organism taxon:{self.organism} ;
                   up:encodedBy ?gene ;
                   up:classifiedWith ?goTerm .
          ?gene skos:prefLabel ?geneName .
          ?goTerm rdfs:label ?goLabel .
          FILTER (?geneName = "{gene_symbol}")
          FILTER (STRSTARTS(STR(?goTerm), "http://purl.obolibrary.org/obo/GO_"))
        }}
        LIMIT 50
        """

        result = self._execute_sparql(ENDPOINTS["uniprot"]["url"], query)
        go_terms = []

        if result and result.get("results", {}).get("bindings"):
            for binding in result["results"]["bindings"]:
                go_terms.append({
                    "id": binding.get("goTerm", {}).get("value", "").split("/")[-1].replace("_", ":"),
                    "label": binding.get("goLabel", {}).get("value", "")
                })

        return go_terms

    def get_diseases_uniprot(self, gene_symbol: str) -> List[str]:
        """Recupera annotazioni di malattia da UniProt"""

        query = f"""
        PREFIX up: <http://purl.uniprot.org/core/>
        PREFIX taxon: <http://purl.uniprot.org/taxonomy/>
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT DISTINCT ?diseaseText
        WHERE {{
          ?protein a up:Protein ;
                   up:organism taxon:{self.organism} ;
                   up:encodedBy ?gene ;
                   up:annotation ?annotation .
          ?gene skos:prefLabel ?geneName .
          ?annotation a up:Disease_Annotation ;
                      rdfs:comment ?diseaseText .
          FILTER (?geneName = "{gene_symbol}")
        }}
        """

        result = self._execute_sparql(ENDPOINTS["uniprot"]["url"], query)
        diseases = []

        if result and result.get("results", {}).get("bindings"):
            for binding in result["results"]["bindings"]:
                disease = binding.get("diseaseText", {}).get("value", "")
                if disease:
                    diseases.append(disease)

        return diseases

    # =========================================================================
    # STRING QUERIES
    # =========================================================================

    def get_interactions_string(self, gene_symbol: str,
                                min_score: float = DEFAULT_CONFIDENCE) -> List[Interaction]:
        """Recupera interazioni proteina-proteina da STRING"""

        params = {
            "identifiers": gene_symbol,
            "species": self.organism,
            "limit": DEFAULT_LIMIT,
            "required_score": int(min_score * 1000)
        }

        result = self._call_string_api("network", params)
        interactions = []

        if result:
            for item in result:
                # Estrai i nomi dei geni (preferredName)
                gene_a = item.get("preferredName_A", item.get("stringId_A", ""))
                gene_b = item.get("preferredName_B", item.get("stringId_B", ""))
                score = item.get("score", 0)

                # Determina tipo di evidenza
                evidence = []
                if item.get("escore", 0) > 0:
                    evidence.append("experimental")
                if item.get("dscore", 0) > 0:
                    evidence.append("database")
                if item.get("tscore", 0) > 0:
                    evidence.append("textmining")
                if item.get("ascore", 0) > 0:
                    evidence.append("coexpression")

                interactions.append(Interaction(
                    protein_a=gene_a,
                    protein_b=gene_b,
                    score=score,
                    evidence_type=", ".join(evidence) if evidence else "combined",
                    source="STRING"
                ))

        return interactions

    def get_functional_partners_string(self, gene_symbol: str, limit: int = 20) -> List[Dict]:
        """Recupera partner funzionali da STRING con dettagli"""

        params = {
            "identifiers": gene_symbol,
            "species": self.organism,
            "limit": limit
        }

        result = self._call_string_api("interaction_partners", params)
        partners = []

        if result:
            for item in result:
                partners.append({
                    "gene": item.get("preferredName_B", ""),
                    "string_id": item.get("stringId_B", ""),
                    "score": item.get("score", 0),
                    "escore": item.get("escore", 0),
                    "dscore": item.get("dscore", 0),
                    "tscore": item.get("tscore", 0)
                })

        return partners

    # =========================================================================
    # WIKIPATHWAYS QUERIES
    # =========================================================================

    def get_pathways_wikipathways(self, gene_symbol: str) -> List[Dict[str, str]]:
        """Recupera pathway da WikiPathways"""

        query = f"""
        PREFIX wp: <http://vocabularies.wikipathways.org/wp#>
        PREFIX dc: <http://purl.org/dc/elements/1.1/>
        PREFIX dcterms: <http://purl.org/dc/terms/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT DISTINCT ?pathway ?title ?identifier
        WHERE {{
          ?gp a wp:GeneProduct ;
              rdfs:label ?label ;
              dcterms:isPartOf ?pathway .
          ?pathway a wp:Pathway ;
                   dc:title ?title ;
                   dcterms:identifier ?identifier ;
                   wp:organismName "Homo sapiens" .
          FILTER (UCASE(?label) = UCASE("{gene_symbol}"))
        }}
        """

        result = self._execute_sparql(ENDPOINTS["wikipathways"]["url"], query)
        pathways = []

        if result and result.get("results", {}).get("bindings"):
            for binding in result["results"]["bindings"]:
                pathways.append({
                    "id": binding.get("identifier", {}).get("value", ""),
                    "title": binding.get("title", {}).get("value", ""),
                    "url": binding.get("pathway", {}).get("value", "")
                })

        return pathways

    # =========================================================================
    # AGGREGATION
    # =========================================================================

    def aggregate_gene_data(self, gene_symbol: str) -> Dict[str, Any]:
        """
        Aggrega tutti i dati disponibili per un gene da tutte le fonti.
        Ritorna un dizionario unificato.
        """

        print(f"\n[INFO] Aggregando dati per {gene_symbol}...")

        aggregated = {
            "gene_symbol": gene_symbol,
            "sources": [],
            "uniprot": {},
            "go_terms": [],
            "diseases": [],
            "interactions": [],
            "pathways": []
        }

        # UniProt
        print("  -> Interrogando UniProt...")
        protein_info = self.get_protein_info_uniprot(gene_symbol)
        if protein_info:
            aggregated["uniprot"] = {
                "id": protein_info.uniprot_id,
                "name": protein_info.protein_name
            }
            aggregated["sources"].append("UniProt")

        # GO Terms
        go_terms = self.get_go_terms_uniprot(gene_symbol)
        if go_terms:
            aggregated["go_terms"] = go_terms

        # Diseases
        diseases = self.get_diseases_uniprot(gene_symbol)
        if diseases:
            aggregated["diseases"] = diseases

        # STRING interactions
        print("  -> Interrogando STRING...")
        interactions = self.get_interactions_string(gene_symbol)
        if interactions:
            aggregated["interactions"] = [
                {
                    "partner": i.protein_b if i.protein_a.upper() == gene_symbol.upper() else i.protein_a,
                    "score": i.score,
                    "evidence": i.evidence_type
                }
                for i in interactions
            ]
            aggregated["sources"].append("STRING")

        # WikiPathways
        print("  -> Interrogando WikiPathways...")
        pathways = self.get_pathways_wikipathways(gene_symbol)
        if pathways:
            aggregated["pathways"] = pathways
            aggregated["sources"].append("WikiPathways")

        print(f"[OK] Dati aggregati da {len(aggregated['sources'])} fonti")

        return aggregated

    def aggregate_multiple_genes(self, gene_list: List[str]) -> Dict[str, Dict]:
        """Aggrega dati per multipli geni"""

        all_data = {}
        for gene in gene_list:
            all_data[gene] = self.aggregate_gene_data(gene)

        return all_data


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    aggregator = SPARQLAggregator()

    # Test con EYS
    data = aggregator.aggregate_gene_data("EYS")

    print("\n" + "="*60)
    print("RISULTATI AGGREGATI PER EYS")
    print("="*60)
    print(json.dumps(data, indent=2, ensure_ascii=False))
