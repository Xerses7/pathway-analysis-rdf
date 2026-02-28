"""
Configurazione endpoint SPARQL e parametri applicazione
"""

# SPARQL Endpoints
ENDPOINTS = {
    "uniprot": {
        "url": "https://sparql.uniprot.org/sparql",
        "name": "UniProt",
        "description": "Database proteico principale",
        "timeout": 60
    },
    "wikipathways": {
        "url": "https://sparql.wikipathways.org/sparql",
        "name": "WikiPathways",
        "description": "Database pathway biologici",
        "timeout": 60
    },
    "string": {
        "url": "https://string-db.org/api",
        "name": "STRING",
        "description": "Interazioni proteina-proteina",
        "timeout": 30
    }
}

# Parametri di default
DEFAULT_ORGANISM = "9606"  # Homo sapiens
DEFAULT_CONFIDENCE = 0.7   # Score minimo STRING
DEFAULT_LIMIT = 100        # Limite risultati query

# Colori per output console
COLORS = {
    "header": "\033[95m",
    "blue": "\033[94m",
    "cyan": "\033[96m",
    "green": "\033[92m",
    "yellow": "\033[93m",
    "red": "\033[91m",
    "end": "\033[0m",
    "bold": "\033[1m"
}
