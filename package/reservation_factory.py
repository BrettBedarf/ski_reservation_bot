from package.providers import providers
from package.epic import EpicReservation

# Factory creates concrete provider-specific reservation objects
class ReservationFactory:
    # TODO could use a better name
    def make_reservation(self, input_data):
        # find provider from map of resorts to providers
        provider = next(
            (
                resort["provider"]
                for resort in providers
                if resort["resort"] == input_data["resort"]
            ),
            None,
        )
        if provider == "Epic":
            return EpicReservation(input_data)
        else:
            raise Exception("Resort not available!")
