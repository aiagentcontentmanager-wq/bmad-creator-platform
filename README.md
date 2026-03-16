# ModelOrchestrator

## Beschreibung
Der ModelOrchestrator ist ein System zur Verwaltung und Orchestrierung von Modellen. Er ermöglicht die einfache Integration, Verwaltung und Ausführung von Modellen in einer einheitlichen Umgebung.

## Installation

### Voraussetzungen
- Python 3.8 oder höher

### Abhängigkeiten installieren
```bash
pip install -r requirements.txt
```

## Verwendung

### Konfiguration
1. Bearbeiten Sie die Konfigurationsdatei `config/config.yaml`, um die Modelle und Parameter zu definieren.

### Ausführung
```bash
python -m src.model_orchestrator
```

### Tests ausführen
```bash
python -m pytest tests/
```

## Projektstruktur
```
.
├── src/
│   └── model_orchestrator.py
├── tests/
│   └── test_model_orchestrator.py
├── docs/
│   └── architecture.md
├── config/
│   └── config.yaml
├── requirements.txt
└── README.md
```

## Dokumentation
Die technische Spezifikation und Architektur finden Sie in `docs/architecture.md`.

## Lizenz
Dieses Projekt steht unter der MIT-Lizenz.