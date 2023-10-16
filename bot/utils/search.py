from django.db.models import Q
from fuzzywuzzy import fuzz

from ..models import Car


def search_cars(query):
    search_terms = query.split()

    # Build query for partial matching on 'name', 'model', 'year', 'price', and 'description'
    name_query = Q()
    model_query = Q()
    year_query = Q()
    price_query = Q()
    description_query = Q()

    for term in search_terms:
        name_query |= Q(name__icontains=term)
        model_query |= Q(model__icontains=term)
        year_query |= Q(year__icontains=term)
        price_query |= Q(price__icontains=term)
        description_query |= Q(description__icontains=term)

    # Combine the queries for all fields
    all_fields_query = name_query | model_query | year_query | price_query | description_query

    # Perform the search query
    results = Car.objects.filter(all_fields_query)

    # Calculate fuzzy matching score for each result
    fuzzy_scores = []
    for result in results:
        name_score = max(fuzz.partial_ratio(term, result.name.lower())
                         for term in search_terms)
        model_score = max(fuzz.partial_ratio(term, result.model.lower())
                          for term in search_terms)
        year_score = max(fuzz.partial_ratio(term, str(result.year))
                         for term in search_terms)
        price_score = max(fuzz.partial_ratio(term, str(result.price))
                          for term in search_terms)
        description_score = max(fuzz.partial_ratio(
            term, result.description.lower()) for term in search_terms)

        # Calculate fuzzy matching score for search terms
        search_terms_score = max(fuzz.partial_ratio(
            term, result.name.lower()) for term in search_terms)

        fuzzy_scores.append((result, max(name_score, model_score, year_score,
                            price_score, description_score, search_terms_score)))

    # Sort the results by fuzzy matching score (most relevant first)
    fuzzy_scores.sort(key=lambda x: x[1], reverse=True)
    results = [result for result, _ in fuzzy_scores]

    return results
