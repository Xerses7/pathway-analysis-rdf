#!/usr/bin/env python3
"""
PPI Analyzer - Main Application
Applicazione per analisi interazioni proteina-proteina e confronto fonti

Uso:
    python main.py --gene EYS
    python main.py --gene EYS --literature GRK7,AIPL1,DAG1
    python main.py --gene EYS --output report.md --format markdown
"""

import argparse
import json
import sys
import os

# Aggiungi directory corrente al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sparql_aggregator import SPARQLAggregator
from enrichment_comparator import EnrichmentComparator
from config import COLORS


def print_header():
    """Stampa header dell'applicazione"""
    header = """
+==============================================================================+
|                                                                              |
|   ____  ____  ___     _    _   _    _    _  __   _______ ____                |
|  |  _ \\|  _ \\|_ _|   / \\  | \\ | |  / \\  | | \\ \\ / /_  / | ___|               |
|  | |_) | |_) || |   / _ \\ |  \\| | / _ \\ | |  \\ V / / /  |  _|                |
|  |  __/|  __/ | |  / ___ \\| |\\  |/ ___ \\| |___| | / /__ | |___               |
|  |_|   |_|   |___|/_/   \\_\\_| \\_/_/   \\_\\_____|_|/_____|_____|               |
|                                                                              |
|            SPARQL Aggregator & Enrichment Comparator v1.0                    |
|                                                                              |
+==============================================================================+
    """
    print(header)


def print_section(title: str):
    """Stampa intestazione di sezione"""
    print(f"\n{COLORS['cyan']}{'-'*70}{COLORS['end']}")
    print(f"{COLORS['bold']}{title}{COLORS['end']}")
    print(f"{COLORS['cyan']}{'-'*70}{COLORS['end']}")


def run_aggregation(gene: str, output_file: str = None) -> dict:
    """Esegue aggregazione dati da tutti gli endpoint"""

    print_section(f"AGGREGAZIONE DATI PER {gene}")

    aggregator = SPARQLAggregator()
    data = aggregator.aggregate_gene_data(gene)

    # Mostra risultati
    print(f"\n{COLORS['green']}Fonti interrogate:{COLORS['end']} {', '.join(data['sources'])}")

    if data.get('uniprot', {}).get('id'):
        print(f"\n{COLORS['bold']}UniProt:{COLORS['end']}")
        print(f"  ID: {data['uniprot']['id']}")
        print(f"  Nome: {data['uniprot']['name']}")

    if data.get('go_terms'):
        print(f"\n{COLORS['bold']}GO Terms:{COLORS['end']} {len(data['go_terms'])} trovati")
        for go in data['go_terms'][:5]:
            print(f"  - {go['id']}: {go['label']}")
        if len(data['go_terms']) > 5:
            print(f"  ... e altri {len(data['go_terms'])-5}")

    if data.get('diseases'):
        print(f"\n{COLORS['bold']}Malattie associate:{COLORS['end']}")
        for disease in data['diseases'][:3]:
            print(f"  - {disease[:80]}...")

    if data.get('interactions'):
        print(f"\n{COLORS['bold']}Interazioni STRING:{COLORS['end']} {len(data['interactions'])} trovate")
        for inter in data['interactions'][:5]:
            score_bar = "#" * int(inter['score'] * 10)
            print(f"  - {inter['partner']:<12} {inter['score']:.3f} {score_bar}")
        if len(data['interactions']) > 5:
            print(f"  ... e altre {len(data['interactions'])-5}")

    if data.get('pathways'):
        print(f"\n{COLORS['bold']}Pathway WikiPathways:{COLORS['end']} {len(data['pathways'])} trovati")
        for pw in data['pathways'][:3]:
            print(f"  - [{pw['id']}] {pw['title']}")

    # Salva su file se richiesto
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"\n{COLORS['green']}[OK] Dati salvati in {output_file}{COLORS['end']}")

    return data


def run_comparison(gene: str, literature_genes: list, db_data: dict,
                   output_file: str = None, output_format: str = "text") -> str:
    """Esegue confronto tra letteratura e database"""

    print_section(f"CONFRONTO FONTI PER {gene}")

    comparator = EnrichmentComparator()

    # Carica dati
    comparator.load_literature_interactors(gene, literature_genes, {
        "source": "User input / Literature",
        "confidence": "curated"
    })
    comparator.load_database_interactors(gene, db_data)

    # Genera report
    report = comparator.generate_report(gene, output_format)
    print(report)

    # Salva su file se richiesto
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"\n{COLORS['green']}[OK] Report salvato in {output_file}{COLORS['end']}")

    return report


def run_cytoscape_export(gene: str, literature_genes: list, db_data: dict,
                         output_file: str):
    """Esporta dati per Cytoscape"""

    print_section(f"EXPORT CYTOSCAPE PER {gene}")

    comparator = EnrichmentComparator()
    comparator.load_literature_interactors(gene, literature_genes)
    comparator.load_database_interactors(gene, db_data)

    cytoscape_data = comparator.export_for_cytoscape(gene)

    # Salva nodi
    nodes_file = output_file.replace('.json', '_nodes.csv')
    with open(nodes_file, 'w', encoding='utf-8') as f:
        f.write("id,label,type,source\n")
        for node in cytoscape_data['nodes']:
            f.write(f"{node['id']},{node['label']},{node['type']},{node['source']}\n")

    # Salva archi
    edges_file = output_file.replace('.json', '_edges.csv')
    with open(edges_file, 'w', encoding='utf-8') as f:
        f.write("source,target,score,evidence,validation\n")
        for edge in cytoscape_data['edges']:
            f.write(f"{edge['source']},{edge['target']},{edge['score']},{edge['evidence']},{edge['validation']}\n")

    # Salva JSON completo
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(cytoscape_data, f, indent=2)

    print(f"{COLORS['green']}[OK] Esportati:{COLORS['end']}")
    print(f"  - {nodes_file} ({len(cytoscape_data['nodes'])} nodi)")
    print(f"  - {edges_file} ({len(cytoscape_data['edges'])} archi)")
    print(f"  - {output_file} (JSON completo)")


def interactive_mode():
    """Modalità interattiva"""

    print_header()

    while True:
        print(f"\n{COLORS['bold']}Opzioni:{COLORS['end']}")
        print("  1. Aggrega dati per un gene")
        print("  2. Confronta letteratura vs database")
        print("  3. Esporta per Cytoscape")
        print("  4. Analisi completa EYS (demo)")
        print("  5. Esci")

        choice = input(f"\n{COLORS['cyan']}Scelta [1-5]: {COLORS['end']}").strip()

        if choice == "1":
            gene = input("Gene symbol: ").strip().upper()
            if gene:
                run_aggregation(gene)

        elif choice == "2":
            gene = input("Gene symbol: ").strip().upper()
            lit_input = input("Interattori da letteratura (separati da virgola): ").strip()
            literature_genes = [g.strip().upper() for g in lit_input.split(",") if g.strip()]

            if gene and literature_genes:
                db_data = run_aggregation(gene)
                run_comparison(gene, literature_genes, db_data)

        elif choice == "3":
            gene = input("Gene symbol: ").strip().upper()
            lit_input = input("Interattori da letteratura (separati da virgola): ").strip()
            literature_genes = [g.strip().upper() for g in lit_input.split(",") if g.strip()]
            output = input("File output [cytoscape_export.json]: ").strip() or "cytoscape_export.json"

            if gene and literature_genes:
                db_data = run_aggregation(gene)
                run_cytoscape_export(gene, literature_genes, db_data, output)

        elif choice == "4":
            # Demo completa con EYS
            run_eys_demo()

        elif choice == "5":
            print(f"\n{COLORS['green']}Arrivederci!{COLORS['end']}")
            break

        else:
            print(f"{COLORS['red']}Scelta non valida{COLORS['end']}")


def run_eys_demo():
    """Esegue demo completa con il gene EYS"""

    print_section("DEMO COMPLETA: Gene EYS")

    # Interattori dal PDF
    literature_interactors = [
        "GRK7", "AIPL1", "DAG1", "POMGNT1", "POMT2", "PROM1", "KIF19", "PDE6D"
    ]

    print(f"\n{COLORS['bold']}Interattori da letteratura (PDF):{COLORS['end']}")
    for gene in literature_interactors:
        print(f"  - {gene}")

    # Aggrega dati
    db_data = run_aggregation("EYS")

    # Confronto
    run_comparison("EYS", literature_interactors, db_data, output_format="text")

    # Export Cytoscape
    output_dir = os.path.dirname(os.path.abspath(__file__))
    cytoscape_file = os.path.join(output_dir, "eys_cytoscape.json")
    run_cytoscape_export("EYS", literature_interactors, db_data, cytoscape_file)


def main():
    """Entry point principale"""

    parser = argparse.ArgumentParser(
        description="PPI Analyzer - SPARQL Aggregator & Enrichment Comparator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Esempi:
  python main.py --gene EYS
  python main.py --gene EYS --literature GRK7,AIPL1,DAG1
  python main.py --gene EYS --output report.md --format markdown
  python main.py --interactive
  python main.py --demo
        """
    )

    parser.add_argument("--gene", "-g", type=str, help="Gene symbol da analizzare")
    parser.add_argument("--literature", "-l", type=str,
                        help="Interattori da letteratura (separati da virgola)")
    parser.add_argument("--output", "-o", type=str, help="File di output")
    parser.add_argument("--format", "-f", choices=["text", "json", "markdown"],
                        default="text", help="Formato output (default: text)")
    parser.add_argument("--cytoscape", "-c", type=str,
                        help="Esporta per Cytoscape nel file specificato")
    parser.add_argument("--interactive", "-i", action="store_true",
                        help="Modalità interattiva")
    parser.add_argument("--demo", "-d", action="store_true",
                        help="Esegui demo con gene EYS")

    args = parser.parse_args()

    print_header()

    # Modalità interattiva
    if args.interactive:
        interactive_mode()
        return

    # Demo
    if args.demo:
        run_eys_demo()
        return

    # Analisi gene specifico
    if args.gene:
        gene = args.gene.upper()

        # Aggrega dati
        db_data = run_aggregation(gene, args.output if args.format == "json" else None)

        # Confronto se specificati interattori letteratura
        if args.literature:
            literature_genes = [g.strip().upper() for g in args.literature.split(",")]
            run_comparison(gene, literature_genes, db_data,
                          args.output if args.format != "json" else None,
                          args.format)

        # Export Cytoscape
        if args.cytoscape:
            literature_genes = []
            if args.literature:
                literature_genes = [g.strip().upper() for g in args.literature.split(",")]
            run_cytoscape_export(gene, literature_genes, db_data, args.cytoscape)

    else:
        # Nessun argomento: modalità interattiva
        interactive_mode()


if __name__ == "__main__":
    main()
