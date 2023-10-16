from django.db.models import Q
from fuzzywuzzy import fuzz

from ..models import Car


def search_cars(query):
    search_terms = query.split()

    # Build query for partial matching on 'name' and 'model'
    name_query = Q()
    model_query = Q()
    for term in search_terms:
        name_query |= Q(name__icontains=term)
        model_query |= Q(model__icontains=term)

    # Combine the name and model queries
    name_or_model_query = name_query | model_query

    # Perform the search query
    results = Car.objects.filter(name_or_model_query)

    # Calculate fuzzy matching score for each result
    fuzzy_scores = []
    for result in results:
        name_score = max(fuzz.partial_ratio(term, result.name.lower())
                         for term in search_terms)
        model_score = max(fuzz.partial_ratio(term, result.model.lower())
                          for term in search_terms)
        fuzzy_scores.append((result, max(name_score, model_score)))

    # Sort the results by fuzzy matching score (most relevant first)
    fuzzy_scores.sort(key=lambda x: x[1], reverse=True)
    results = [result for result, _ in fuzzy_scores]

    return results
