"""
Enrichment Comparator Module
Confronta interattori da fonti diverse (letteratura/PDF vs database) e identifica gap di conoscenza
"""

import json
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class ComparisonResult:
    """Risultato del confronto tra fonti"""
    gene: str
    source_a: str
    source_b: str
    only_in_a: Set[str] = field(default_factory=set)
    only_in_b: Set[str] = field(default_factory=set)
    in_both: Set[str] = field(default_factory=set)
    overlap_score: float = 0.0


@dataclass
class GapAnalysis:
    """Analisi dei gap di conoscenza"""
    missing_in_databases: List[Dict] = field(default_factory=list)
    missing_in_literature: List[Dict] = field(default_factory=list)
    validation_candidates: List[Dict] = field(default_factory=list)
    confidence_assessment: Dict = field(default_factory=dict)


class EnrichmentComparator:
    """
    Confronta interattori da diverse fonti e identifica:
    - Interazioni documentate solo in letteratura (gap nei database)
    - Interazioni nei database ma non nella letteratura (nuove scoperte)
    - Candidati per validazione sperimentale
    """

    def __init__(self):
        self.literature_data: Dict[str, Set[str]] = {}
        self.database_data: Dict[str, Dict] = {}

    def load_literature_interactors(self, gene: str, interactors: List[str],
                                    metadata: Optional[Dict] = None):
        """
        Carica interattori da letteratura/PDF.

        Args:
            gene: Gene centrale
            interactors: Lista di geni interattori
            metadata: Metadati opzionali (fonte, tipo interazione, etc.)
        """
        self.literature_data[gene] = {
            "interactors": set(i.upper() for i in interactors),
            "metadata": metadata or {}
        }

    def load_database_interactors(self, gene: str, aggregated_data: Dict):
        """
        Carica interattori da dati aggregati (output di SPARQLAggregator).

        Args:
            gene: Gene centrale
            aggregated_data: Dizionario con dati aggregati
        """
        interactors = set()

        # Estrai interattori dalle interazioni STRING
        for interaction in aggregated_data.get("interactions", []):
            partner = interaction.get("partner", "")
            if partner:
                interactors.add(partner.upper())

        self.database_data[gene] = {
            "interactors": interactors,
            "full_data": aggregated_data
        }

    def compare_sources(self, gene: str) -> ComparisonResult:
        """
        Confronta interattori da letteratura vs database per un gene.

        Returns:
            ComparisonResult con overlap e differenze
        """
        lit_interactors = self.literature_data.get(gene, {}).get("interactors", set())
        db_interactors = self.database_data.get(gene, {}).get("interactors", set())

        only_in_lit = lit_interactors - db_interactors
        only_in_db = db_interactors - lit_interactors
        in_both = lit_interactors & db_interactors

        # Calcola Jaccard similarity
        union = lit_interactors | db_interactors
        overlap_score = len(in_both) / len(union) if union else 0.0

        return ComparisonResult(
            gene=gene,
            source_a="Literature",
            source_b="Databases",
            only_in_a=only_in_lit,
            only_in_b=only_in_db,
            in_both=in_both,
            overlap_score=overlap_score
        )

    def analyze_gaps(self, gene: str) -> GapAnalysis:
        """
        Analizza i gap di conoscenza per un gene.

        Returns:
            GapAnalysis con dettagli su missing data e candidati
        """
        comparison = self.compare_sources(gene)
        lit_metadata = self.literature_data.get(gene, {}).get("metadata", {})
        db_data = self.database_data.get(gene, {}).get("full_data", {})

        # Gap nei database (presente in letteratura ma non nei DB)
        missing_in_db = []
        for interactor in comparison.only_in_a:
            missing_in_db.append({
                "gene": interactor,
                "status": "NOT_IN_DATABASES",
                "suggestion": "Verifica se l'interazione è recente o non ancora annotata",
                "action": "Candidato per submission a STRING/IntAct"
            })

        # Gap nella letteratura (presente nei DB ma non citato)
        missing_in_lit = []
        interactions_dict = {
            i.get("partner", "").upper(): i
            for i in db_data.get("interactions", [])
        }

        for interactor in comparison.only_in_b:
            interaction_info = interactions_dict.get(interactor, {})
            missing_in_lit.append({
                "gene": interactor,
                "status": "NOT_IN_LITERATURE",
                "score": interaction_info.get("score", 0),
                "evidence": interaction_info.get("evidence", ""),
                "suggestion": "Potenziale nuova interazione da investigare"
            })

        # Ordina per score
        missing_in_lit.sort(key=lambda x: x.get("score", 0), reverse=True)

        # Candidati per validazione (alta confidenza ma non in letteratura)
        validation_candidates = [
            item for item in missing_in_lit
            if item.get("score", 0) >= 0.7
        ]

        # Assessment di confidenza
        confidence = {
            "total_literature": len(comparison.only_in_a) + len(comparison.in_both),
            "total_databases": len(comparison.only_in_b) + len(comparison.in_both),
            "overlap_count": len(comparison.in_both),
            "overlap_percentage": round(comparison.overlap_score * 100, 1),
            "gaps_in_databases": len(comparison.only_in_a),
            "gaps_in_literature": len(comparison.only_in_b),
            "high_confidence_candidates": len(validation_candidates)
        }

        return GapAnalysis(
            missing_in_databases=missing_in_db,
            missing_in_literature=missing_in_lit,
            validation_candidates=validation_candidates,
            confidence_assessment=confidence
        )

    def generate_report(self, gene: str, output_format: str = "text") -> str:
        """
        Genera report di confronto.

        Args:
            gene: Gene da analizzare
            output_format: "text", "json", o "markdown"

        Returns:
            Report formattato
        """
        comparison = self.compare_sources(gene)
        gap_analysis = self.analyze_gaps(gene)

        if output_format == "json":
            return json.dumps({
                "gene": gene,
                "comparison": {
                    "only_in_literature": list(comparison.only_in_a),
                    "only_in_databases": list(comparison.only_in_b),
                    "in_both": list(comparison.in_both),
                    "overlap_score": comparison.overlap_score
                },
                "gap_analysis": {
                    "missing_in_databases": gap_analysis.missing_in_databases,
                    "missing_in_literature": gap_analysis.missing_in_literature,
                    "validation_candidates": gap_analysis.validation_candidates,
                    "confidence": gap_analysis.confidence_assessment
                }
            }, indent=2, ensure_ascii=False)

        elif output_format == "markdown":
            return self._generate_markdown_report(gene, comparison, gap_analysis)

        else:
            return self._generate_text_report(gene, comparison, gap_analysis)

    def _generate_text_report(self, gene: str, comparison: ComparisonResult,
                              gap_analysis: GapAnalysis) -> str:
        """Genera report testuale"""

        lines = []
        lines.append("=" * 70)
        lines.append(f"ENRICHMENT COMPARISON REPORT: {gene}")
        lines.append("=" * 70)

        # Summary
        conf = gap_analysis.confidence_assessment
        lines.append(f"\n{'SUMMARY':^70}")
        lines.append("-" * 70)
        lines.append(f"  Interattori da letteratura:  {conf['total_literature']}")
        lines.append(f"  Interattori da database:     {conf['total_databases']}")
        lines.append(f"  Overlap:                     {conf['overlap_count']} ({conf['overlap_percentage']}%)")
        lines.append(f"  Gap nei database:            {conf['gaps_in_databases']}")
        lines.append(f"  Gap nella letteratura:       {conf['gaps_in_literature']}")

        # Overlap
        lines.append(f"\n{'INTERATTORI CONFERMATI (in entrambe le fonti)':^70}")
        lines.append("-" * 70)
        if comparison.in_both:
            for gene_name in sorted(comparison.in_both):
                lines.append(f"  [OK] {gene_name}")
        else:
            lines.append("  Nessun overlap trovato")

        # Only in literature
        lines.append(f"\n{'GAP NEI DATABASE (solo in letteratura)':^70}")
        lines.append("-" * 70)
        if comparison.only_in_a:
            for item in gap_analysis.missing_in_databases:
                lines.append(f"  [!] {item['gene']}")
                lines.append(f"      -> {item['suggestion']}")
        else:
            lines.append("  Tutti gli interattori sono presenti nei database")

        # Only in databases
        lines.append(f"\n{'NUOVE INTERAZIONI DA DATABASE (non in letteratura)':^70}")
        lines.append("-" * 70)
        if gap_analysis.missing_in_literature:
            for item in gap_analysis.missing_in_literature[:10]:  # Top 10
                score_bar = "#" * int(item.get('score', 0) * 10)
                lines.append(f"  [+] {item['gene']:<12} Score: {item.get('score', 0):.3f} {score_bar}")
                if item.get('evidence'):
                    lines.append(f"      Evidence: {item['evidence']}")
        else:
            lines.append("  Nessuna nuova interazione trovata")

        # Validation candidates
        lines.append(f"\n{'CANDIDATI PER VALIDAZIONE SPERIMENTALE':^70}")
        lines.append("-" * 70)
        if gap_analysis.validation_candidates:
            for item in gap_analysis.validation_candidates[:5]:  # Top 5
                lines.append(f"  [*] {item['gene']:<12} Score: {item.get('score', 0):.3f}")
                lines.append(f"      -> Alta confidenza, non documentato in letteratura")
        else:
            lines.append("  Nessun candidato ad alta confidenza")

        lines.append("\n" + "=" * 70)

        return "\n".join(lines)

    def _generate_markdown_report(self, gene: str, comparison: ComparisonResult,
                                   gap_analysis: GapAnalysis) -> str:
        """Genera report in Markdown"""

        lines = []
        conf = gap_analysis.confidence_assessment

        lines.append(f"# Enrichment Comparison Report: {gene}\n")

        # Summary table
        lines.append("## Summary\n")
        lines.append("| Metrica | Valore |")
        lines.append("|---------|--------|")
        lines.append(f"| Interattori letteratura | {conf['total_literature']} |")
        lines.append(f"| Interattori database | {conf['total_databases']} |")
        lines.append(f"| Overlap | {conf['overlap_count']} ({conf['overlap_percentage']}%) |")
        lines.append(f"| Gap nei database | {conf['gaps_in_databases']} |")
        lines.append(f"| Gap in letteratura | {conf['gaps_in_literature']} |")
        lines.append("")

        # Confirmed
        lines.append("## Interattori Confermati\n")
        if comparison.in_both:
            for g in sorted(comparison.in_both):
                lines.append(f"- ✅ **{g}**")
        else:
            lines.append("*Nessun overlap*")
        lines.append("")

        # Gaps in DB
        lines.append("## Gap nei Database\n")
        lines.append("*Interattori presenti in letteratura ma non nei database*\n")
        if comparison.only_in_a:
            for item in gap_analysis.missing_in_databases:
                lines.append(f"- ⚠️ **{item['gene']}** - {item['suggestion']}")
        else:
            lines.append("*Tutti presenti*")
        lines.append("")

        # New from DB
        lines.append("## Nuove Interazioni da Database\n")
        if gap_analysis.missing_in_literature:
            lines.append("| Gene | Score | Evidenza |")
            lines.append("|------|-------|----------|")
            for item in gap_analysis.missing_in_literature[:10]:
                lines.append(f"| {item['gene']} | {item.get('score', 0):.3f} | {item.get('evidence', '-')} |")
        else:
            lines.append("*Nessuna*")
        lines.append("")

        # Candidates
        lines.append("## Candidati per Validazione\n")
        if gap_analysis.validation_candidates:
            for item in gap_analysis.validation_candidates[:5]:
                lines.append(f"- 🔬 **{item['gene']}** (score: {item.get('score', 0):.3f})")
        else:
            lines.append("*Nessun candidato ad alta confidenza*")

        return "\n".join(lines)

    def export_for_cytoscape(self, gene: str) -> Dict:
        """
        Esporta dati in formato compatibile con Cytoscape.

        Returns:
            Dizionario con nodi e archi per import in Cytoscape
        """
        comparison = self.compare_sources(gene)
        db_data = self.database_data.get(gene, {}).get("full_data", {})

        nodes = []
        edges = []

        # Nodo centrale
        nodes.append({
            "id": gene,
            "label": gene,
            "type": "central",
            "source": "both"
        })

        # Interattori
        interactions_dict = {
            i.get("partner", "").upper(): i
            for i in db_data.get("interactions", [])
        }

        for interactor in comparison.in_both:
            info = interactions_dict.get(interactor, {})
            nodes.append({
                "id": interactor,
                "label": interactor,
                "type": "interactor",
                "source": "both"
            })
            edges.append({
                "source": gene,
                "target": interactor,
                "score": info.get("score", 0),
                "evidence": info.get("evidence", ""),
                "validation": "confirmed"
            })

        for interactor in comparison.only_in_a:
            nodes.append({
                "id": interactor,
                "label": interactor,
                "type": "interactor",
                "source": "literature_only"
            })
            edges.append({
                "source": gene,
                "target": interactor,
                "score": 0,
                "evidence": "literature",
                "validation": "literature_only"
            })

        for interactor in comparison.only_in_b:
            info = interactions_dict.get(interactor, {})
            nodes.append({
                "id": interactor,
                "label": interactor,
                "type": "interactor",
                "source": "database_only"
            })
            edges.append({
                "source": gene,
                "target": interactor,
                "score": info.get("score", 0),
                "evidence": info.get("evidence", ""),
                "validation": "database_only"
            })

        return {
            "nodes": nodes,
            "edges": edges
        }


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    comparator = EnrichmentComparator()

    # Simula dati da letteratura (dal PDF)
    literature_interactors = [
        "GRK7", "AIPL1", "DAG1", "POMGNT1", "POMT2", "PROM1", "KIF19", "PDE6D"
    ]

    comparator.load_literature_interactors("EYS", literature_interactors, {
        "source": "PDF - Modellazione RDF Gene EYS",
        "confidence": "curated"
    })

    # Simula dati da database (STRING)
    mock_db_data = {
        "interactions": [
            {"partner": "CERKL", "score": 0.857, "evidence": "textmining"},
            {"partner": "IMPG2", "score": 0.856, "evidence": "textmining"},
            {"partner": "PRPF31", "score": 0.841, "evidence": "textmining"},
            {"partner": "PCARE", "score": 0.841, "evidence": "textmining"},
            {"partner": "RPGR", "score": 0.837, "evidence": "textmining, experimental"},
            {"partner": "ABCA4", "score": 0.834, "evidence": "textmining, experimental"},
            {"partner": "PDE6A", "score": 0.814, "evidence": "textmining"},
            {"partner": "RDH12", "score": 0.813, "evidence": "textmining, experimental"},
            {"partner": "CNGB1", "score": 0.810, "evidence": "textmining"},
            {"partner": "TULP1", "score": 0.801, "evidence": "textmining"},
            {"partner": "PRPH2", "score": 0.788, "evidence": "textmining"},
            {"partner": "FSCN2", "score": 0.740, "evidence": "textmining"},
        ]
    }

    comparator.load_database_interactors("EYS", mock_db_data)

    # Genera report
    print(comparator.generate_report("EYS", "text"))
