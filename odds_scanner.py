import requests
import time
import sqlite3
import os

from datetime import (
    datetime,
    timezone
)

BOT_TOKEN = "8925919932:AAE_CN7NRn9JCbtknc9RqwXdzc9xqfGpG6g"

CHAT_ID = "@sokeoscanner"

API_KEY = "4e33248024942ca4651ab2f6d806c05d"

LEAGUES = [

    "soccer_epl",

    "soccer_spain_la_liga",

    "soccer_germany_bundesliga",

    "soccer_italy_serie_a",

    "soccer_france_ligue_one",

    "soccer_uefa_champs_league"

]

ASIAN_BOOKMAKERS = [

    "Pinnacle",

    "Betfair",

    "Matchbook",

    "Marathon Bet",

    "1xBet"

]

previous_odds = {}

last_sent = {}

conn = sqlite3.connect(
    "scanner.db"
)

cursor = conn.cursor()

cursor.execute("""

CREATE TABLE IF NOT EXISTS odds_history (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    league TEXT,

    home_team TEXT,

    away_team TEXT,

    bookmaker TEXT,

    odds REAL,

    point REAL,

    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP

)

""")

conn.commit()


def send_telegram(message):

    url = (
        f"https://api.telegram.org/bot"
        f"{BOT_TOKEN}/sendMessage"
    )

    payload = {

        "chat_id": CHAT_ID,

        "text": message

    }

    try:

        requests.post(
            url,
            data=payload,
            timeout=15
        )

    except Exception as e:

        print(e)


while True:

    try:

        print(
            "\n✅ SOCCER MONITOR RUNNING...\n"
        )

        for league in LEAGUES:

            print(
                f"📡 Scanning {league}"
            )

            url = (

                f"https://api.the-odds-api.com/v4/sports/"
                f"{league}/odds/?apiKey={API_KEY}"
                f"&regions=eu"
                f"&markets=spreads,totals"

            )

            response = requests.get(
                url,
                timeout=20
            )

            if response.status_code != 200:

                print(
                    "❌ API Error"
                )

                print(
                    response.text
                )

                continue

            data = response.json()

            for match in data:

                home_team = (
                    match["home_team"]
                )

                away_team = (
                    match["away_team"]
                )

                commence_time = (
                    match["commence_time"]
                )

                match_time = (
                    datetime.fromisoformat(
                        commence_time.replace(
                            "Z",
                            "+00:00"
                        )
                    )
                )

                now = datetime.now(
                    timezone.utc
                )

                hours_until_match = (

                    (
                        match_time - now
                    ).total_seconds() / 3600

                )

                if hours_until_match > 4:
                    continue

                for bookmaker in (
                    match["bookmakers"]
                ):

                    if (

                        bookmaker["title"]
                        not in ASIAN_BOOKMAKERS

                    ):

                        continue

                    for market in (
                        bookmaker["markets"]
                    ):

                        for outcome in (
                            market["outcomes"]
                        ):

                            name = (
                                outcome["name"]
                            )

                            price = (
                                outcome["price"]
                            )

                            point = (
                                outcome.get(
                                    "point",
                                    0
                                )
                            )

                            cursor.execute("""

                            INSERT INTO odds_history (

                                league,
                                home_team,
                                away_team,
                                bookmaker,
                                odds,
                                point

                            )

                            VALUES (?, ?, ?, ?, ?, ?)

                            """, (

                                league,
                                home_team,
                                away_team,
                                bookmaker["title"],
                                price,
                                point

                            ))

                            conn.commit()

                            odds_key = (

                                f"{league}-"
                                f"{home_team}-"
                                f"{away_team}-"
                                f"{name}"

                            )

                            if (
                                odds_key
                                in previous_odds
                            ):

                                old_price = (

                                    previous_odds[
                                        odds_key
                                    ]["price"]

                                )

                                old_point = (

                                    previous_odds[
                                        odds_key
                                    ]["point"]

                                )

                                line_move = (
                                    point - old_point
                                )

                                if (

                                    abs(
                                        price - old_price
                                    ) >= 0.15

                                    or

                                    abs(
                                        line_move
                                    ) >= 0.25

                                ):

                                    now_ts = (
                                        time.time()
                                    )

                                    if (
                                        odds_key
                                        in last_sent
                                    ):

                                        if (

                                            now_ts
                                            -
                                            last_sent[
                                                odds_key
                                            ]

                                            < 300

                                        ):

                                            continue

                                    last_sent[
                                        odds_key
                                    ] = now_ts

                                    direction = "🔵"

                                    if (
                                        price
                                        <
                                        old_price
                                    ):

                                        direction = "🔴"

                                    match_display_time = (

                                        match_time.strftime(
                                            "%d/%m %H:%M UTC"
                                        )

                                    )

                                    signal = (
                                        "VALUE UP"
                                    )

                                    if (
                                        price
                                        <
                                        old_price
                                    ):

                                        signal = (
                                            "ODDS CHANGE"
                                        )

                                    tele_message = f"""

🔥 SOCCER ALERT

🏆 {league}

⚽ {home_team} vs {away_team}

🕒 {match_display_time}

────────────────────

🎯 {name}

LINE:
{point}

ODDS:
{old_price} → {price}

MOVE:
{line_move:+}

SIGNAL:
{signal}

📚 {bookmaker['title']}

"""

                                    print(
                                        tele_message
                                    )

                                    send_telegram(
                                        tele_message
                                    )

                            previous_odds[
                                odds_key
                            ] = {

                                "price":
                                    price,

                                "point":
                                    point

                            }

        print(
            "\n⏳ Waiting 60 seconds...\n"
        )

        time.sleep(60)

    except Exception as e:

        print(
            "\n❌ SCANNER ERROR:"
        )

        print(e)

        time.sleep(10)