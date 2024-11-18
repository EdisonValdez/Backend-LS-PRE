from local_secrets.cities.models import City
from local_secrets.routes.models import Route
from local_secrets.sites.models import Site
from local_secrets.travels.models import Travel
from local_secrets.travels.tests.test_setup import TestTravelSetup


class TestTravelModels(TestTravelSetup):
    def test_add_route(self):
        travel = Travel.objects.first()
        route = Route.objects.create(
            title='TestRoute',
            city=City.objects.first(),
        )
        route.stops.add(Site.objects.first())
        assert travel.stops.count() == 0
        travel.add_route(route)
        assert travel.stops.count() == 1

    def test_generate_pdf(self):
        travel = Travel.objects.first()
        assert travel.generate_pdf()
