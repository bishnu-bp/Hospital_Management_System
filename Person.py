class Person:
    """A class representing a generic person."""
    
    def __init__(self, first_name, surname, username, password):
    # def __init__(self, first_name, surname):
        """
        Args:
            first_name (string): First name
            surname (string): Surname
        """
        self._first_name = first_name
        self._surname = surname
        self.__username = username
        self.__password = password

    @staticmethod
    def login(person):
        """A login."""
        print("-----Login-----")
        username = input('Enter the username: ')
        password = input('Enter the password: ')
        return person.get_username() == username and person.get_password() == password

    def get_username(self):
        return self.__username

    def set_username(self, new_username):
        self.__username  = new_username

    def get_password(self):
        return self.__password

    def set_password(self, new_password):
        self.__password  = new_password

    def get_first_name(self):
        """Returns the first name of the person."""
        return self._first_name

    def set_first_name(self, new_first_name):
        """Sets the first name of the person."""
        self._first_name = new_first_name

    def get_surname(self):
        """Returns the surname of the person."""
        return self._surname

    def set_surname(self, new_surname):
        """Sets the surname of the person."""
        self._surname = new_surname

    def full_name(self):
        """Returns the full name of the person."""
        return f"{self._first_name} {self._surname}"

    def __str__(self):
        """Returns a string representation of the person."""
        return self.full_name()