import json
from flask import Flask
from flask import request

app = Flask(__name__)


@app.route("/")
def index():
    decklink = request.args.get("decklink", "")
    if decklink:
        decklist = parse_deck(decklink)
    else:
        decklist = ""
    return (
        """<form action="" method="get">
                Input deck link: <input type="text" name="decklink">
                <input type="submit" value="Submit Deck">
            </form>"""
        + "Results Printing: "
        + decklist
    )


def parse_deck(decklink):
    """Convert Celsius to Fahrenheit degrees."""
    import mtg_parser
    import json
    decklist = mtg_parser.parse_deck(decklink)
    with open(decklist, encoding='utf8') as json_file:
        carddata = json.load(json_file)
    return str(carddata)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
