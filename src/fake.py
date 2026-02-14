from faker import Faker
from faker.providers import company, file, internet, person, job
from faker_music import MusicProvider
from faker_vehicle import VehicleProvider

fake: Faker | None = None

def get_fake() -> Faker:
    global fake
    
    if fake is None:
        fake = Faker("en_US")
        fake.add_provider(company)
        fake.add_provider(file)
        fake.add_provider(internet)
        fake.add_provider(person)
        fake.add_provider(job)
        fake.add_provider(MusicProvider)
        fake.add_provider(VehicleProvider)

    return fake