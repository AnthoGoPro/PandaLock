# Anthony Brown
# PandaLock - password strength checker
# The password is only checked in memory. It is never stored or saved.

import random

# About how many guesses per second one high-end gaming GPU (like an RTX 4090)
# can make against a password stored with a fast hash like MD5.
# Sites that use slow hashes like bcrypt are much harder to crack than this.
GUESSES_PER_SECOND = 100000000000

# How many guesses a dictionary attack needs to cover one common word,
# including variations like Dragon, DRAGON, and Dr@g0n
DICTIONARY_GUESSES = 1000000

# Age of the universe in years, for comparison
UNIVERSE_AGE_YEARS = 13800000000

# Full passwords that show up in breach dumps all the time
COMMON_PASSWORDS = [
    "password", "password1", "password123", "123456", "12345678",
    "123456789", "1234567890", "qwerty", "qwerty123", "abc123",
    "111111", "iloveyou", "admin", "welcome", "letmein",
    "monkey", "dragon", "football", "baseball", "sunshine",
    "princess", "master", "shadow", "trustno1", "passw0rd",
]

# Words, names, and patterns that show up over and over inside hacked passwords.
# If any of these appear anywhere in a password, attackers will find it fast.
COMMON_WORDS = [
    # Words
    "password", "qwerty", "asdf", "zxcv", "letmein", "welcome", "admin",
    "login", "iloveyou", "love", "hello", "secret", "freedom", "whatever",
    "monkey", "dragon", "master", "shadow", "sunshine", "princess",
    "superman", "batman", "starwars", "pokemon", "killer", "cookie",
    "summer", "winter", "flower", "football", "baseball", "soccer",
    "hockey", "hunter", "tigger", "buster", "ginger", "pepper", "maggie",
    # Names
    "michael", "jessica", "ashley", "jordan", "daniel", "thomas", "robert",
    "charlie", "jennifer", "matthew", "andrew", "joshua", "amanda", "nicole",
    # Number patterns
    "1234", "1111", "0000", "abc123",
]

# Educational tips the panda can share
PANDA_TIPS = [
    "Dictionary words are risky. Crackers try every word in the dictionary first.",
    "Swapping letters for symbols (like @ for a) is a trick crackers already know.",
    "A long passphrase like 'purple-taco-rocket-lamp' beats a short messy password.",
    "Never reuse a password. One breach can unlock all your accounts.",
    "A password manager can create and remember strong passwords for you.",
    "Turn on two-factor authentication. It stops attackers even if they get your password.",
    "Avoid personal info like birthdays, pet names, or your favorite team.",
]


# Get the password from the user
def get_password():
    password = input("Enter a password to check:\n")
    return password


# Check if the password is at least 8 characters
def check_length(password):
    if len(password) >= 8:
        return True
    else:
        return False


# Check if the password has at least one uppercase letter
def check_uppercase(password):
    for i in range(len(password)):
        if password[i].isupper():
            return True
    return False


# Check if the password has at least one lowercase letter
def check_lowercase(password):
    for i in range(len(password)):
        if password[i].islower():
            return True
    return False


# Check if the password has at least one number
def check_numbers(password):
    for i in range(len(password)):
        if password[i].isdigit():
            return True
    return False


# Check if the password has at least one special character (not a letter or number)
def check_special(password):
    for i in range(len(password)):
        if not password[i].isalnum():
            return True
    return False


# Check if the whole password is on the common password list
def check_common(password):
    for i in range(len(COMMON_PASSWORDS)):
        if password.lower() == COMMON_PASSWORDS[i]:
            return True
    return False


# Undo common symbol swaps so "p@ssw0rd" reads as "password"
def undo_symbol_swaps(password):
    swap_from = "@4310$5!7"
    swap_to = "aaeiossit"
    result = ""
    for i in range(len(password)):
        char = password[i].lower()
        new_char = char
        for j in range(len(swap_from)):
            if char == swap_from[j]:
                new_char = swap_to[j]
        result = result + new_char
    return result


# Find every common word hiding inside the password
def find_common_words(password):
    plain = password.lower()
    unswapped = undo_symbol_swaps(password)
    found = []
    for i in range(len(COMMON_WORDS)):
        word = COMMON_WORDS[i]
        # "in" checks if one string appears anywhere inside another
        if word in plain or word in unswapped:
            found.append(word)
    return found


# Count how many possible characters an attacker has to try for each spot
def count_character_pool(password):
    pool = 0
    if check_lowercase(password):
        pool = pool + 26
    if check_uppercase(password):
        pool = pool + 26
    if check_numbers(password):
        pool = pool + 10
    if check_special(password):
        pool = pool + 32
    return pool


# Estimate the average time to crack the password, in seconds
def estimate_crack_seconds(password, found_words):
    pool = count_character_pool(password)

    if len(found_words) == 0:
        # Brute force: try every possible combination of characters
        combinations = pool ** len(password)
    else:
        # Dictionary attack: guess each common word from a list,
        # then brute force only the characters around them
        word_letters = 0
        for i in range(len(found_words)):
            word_letters = word_letters + len(found_words[i])
        leftover = len(password) - word_letters
        if leftover < 0:
            leftover = 0
        combinations = DICTIONARY_GUESSES ** len(found_words) * pool ** leftover

    # Really long passwords make numbers too big for Python to divide,
    # so cap it. At this size it's uncrackable anyway.
    if combinations > 10 ** 300:
        combinations = 10 ** 300

    # On average an attacker finds it halfway through all the combinations
    return combinations / 2 / GUESSES_PER_SECOND


# Turn a big number into words, like 4900000 -> "4.9 million"
def format_big_number(number):
    if number < 1000:
        return "%.1f" % number
    elif number < 1000000:
        return "%.1f thousand" % (number / 1000)
    elif number < 1000000000:
        return "%.1f million" % (number / 1000000)
    elif number < 1000000000000:
        return "%.1f billion" % (number / 1000000000)
    elif number < 1000000000000000:
        return "%.1f trillion" % (number / 1000000000000)
    elif number < 1000000000000000000:
        return "%.1f quadrillion" % (number / 1000000000000000)
    elif number < 1000000000000000000000:
        return "%.1f quintillion" % (number / 1000000000000000000)
    else:
        return "%.1e" % number


# Turn a number of seconds into a real, readable stat
def format_time(seconds):
    minute = 60
    hour = minute * 60
    day = hour * 24
    year = day * 365
    years = seconds / year

    if seconds < 1:
        return "less than a second"
    elif seconds < minute:
        return "%.1f seconds" % seconds
    elif seconds < hour:
        return "%.1f minutes" % (seconds / minute)
    elif seconds < day:
        return "%.1f hours" % (seconds / hour)
    elif seconds < year:
        return "%.1f days" % (seconds / day)
    else:
        return format_big_number(years) + " years"


# Turn the crack time into a strength label
def get_rating(seconds):
    day = 60 * 60 * 24
    year = day * 365
    if seconds < day:
        return "Easily Hackable"
    elif seconds < year * 1000:
        return "Hackable"
    else:
        return "Non-Hackable"


# Build a list of suggestions based on whichever checks failed
# (The terminal version prints them, and the website shows them on the page)
def get_suggestions(password, has_length, has_upper, has_lower, has_number, has_special, is_common, found_words):
    suggestions = []
    if is_common:
        suggestions.append("This exact password is on breach lists. Pick something totally new.")
    for i in range(len(found_words)):
        word = found_words[i]
        tip = "We spotted '" + word + "' in your password. It's one of the most common words in hacked passwords, so attackers try it first."
        if word not in password.lower():
            tip = tip + " Swapping letters for symbols doesn't hide it. Crackers check that too."
        suggestions.append(tip)
    if not has_length:
        suggestions.append("Make it at least 8 characters. Longer is much stronger.")
    if not has_upper:
        suggestions.append("Add an uppercase letter (A-Z).")
    if not has_lower:
        suggestions.append("Add a lowercase letter (a-z).")
    if not has_number:
        suggestions.append("Add a number (0-9).")
    if not has_special:
        suggestions.append("Add a special character like ! @ # $ %.")

    all_passed = has_length and has_upper and has_lower and has_number and has_special
    if all_passed and not is_common and len(found_words) == 0:
        suggestions.append("Nothing to fix. Nice work!")
    return suggestions


# Show a pass or fail line for one check
def show_check(label, result):
    if result:
        print("  [PASS]", label)
    else:
        print("  [FAIL]", label)


def main():
    print("=" * 60)
    print("  PandaLock - Password Strength Checker")
    print("  Your password is checked in memory and never saved.")
    print("=" * 60)

    password = get_password()

    has_length = check_length(password)
    has_upper = check_uppercase(password)
    has_lower = check_lowercase(password)
    has_number = check_numbers(password)
    has_special = check_special(password)
    is_common = check_common(password)
    found_words = find_common_words(password)

    print("\nResults:")
    show_check("At least 8 characters", has_length)
    show_check("Uppercase letter", has_upper)
    show_check("Lowercase letter", has_lower)
    show_check("Number", has_number)
    show_check("Special character", has_special)
    show_check("Not a common password", not is_common)
    show_check("No common words or names", len(found_words) == 0)

    if is_common:
        seconds = 0
    else:
        seconds = estimate_crack_seconds(password, found_words)

    print("\nStrength:", get_rating(seconds))
    print("Average time to crack:", format_time(seconds))
    print("  (Based on one high-end GPU making about 100 billion guesses per second)")
    if seconds / (60 * 60 * 24 * 365) > UNIVERSE_AGE_YEARS:
        times = seconds / (60 * 60 * 24 * 365) / UNIVERSE_AGE_YEARS
        print("  That's about " + format_big_number(times) + " times the age of the universe!")

    suggestions = get_suggestions(password, has_length, has_upper, has_lower, has_number, has_special, is_common, found_words)
    print("\nPanda's suggestions:")
    for i in range(len(suggestions)):
        print("  -", suggestions[i])

    print("\n  (o_o)  Panda tip:")
    print("  /[__]\\ ", random.choice(PANDA_TIPS))


# Only run the terminal version when this file is run directly.
# This lets the website (app.py) borrow the functions without starting main().
if __name__ == "__main__":
    main()
