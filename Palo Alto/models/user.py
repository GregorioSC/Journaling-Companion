# models/user.py


class User:
    def __init__(
        self,
        id,
        username,
        email,
        password,
        age,
        gender,
        last_entry_date=None,  # "YYYY-MM-DD" or None
        current_streak=0,
        longest_streak=0,
    ):
        self._id = id
        self._username = username
        self._email = email
        self._password = password
        self._age = age
        self._gender = gender
        self._last_entry_date = last_entry_date
        self._current_streak = current_streak
        self._longest_streak = longest_streak

    # --- id ---
    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value

    # --- username ---
    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, value):
        self._username = value

    # --- email ---
    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, value):
        self._email = value

    # --- password (store hash in production) ---
    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        self._password = value

    # --- age ---
    @property
    def age(self):
        return self._age

    @age.setter
    def age(self, value):
        self._age = value

    # --- gender ---
    @property
    def gender(self):
        return self._gender

    @gender.setter
    def gender(self, value):
        self._gender = value

    # --- last_entry_date ---
    @property
    def last_entry_date(self):
        return self._last_entry_date

    @last_entry_date.setter
    def last_entry_date(self, value):
        self._last_entry_date = value

    # --- current_streak ---
    @property
    def current_streak(self):
        return self._current_streak

    @current_streak.setter
    def current_streak(self, value):
        self._current_streak = value

    # --- longest_streak ---
    @property
    def longest_streak(self):
        return self._longest_streak

    @longest_streak.setter
    def longest_streak(self, value):
        self._longest_streak = value
