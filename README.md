# Local Open-Source LLMs as an Explainable Triage Layer for SCADA/ICS Anomaly Alerts

A practical evaluation of locally deployed open-source LLMs (served via Ollama) as an
explainable triage layer on top of classical SCADA/ICS anomaly detectors.

The framing is **"ML detects, LLM explains and triages"**: a classical detector produces an
anomaly score and label, these are summarized into a structured *incident card*, and a local
LLM classifies the card as `normal | suspicious | critical` and emits a strict-JSON,
operator-facing explanation.

## Research questions

- **RQ1** How accurately can local open-source LLMs classify structured SCADA incident cards,
  relative to classical baselines (Random Forest, Logistic Regression, Isolation Forest, rules)?
- **RQ2** Does few-shot prompting improve classification accuracy and output reliability
  (valid-JSON rate, field completeness) over zero-shot?
- **RQ3** How useful and faithful are the generated explanations for operator-facing triage?
- **RQ4** What are the latency and resource trade-offs across a 3B-14B model ladder?

## Repository layout

```
scada-llm-triage/
  notebooks/scada_llm_triage.ipynb   end-to-end pipeline (phases 1-5)
  data/                              place BATADAL CSVs here (see data/README.md)
  results/                           generated metrics, plots, raw responses
  requirements.txt
```

## Pipeline (phases 1-5 in the notebook)

1. Data loading, preprocessing, sliding-window feature aggregation, severity labeling.
2. Classical baselines: Random Forest, Logistic Regression, Isolation Forest, rule-based.
3. Incident-card generation, JSON schema, prompt templates; retrieval pool and four
   strategies: zero-shot, few-shot, retrieval-augmented few-shot, self-consistency.
4. Local LLM execution through Ollama (deterministic base, JSON-forced).
5. Evaluation: classification quality, output reliability, hallucination heuristic,
   explanation annotation export, latency and token cost.

## Setup

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Pull the models you want to evaluate, e.g.:

```
ollama pull qwen2.5:14b
ollama pull mistral-nemo:12b
ollama pull gemma3:12b
ollama pull qwen2.5:7b
ollama pull llama3.2:3b
ollama pull nomic-embed-text
```

The embedding model powers the retrieval-augmented few-shot strategy; if it is not pulled, the retriever
falls back to a TF-IDF baseline automatically.

Then open `notebooks/scada_llm_triage.ipynb` and run top to bottom. If no dataset is present,
the notebook runs on a clearly-flagged synthetic BATADAL-like sample so you can validate the
pipeline before downloading real data.
