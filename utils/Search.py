def chromaSearchPlan(query, nResults, vector_store, allowed_files=None):
    results = vector_store.similarity_search_with_relevance_scores(query, k=nResults*2)
     
    if not allowed_files:
        return vector_store.similarity_search_with_relevance_scores(query, k=nResults)

    filtered = [
        (doc, score)
        for doc, score in results
        if any(doc.metadata.get("file_basename", "").startswith(prefix) for prefix in allowed_files)
    ]

    return filtered[:nResults]