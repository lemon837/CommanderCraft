# CommanderCraft
(WIP) A multipurpose EDH deck analyser for the Magic the Gathering card game.

### Deck Analysis:
  - Uses bulkdata download of all default-cards from the Scryfall API, parses deck URL into rawdecklist
  - Creates decklist from default-cards using the names, set codes and collector numbers of cards in rawdecklist
  - Using the Selenium webscraping tool, retrieves tags for all cards in deck from Scryfall Tagger Project
  - Dumps decklist to a .json file, to analyse now and save for later

  - Legality checker (100 cards, colour identity, format legalities)
  
  - Basic Functions:
    - Average CMC with and without lands
    - Average power and toughtness of creatures
    - Distributions of each card type
    - Mana symbols on cards compared with mana symbols on lands
    - Average EDHREC rank
    - Artist, set, and creature type distributions
    - Token information, what tokens are required to play and how many of them on average

  - Tagger Functions
    - Most common art tags and function tags
    - Counters for amount of removal, card draw, and ramp
    - HYPERGEOMETRIC PROBABILITIES! - "By turn x, y% chance to have drawn at least one card of z-type"

### For Bulk Data Testing:
  - Average EDHREC ranks

### Roadmap:
  - The "Auto-Lander", take into account mana symbols on cards and intuitively construct a 37 card landbase
  - 'Strictly better/worse' and 'similar to' html code from Tagger
  - Using EDHREC data: all possible combos, then, potential combos by adding one more card etc
  - Pricing information (combine this with "strictly better/worse" tags for a down/upgrader function)
  - Draw-o-meter, how much of your deck will you see, factoring in draw per turn and draw effects
