from django.db.models import Q
from fuzzywuzzy import fuzz

from ..models import Car


def search_cars(search_text):
    cars = Car.objects.filter(complate=True)

    results = []
    for car in cars:
        name_similarity = fuzz.token_sort_ratio(search_text, car.name)
        model_similarity = fuzz.token_sort_ratio(search_text, car.model)
        description_similarity = fuzz.token_sort_ratio(
            search_text, car.description)
        contact_number_similarity = fuzz.ratio(search_text, car.contact_number)
        # price_similarity = fuzz.token_sort_ratio(search_text, car.price)
        year_similarity = fuzz.token_sort_ratio(search_text, car.year)

        if (
            name_similarity >= 50 or
            model_similarity >= 50 or
            description_similarity >= 50 or
            contact_number_similarity >= 50 or
            # price_similarity >= 50 or
            year_similarity >= 90
        ):
            results.append(car)

    return results
