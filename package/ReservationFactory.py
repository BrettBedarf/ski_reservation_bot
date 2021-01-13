from package.providers import providers
from package.Epic import EpicReservation

# Factory creates concrete provider-specific reservation objects
class ReservationFactory:
    # TODO could use a better name
    def make_provider(self, input):
        # find provider from map of resorts to providers
        provider = next(
            (resort["provider"] for resort in providers if resort["resort"] == input.resort),
            None,
        )
        if provider == "Epic":
            return EpicReservation(input=input)
        else:
            raise Exception("Resort not available!")
