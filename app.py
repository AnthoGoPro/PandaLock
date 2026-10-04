# Anthony Brown
# PandaLock website - runs the checks from PandaLock.py and shows them on a web page.
# The password is only checked in memory. It is never stored, saved, or logged.

import random

from flask import Flask, jsonify, render_template, request

import PandaLock as pl

app = Flask(__name__)


# Run every check on the password and collect the results for the web page
def analyze(password):
    has_length = pl.check_length(password)
    has_upper = pl.check_uppercase(password)
    has_lower = pl.check_lowercase(password)
    has_number = pl.check_numbers(password)
    has_special = pl.check_special(password)
    is_common = pl.check_common(password)
    found_words = pl.find_common_words(password)

    if is_common:
        seconds = 0
    else:
        seconds = pl.estimate_crack_seconds(password, found_words)

    universe_note = ""
    years = seconds / (60 * 60 * 24 * 365)
    if years > pl.UNIVERSE_AGE_YEARS:
        times = years / pl.UNIVERSE_AGE_YEARS
        universe_note = "That's about " + pl.format_big_number(times) + " times the age of the universe!"

    return {
        "checks": [
            {"label": "At least 8 characters", "passed": has_length},
            {"label": "Uppercase letter", "passed": has_upper},
            {"label": "Lowercase letter", "passed": has_lower},
            {"label": "Number", "passed": has_number},
            {"label": "Special character", "passed": has_special},
            {"label": "Not a common password", "passed": not is_common},
            {"label": "No common words or names", "passed": len(found_words) == 0},
        ],
        "seconds": seconds,
        "rating": pl.get_rating(seconds),
        "crack_time": pl.format_time(seconds),
        "universe_note": universe_note,
        "found_words": found_words,
        "suggestions": pl.get_suggestions(password, has_length, has_upper, has_lower,
                                          has_number, has_special, is_common, found_words),
    }


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/check", methods=["POST"])
def check():
    data = request.get_json(silent=True) or {}
    password = str(data.get("password", ""))
    response = jsonify(analyze(password))
    # Tell browsers and proxies not to keep a copy of the result
    response.headers["Cache-Control"] = "no-store"
    return response


@app.route("/tip")
def tip():
    return jsonify({"tip": random.choice(pl.PANDA_TIPS)})


if __name__ == "__main__":
    # Port 5001 because macOS uses 5000 for AirPlay
    app.run(debug=True, port=5001)
