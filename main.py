from package.epic import EpicReservation


def main():
    # TODO: refactor routing logic to another namespace allowing for multiple reservation systems

    # *** EPIC *** #

    EpicReservation()

    input("Any key to exit...")


if __name__ == "__main__":
    main()
