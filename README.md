# CommanderCraft
A multipurpose EDH deck analyser for Magic the Gathering

Current Functions:
  - Legality checker (100 cards, colour identity, format legalities)
  - Distributions of each card type
  - Average CMC with and without lands
  - Average power and toughtness of creatures
  - Mana symbols and mana symbols on lands
  - Artist information and set information, commonalities
  - Creature type information, commonalities
  - EDHREC Ranking information, how boring is your deck?
  - Implemented Selenium webscraping from the Scryfall Tagger site
        - Most common art and function tags
        - Number of removal pieces
        - PARTIALLY DONE: - Removal-o-meter / Interactivity-o-meter, card draw levels, ramp levels
    

For Bulk Data Testing
  - Average EDHREC ranks

Roadmap:
  - Lands required calculator (far future: The "Auto-Lander")
  - Scryfall Tagger functions:
      - Strictly better
  - Using EDHREC data, all possible combos, potential combos by adding one more card etc
  - Pricing information (combine this with "strictly worse" tags for a downgrader function?)
  - Token information, what tokens are required to play and how many of them on average
  - Friend suggestions:
      - Draw-o-meter, how much of your deck will you see, factoring in draw per turn and draw effects (lot's o math)
