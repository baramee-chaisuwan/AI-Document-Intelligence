# Retrieval Evaluation

## Objective

Evaluate the semantic retrieval performance of the RAG pipeline in the AI Document Intelligence project.

The evaluation measures whether the vector search system can retrieve the correct candidate based on user queries.

---

## Dataset

- Candidates: 3 resumes
- Resume Chunks: 14 chunks

Candidate IDs:

- 109
- 110
- 111

---

## Embedding Model

SentenceTransformer 

Model:

- paraphrase-MiniLM-L3-v2 (384 dimensions)

---

## Vector Database

PostgreSQL with pgvector

Similarity Search: 

- Cosine-distance semantic search using pgvector
- Equal-weight reciprocal-rank fusion with database-backed BM25

---

## Evaluation Metrics

The retrieval performance was evaluated using:

- Top-1 Accuracy
- Top-3 Accuracy

---

## Test Queries

The evaluation dataset contains queries related to candidate skills and experience:

- Python
- Machine Learning
- FastAPI
- Docker
- ETL
- SQL Server
- LLM
- Who has ETL experience?

---

## Historical Results

The results below were recorded before the PostgreSQL/pgvector persistence
migration. Re-run the evaluation dataset before treating them as current
quality measurements.

| Metric | Score |
|---|---:|
| Top-1 Accuracy | 75.00% |
| Top-3 Accuracy | 87.50% |

---

## Failure Analysis

### Machine Learning

The expected candidate was retrieved within the Top-3 results but was not ranked first.

Candidate 109 achieved a higher similarity score because the resume contained more explicit Machine Learning related keywords:

- TensorFlow
- Naive Bayes
- Classification
- Machine Learning projects

This indicates a ranking limitation rather than a retrieval failure.

---

### LLM

The query: 

```text
LLM
```

failed to retrieve the expected candidate within the Top-3 results.

Although the candidate resume contained related concepts:

- Large Language Models
- Generative AI
- LLM Integration
- Prompt Engineering

the embedding model did not strongly associate the abbreviation "LLM" with these related terms.

This highlights a limitation of general-purpose embedding models when handling domain-specific abbreviations.

---

## Future Improvements

Potential improvements for retrieval quality:

- Cross Encoder Re-ranking
- Query Expansion
- Domain-specific Embedding Models
- Better Resume Chunking Strategy
- Metadata Filtering
