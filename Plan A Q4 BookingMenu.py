import pandas as pd

pd.read_csv('/Users/sylvin/PycharmProjects/FC723 Project 3/FC723-Final-Project/planAseatplan.csv')


class SeatBooking:
    def __init__(self, csv_file_path):
        """initialises the seat booking system by reading seat data from a csvfile.

        Argument:
            csv_file_path (str): The path to the csv file containing seat information.
        """
        self.csv_file_path = csv_file_path
        self.seats = pd.read_csv(csv_file_path, index_col='Seat')

    # method checks if a seat is available for booking
    def check_availability(self, seat_label):
        seat_label = seat_label.upper()
        # indexing by the 'Seat' column to be easily viewed by user
        return self.seats.at[seat_label, 'Status'] == 'Free'

    # method to enable the booking of seats
    def book_seat(self, seat_label):
        """Checks if the specified seat is free.

        Argument:
            seat_label (str): The label of the seat to check.

        Returns:
            boolean: True if the seat is free, otherwise False.
        """
        # automatically converts seat label to uppercase to avoid case sensitivity issues.
        seat_label = seat_label.upper()
        if self.check_availability(seat_label):
            self.seats.at[seat_label, 'Status'] = 'Reserved'
            self.seats.to_csv(self.csv_file_path)
            return True
        else:
            return False
    # method for inability to book on specific seats
    # checks and prevent booking if applied to (aisle - X) and (storage - S)
    def can_not_book_seat(self, seat_label):
        """Attempts to book a seat if it is available.

        Argument:
            seat_label (str): The label of the seat to book.

        Returns:
            boolean: True if the booking was successful, False if the seat was already booked.
        """
        if self.check_availability(seat_label):
            self.seats.at[seat_label, 'Statis'] = 'X' and 'S'
            return False

    # method to cancel booking and free seat if it was previously reserved
    def free_seat(self, seat_label):
        """Frees up a seat if it is currently reserved.

        Argument:
            seat_label (str): The label of the seat to free.

        Returns:
            boolean: True if the seat was successfully freed, otherwise False.
        """
        if self.seats.at[seat_label, 'Status'] == 'Reserved':
            self.seats.at[seat_label, 'Status'] = 'Free'
            self.seats.to_csv(self.csv_file_path)
            return True
        else:
            return False

    # method to show all booked seats
    def show_booking_state(self):
        # prints the current booking status of all seats in the system.
        reserved_seats = self.seats[self.seats['Status'] == 'Reserved']
        if not reserved_seats.empty:
            for seat, row in reserved_seats.iterrows():
                print(f"{seat}: {row['Status']}")
        else:
            print("No seats are currently reserved.")


# main menu tied to csv file to append changes saved to the file (if any)
def main_menu(csv_file_path):
    booking_system = SeatBooking(csv_file_path)

    # main menu options 1 - 5
    # on a loop until function is terminated
    while True:
        print("\nMenu:")
        print("1. Check availability of seat")
        print("2. Book a seat")
        print("3. Free a seat")
        print("4. Show booking state")
        print("5. Exit program")
        choice = input("Choose an option: ")

        # option 1 for checking of seat
        if choice == '1':
            # checking of individual seat by row (number) and column (letter)
            seat_label = input("Enter seat label (e.g., '1A'): ")
            # condition if seat is not booked
            if booking_system.check_availability(seat_label):
                print("The seat is available.")
            # condition if seat is booked
            else:
                print("Sorry this seat is not available.")

        # option 2 to book seat
        elif choice == '2':
            # request for user input on which seat they intend to book
            seat_label = input("Enter seat label (e.g., '1A'): ")
            # if input seat is a seat that is available for booking
            # change status from Free to Reserved
            if booking_system.book_seat(seat_label):
                print("The seat has been booked.")
            # conditional statement if the seat had already been booked
            else:
                print("Sorry this seat has already been booked.")

        # option 3 to cancel booking and free up the seat
        elif choice == '3':
            # request for user input on which seat they had booked
            seat_label = input("Enter seat label (e.g., '1A'): ")
            # if input seat is a seat that has been booked
            # change status from Reserved to Free
            if booking_system.free_seat(seat_label):
                print("The seat has been freed.")
            # conditional statement if the seat was not booked
            else:
                print("Sorry this seat is not booked.")

        # option 4 to show all current bookings
        # allows for the viewing of which seats have been booked
        elif choice == '4':
            booking_system.show_booking_state()

        # option 5 to exit program
        # option to be selected when all other options have been used to user satisfaction
        elif choice == '5':
            print("Thank you for using our program!")
            break

        # conditional statement if anything other than 1-5 is chosen
        else:
            print("Invalid option. Please try again.")




if __name__ == "__main__":
    # Entry point of the program when run as a script.
    # This sets the path to the CSV file and launches the main menu.
    csv_file_path = '/Users/sylvin/PycharmProjects/FC723 Project 3/FC723-Final-Project/planAseatplan.csv'
    main_menu(csv_file_path)
