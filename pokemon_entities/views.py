import folium

from django.shortcuts import get_object_or_404, render
from django.utils.timezone import localtime

from pokemon_entities.models import Pokemon, PokemonEntity


MOSCOW_CENTER = [55.751244, 37.618423]
DEFAULT_IMAGE_URL = (
    'https://vignette.wikia.nocookie.net/pokemon/images/6/6e/%21.png/revision'
    '/latest/fixed-aspect-ratio-down/width/240/height/240?cb=20130525215832'
    '&fill=transparent'
)


def add_pokemon(folium_map, lat, lon, image_url=DEFAULT_IMAGE_URL):
    icon = folium.features.CustomIcon(
        image_url,
        icon_size=(50, 50),
    )
    folium.Marker(
        [lat, lon],
        icon=icon,
    ).add_to(folium_map)


def show_all_pokemons(request):
    folium_map = folium.Map(location=MOSCOW_CENTER, zoom_start=12)

    current_time = localtime()

    active_pokemon_entities = PokemonEntity.objects.filter(
        appeared_at__lte=current_time,
        disappeared_at__gt=current_time,
    )

    for pokemon_entity in active_pokemon_entities:
        if pokemon_entity.pokemon.image:
            image_url = request.build_absolute_uri(
                pokemon_entity.pokemon.image.url
            )
        else:
            image_url = DEFAULT_IMAGE_URL

        add_pokemon(
            folium_map,
            pokemon_entity.latitude,
            pokemon_entity.longitude,
            image_url,
        )

    pokemons_on_page = []

    for pokemon in Pokemon.objects.all():
        if pokemon.image:
            image_url = request.build_absolute_uri(pokemon.image.url)
        else:
            image_url = DEFAULT_IMAGE_URL

        pokemons_on_page.append({
            'pokemon_id': pokemon.id,
            'img_url': image_url,
            'title_ru': pokemon.title,
        })

    return render(request, 'mainpage.html', context={
        'map': folium_map._repr_html_(),
        'pokemons': pokemons_on_page,
    })


def show_pokemon(request, pokemon_id):
    requested_pokemon = get_object_or_404(
        Pokemon,
        id=pokemon_id,
    )

    if requested_pokemon.image:
        image_url = request.build_absolute_uri(
            requested_pokemon.image.url
        )
    else:
        image_url = DEFAULT_IMAGE_URL

    previous_evolution = None

    if requested_pokemon.previous_evolution:
        previous_pokemon = requested_pokemon.previous_evolution

        if previous_pokemon.image:
            previous_image_url = request.build_absolute_uri(
                previous_pokemon.image.url
            )
        else:
            previous_image_url = DEFAULT_IMAGE_URL

        previous_evolution = {
            'pokemon_id': previous_pokemon.id,
            'title_ru': previous_pokemon.title,
            'img_url': previous_image_url,
        }

    next_evolution = None

    next_evolutions = requested_pokemon.next_evolutions.all()

    if next_evolutions.exists():
        next_pokemon = next_evolutions.first()

        if next_pokemon.image:
            next_image_url = request.build_absolute_uri(
                next_pokemon.image.url
            )
        else:
            next_image_url = DEFAULT_IMAGE_URL

        next_evolution = {
            'pokemon_id': next_pokemon.id,
            'title_ru': next_pokemon.title,
            'img_url': next_image_url,
        }

    current_time = localtime()

    pokemon_entities = requested_pokemon.entities.filter(
        appeared_at__lte=current_time,
        disappeared_at__gt=current_time,
    )

    folium_map = folium.Map(location=MOSCOW_CENTER, zoom_start=12)

    for pokemon_entity in pokemon_entities:
        add_pokemon(
            folium_map,
            pokemon_entity.latitude,
            pokemon_entity.longitude,
            image_url,
        )

    pokemon = {
        'pokemon_id': requested_pokemon.id,
        'title': requested_pokemon.title,
        'title_ru': requested_pokemon.title,
        'title_en': requested_pokemon.title_en,
        'title_jp': requested_pokemon.title_jp,
        'description': requested_pokemon.description,
        'img_url': image_url,
        'previous_evolution': previous_evolution,
        'next_evolution': next_evolution,
    }

    return render(request, 'pokemon.html', context={
        'map': folium_map._repr_html_(),
        'pokemon': pokemon,
    })