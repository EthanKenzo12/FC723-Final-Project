import pandas as pd
import random
import string
import json


# creation of a class BookingReferenceGenerator
# class will house a method to generate unique booking references
# which can be tracked using a set
class BookingReferenceGenerator:
    def __init__(self):
        # creation of a set to track the unique booking references generated
        self.generated_references = set()

    # method to generate a unique booking reference
    def generate_unique_reference(self):
        while True:
            # creation of a reference consisting of 8 random uppercase letters and digits
            reference = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            # conditional statement to ensure the reference has not already been generated prior
            if reference not in self.generated_references:
                self.generated_references.add(reference)
                return reference


class SeatBooking:
    def __init__(self, csv_file_path):
        """initialises the seat booking system by reading seat data from a csvfile.

        Argument:
            csv_file_path (str): The path to the csv file containing seat information.
        """
        # csv file path with seat information
        self.csv_file_path = csv_file_path
        # attribute to load seat data from the csv file into a DataFrame
        self.seats = pd.read_csv(csv_file_path, index_col='Seat')
        # attribute for the instance of the reference generator
        self.reference_generator = BookingReferenceGenerator()
        # attribute of dictionary to store booking details
        self.booking_details = {}

    # method saves the current state of bookings to a json file
    def save_booking_details(self):
        with open('booking_details.json', 'w') as f:
            json.dump(self.booking_details, f)

    # method loads the booking details from a json file
    def load_booking_details(self):
        # try handling in the event there is a file to load the details of saved bookings
        try:
            with open('booking_details.json', 'r') as f:
                self.booking_details = json.load(f)
        except FileNotFoundError:
            # exception handling if the file doesn't exist to initialise to an empty dict
            self.booking_details = {}

    # method checks if a seat is available for booking
    def check_availability(self, seat_label):
        seat_label = seat_label.upper()
        # indexing by the 'Seat' column to be easily viewed by user
        return self.seats.at[seat_label, 'Status'] == 'Free'

    # method to enable the booking of seats
    def book_seat(self, seat_label, customer_data):
        """Checks if the specified seat is free.

        Argument:
            seat_label (str): The label of the seat to check.
            customer data (dict): A dictionary containing customer information

        Returns:
            boolean: True if the seat is free, otherwise False.
        """
        # automatically converts seat label to uppercase to avoid case sensitivity issues.
        seat_label = seat_label.upper()
        if self.seats.at[seat_label, 'Status'] not in ('X', 'S') and self.check_availability(seat_label):
            # generation a unique booking reference
            reference = self.reference_generator.generate_unique_reference()
            # update the status from Free to Reserved
            self.seats.at[seat_label, 'Status'] = 'Reserved'
            # stores the booking detail to be retrieved if needed
            self.booking_details[seat_label] = {'reference': reference, 'customer_data': customer_data}
            # saves the updated data to csv file
            self.seats.to_csv(self.csv_file_path)
            print(f"Booking complete. Reference: {reference}")
            return True
        else:
            return False

    # method to cancel booking and free seat if it was previously reserved
    def free_seat(self, seat_label, booking_reference):
        """Frees up a seat if it is currently reserved.

        Argument:
            seat_label (str): The label of the seat to free.
            booking_reference (str): 8 character booking given to passengers on successful booking


        Returns:
            boolean: True if the seat was successfully freed, otherwise False.
        """
        # conditional statement to proceed only if the seat is currently reserved
        if self.seats.at[seat_label, 'Status'] == 'Reserved' and self.booking_details.get(seat_label, {}).get(
                'reference') == booking_reference:
            # update the status from Reserved to Free
            self.seats.at[seat_label, 'Status'] = 'Free'
            # removes the booking detail
            self.booking_details.pop(seat_label, None)  # Remove booking details
            # saves the updated data to csv file
            self.seats.to_csv(self.csv_file_path)
            # save the updated booking details to the JSON file
            self.save_booking_details()
            return True
        else:
            return False

    # method to show all booked seats
    def show_booking_state(self):
        # iterate over each item in the booking details dictionary
        for seat_label, details in self.booking_details.items():
            # retrieve the current status of the seat from the DataFrame
            status = self.seats.at[seat_label, 'Status']
            # print out the seat label, its status, and the booking reference to the console
            print(f"Seat {seat_label} is {status}. Booking reference: {details['reference']}")

    # method to check for availability of seats by rows
    def check_row_availability(self, row_number):
        # available seats denoted by and empty list, which will be appended based on available seats
        available_seats = []
        # range of columns as denoted by letters
        for col in 'ABCDEF':
            # row_numbers (1-80) and col (letters A-E)
            seat_label = f"{row_number}{col}"
            try:
                if self.check_availability(seat_label):
                    available_seats.append(seat_label)
            except KeyError:
                continue
        if available_seats:
            print(f"The following seats are available in row {row_number}: {', '.join(available_seats)}")
        else:
            print(f"No available seats in row {row_number}")


# main menu tied to csv file to append changes saved to the file (if any)
def main_menu(csv_file_path):
    booking_system = SeatBooking(csv_file_path)

    # main menu options 1 - 5
    # on a loop until function is terminated
    while True:
        print("\nMenu:")
        print("1. Check availability of seats.")
        print("2. Book a seat")
        print("3. Free a seat")
        print("4. Show booking state")
        print("5. Exit")
        choice = input("Choose an option: ")

        # sub-menu option 1 for checking of seat availability by row
        if choice == '1':
            # sub-menu choices, 1 to continue and 0 to return to main menu
            while True:
                print("\nAvailability-Menu:")
                print("1. Check availability by row number.")
                print("0. Return to main menu.")
                sub_choice = input("Choose an option: ")

                if sub_choice == '1':
                    row_number = input("Enter row number (e.g., '1'): ")
                    booking_system.check_row_availability(row_number)
                elif sub_choice == '0':
                    break
                else:
                    print("Invalid option. Please try again.")

        # sub-menu option 2 for booking of selected seat
        elif choice == '2':
            # sub-menu choices, 1 to continue and 0 to return to main menu
            while True:
                print("\nBooking-Menu:")
                print("1. Proceed to booking page.")
                print("0. Return to main menu.")
                sub_choice = input("Choose an option: ")

                # conditional statement to proceed with booking
                # while prompting for user's name and email
                if sub_choice == '1':
                    seat_label = input("Enter seat label (e.g., '1A'): ")
                    name = input("Enter your name: ")
                    email = input("Enter your email: ")
                    customer_data = {'name': name, 'email': email}
                    if booking_system.book_seat(seat_label, customer_data):
                        print("The seat has been booked.")
                    else:
                        print("Sorry! This seat has already been booked")
                elif sub_choice == '0':
                    break
                else:
                    print("Invalid option. Please try again.")

        # sub-menu option 3 for cancellation of booked seat
        elif choice == '3':
            while True:
                print("\nCancellation-Menu:")
                print("1. Continue to cancellation page.")
                print("0. Return to main menu.")
                sub_choice = input("Choose an option: ")
                # conditional statement to proceed with cancellation provided seat and booking reference input
                if sub_choice == '1':
                    seat_label = input("Enter seat label (e.g., '1A'): ")
                    booking_reference = input("Please enter your booking reference: ")
                    if booking_system.free_seat(seat_label, booking_reference):
                        print("The seat has been freed.")
                    else:
                        print("Sorry this seat cannot be freed at this time.")
                elif sub_choice == '0':
                    break
                else:
                    print("Invalid option. Please try again.")

        elif choice == '4':
            # to show all current seats that have been booked and the reference associated with it
            booking_system.show_booking_state()

        elif choice == '5':
            # exit function with a thank-you message.
            booking_system.save_booking_details()
            print("Thank you for using our system!")
            break
        else:
            print("Invalid option. Please try again.")


# csv file path
csv_file_path = '/Users/sylvin/PycharmProjects/FC723 Project 3/FC723-Final-Project/seatplanx.csv'

if __name__ == "__main__":
    # Entry point of the program when run as a script.
    # This sets the path to the CSV file and launches the main menu.
    csv_file_path = '/Users/sylvin/PycharmProjects/FC723 Project 3/FC723-Final-Project/seatplanx.csv'
    main_menu(csv_file_path)
