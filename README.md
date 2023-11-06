# CommanderCraft
A multipurpose EDH deck analyser for Magic the Gathering

### Deck Analysis:
  - Legality checker (100 cards, colour identity, format legalities)
  
  - Basic Functions:
    - Average CMC with and without lands
    - Average power and toughtness of creatures
    - Distributions of each card type
    - Mana symbols on cards compared with mana symbols on lands
    - Average EDHREC rank
    - Artist, set, and creature type distributions

  - Tagger Functions
    - Most common art tags and function tags
    - Counters for amount of removal, card draw, and ramp
    - Hypergeometric probability calculations - "By turn x, y% chance to have drawn at least one card of z-type"
    
### Bug Fixing Required:
  - Cardtype distributions not displaying correct numbers, could be an issue with how cards are added now using
    'default-cards.json' instead of the old method (see 'jolene.json' card distributions)

### For Bulk Data Testing:
  - Average EDHREC ranks

### Roadmap:
  - The "Auto-Lander", take into account mana symbols on cards and intuitively construct a 37 card landbase
  - Token information, what tokens are required to play and how many of them on average
  - 'Strictly better/worse' and 'similar to' html code from Tagger
  - Using EDHREC data: all possible combos, then, potential combos by adding one more card etc
  - Pricing information (combine this with "strictly better/worse" tags for a down/upgrader function)
  - Draw-o-meter, how much of your deck will you see, factoring in draw per turn and draw effects
