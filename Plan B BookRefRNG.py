import random
import string

# creation of a class BookingSystem
# class will house methods:
# to generate unique_references, book_seat and free_seat
class BookingSystem:
    def __init__(self):
        # use of a set to track each unique reference
        self.booking_references = set()
        # use of a dictionary to store customer information associated with a booking reference
        self.customer_data = {}
        # use a dictionary to track the reservation status of seats
        self.seat_status = {}

    # method to generate a unique booking reference
    def generate_unique_reference(self):
        while True:
            # creation of a reference consisting of 8 random uppercase letters and digits
            reference = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            # conditional statement to ensure the reference has not already been generated prior
            if reference not in self.booking_references:
                self.booking_references.add(reference)
                return reference

    # method to enable the booking of seats
    def book_seat(self, seat_label, customer_info):
        # conditional statement to proceed only if the seat is free
        if seat_label not in self.seat_status or self.seat_status[seat_label] == 'Free':
            # generation a unique booking reference
            reference = self.generate_unique_reference()
            # update the seat status to the new booking reference
            self.seat_status[seat_label] = reference
            # store customer data under the generated reference.
            self.customer_data[reference] = customer_info
            return reference
        return None

    # method to cancel booking and free seat if it was previously reserved
    def free_seat(self, seat_label):
        # conditional statement to proceed only if the seat is currently reserved
        if seat_label in self.seat_status and self.seat_status[seat_label] != 'Free':
            # utilising reference stored in prior booking
            reference = self.seat_status[seat_label]
            # update the status of the seat from to Free
            self.seat_status[seat_label] = 'Free'
            # remove customer data associated with the booking reference
            del self.customer_data[reference]
            return True
        return False

# example usage to be viewed
booking_system = BookingSystem()

# customer booking a seat
seat_booked = booking_system.book_seat('1A', {'name': 'John Doe', 'email': 'johndoe@example.com'})
print(f"Seat booked with reference: {seat_booked}")

# condition to free a seat
if booking_system.free_seat('1A'):
    print("Seat has been freed and customer data removed.")
