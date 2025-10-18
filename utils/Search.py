def chromaSearchPlan(query, nResults, vector_store):
    results = []
    results = vector_store.similarity_search_with_relevance_scores(query, nResults)
    return results