import requests

API_KEY = "4e33248024942ca4651ab2f6d806c05d"

url = (

    f"https://api.the-odds-api.com/v4/sports/"
    f"soccer_epl/odds/?apiKey={API_KEY}"
    f"&regions=eu"
    f"&markets=spreads,totals"

)

print("\n📡 TESTING EPL API...\n")

try:

    response = requests.get(

        url,

        timeout=20

    )

    print(
        "STATUS:",
        response.status_code
    )

    data = response.json()

    if isinstance(data, list):

        print(
            f"\n✅ TOTAL MATCHES: {len(data)}\n"
        )

        for match in data[:5]:

            print(
                "================================="
            )

            print(
                f"⚽ {match['home_team']} vs {match['away_team']}"
            )

            print(
                f"🏆 {match['sport_title']}"
            )

            bookmakers = (
                match.get(
                    "bookmakers",
                    []
                )
            )

            if bookmakers:

                first_book = (
                    bookmakers[0]
                )

                print(
                    f"📚 BOOK: {first_book['title']}"
                )

                markets = (
                    first_book.get(
                        "markets",
                        []
                    )
                )

                if markets:

                    first_market = (
                        markets[0]
                    )

                    outcomes = (
                        first_market.get(
                            "outcomes",
                            []
                        )
                    )

                    for outcome in outcomes:

                        print(

                            f"➡ {outcome['name']} | "
                            f"ODDS: {outcome['price']} | "
                            f"LINE: {outcome.get('point', '-')}"

                        )

    else:

        print("\n❌ API ERROR:\n")

        print(data)

except Exception as e:

    print("\n❌ REQUEST FAILED:\n")

    print(e)