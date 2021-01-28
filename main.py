from package.reservation_factory import ReservationFactory
import config.reservation_input as input


def main():

    res_factory = ReservationFactory()
    res = res_factory.make_reservation(input)
    res.process()

    input("Any key to exit...")


if __name__ == "__main__":
    main()
