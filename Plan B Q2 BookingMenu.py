import pandas as pd
import random
import string
import sqlite3
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
    def __init__(self, csv_file_path, db_path):
        """Initialises the seat booking system by reading seat data from a csvfile.

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
        self.db_path = db_path
        # attribute to link to sqlite database
        self.conn = sqlite3.connect(db_path)
        # attribute to initialise database
        self.init_db()
        # attribute to load booking details from JSON file if it exists
        self.load_booking_details()

    # creation of method to initialise database and create table to store passnger information
    def init_db(self):
        # creation of a new SQLite table for bookings if it does not exist
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bookings (
                seat_label TEXT PRIMARY KEY,
                reference TEXT,
                first_name TEXT,
                last_name TEXT,
                passport_number TEXT,
                email TEXT,
                status TEXT
            )
        ''')
        self.conn.commit()

    # method saves the current state of bookings to a json file
    def save_booking_details(self):
        # save booking to json file for later retrival
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
        """Check if the given seat is available for booking."""
        seat_label = seat_label.upper()
        cursor = self.conn.cursor()
        cursor.execute('SELECT status FROM bookings WHERE seat_label=?', (seat_label,))
        result = cursor.fetchone()
        # conditional statement if seat is not in bookings table, check the status in the DataFrame.
        if result is None:
            # If there is no entry in the bookings table, check the CSV file status
            return self.seats.at[seat_label, 'Status'] == 'Free'
        return result[0] == 'Free'

    # method to enable the booking of seats
    def book_seat(self, seat_label, customer_data):
        """Attempt to book a seat for a customer if it is available.

        Argument:
            seat_label (str): The label of the seat to check.
            customer data (dict): A dictionary containing customer information

        Returns:
            boolean: True if the seat is free, otherwise False.
        """
        # automatically converts seat label to uppercase to avoid case sensitivity issues.
        seat_label = seat_label.upper()

        # Check if the seat exists in the DataFrame before proceeding
        if seat_label not in self.seats.index:
            print(f"Error: Seat '{seat_label}' does not exist.")
            return False

        cursor = self.conn.cursor()
        cursor.execute('SELECT status FROM bookings WHERE seat_label=?', (seat_label,))
        result = cursor.fetchone()
        # Check if the seat is already booked
        if result is not None:
            print(f"Seat {seat_label} is already booked.")
            return False

        if self.seats.at[seat_label, 'Status'] not in ('X', 'S') and self.check_availability(seat_label):
            reference = self.reference_generator.generate_unique_reference()
            self.seats.at[seat_label, 'Status'] = 'Reserved'

            try:
                cursor.execute('''
                    INSERT INTO bookings (seat_label, reference, first_name, last_name, passport_number, email, status)
                    VALUES (?, ?, ?, ?, ?, ?, 'Reserved')
                ''', (seat_label, reference, customer_data['first_name'], customer_data['last_name'],
                      customer_data['passport_number'], customer_data['email']))
                self.conn.commit()
                print(f"Booking complete. Reference: {reference}")
                return True
            except sqlite3.IntegrityError as e:
                print(f"A booking for seat {seat_label} already exists.")
                return False
        else:
            print(f"Seat {seat_label} cannot be booked.")
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
        seat_label = seat_label.upper()
        cursor = self.conn.cursor()
        cursor.execute('SELECT reference FROM bookings WHERE seat_label=?', (seat_label,))
        result = cursor.fetchone()
        if result and result[0] == booking_reference:
            # if there is a matche, delete the record from the database
            cursor.execute("DELETE FROM bookings WHERE seat_label=?", (seat_label,))
            self.conn.commit()
            self.seats.at[seat_label, 'Status'] = 'Free'
            self.seats.to_csv(self.csv_file_path)
            print(f"Removing seat {seat_label} with Ref: {booking_reference} from the database.")
            return True
        else:
            print(f"No matching booking reference found for seat {seat_label}, or the seat was not reserved.")
            return False

    # method to show all booked seats
    def show_booking_state(self):
        cursor = self.conn.cursor()
        # Select only seats that are reserved and have a valid reference
        cursor.execute(
            'SELECT seat_label, status, reference FROM bookings WHERE status <> "Free" AND reference IS NOT NULL')
        results = cursor.fetchall()
        if results:
            for row in results:
                print(f"Seat {row[0]} is {row[1]}. Booking reference: {row[2]}")
        else:
            print("No booked seats.")

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
    # data from use input to be saved into database
    db_path = 'Booking_Information.db'
    booking_system = SeatBooking(csv_file_path, db_path)
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
                    first_name = input("Enter your first name: ")
                    last_name = input("Enter your last name: ")
                    passport_number = input("Enter your passport number: ")
                    email = input("Enter your email: ")
                    customer_data = {'first_name': first_name, 'last_name': last_name,
                                     'passport_number': passport_number,
                                     'email': email}
                    booking_system.book_seat(seat_label, customer_data)

                # return to main menu
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
                    booking_reference = input("Enter your booking reference: "
                                              "(Your booking reference is case-sensitive) ")
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