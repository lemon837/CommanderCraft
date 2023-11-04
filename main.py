"""
A multiuse EDH deck analyser
"""
# {'object' 'id' 'oracle_id' 'multiverse_ids' 'mtgo_id' 'tcgplayer_id' 'cardmarket_id' 'name' 'lang' 'released_at'
# 'uri' 'scryfall_uri' 'layout' 'highres_image' 'image_status' 'image_uris' 'normal' 'large' 'png' 'art_crop'
# 'border_crop' 'mana_cost' 'cmc' 'type_line' 'oracle_text' 'power' 'toughness' 'colors' 'color_identity' 'keywords'
# 'legalities' 'games' 'reserved' 'foil' 'nonfoil' 'finishes' 'oversized' 'promo' 'reprint' 'variation' 'set_id' 'set'
# 'set_name' 'set_type' 'set_uri' 'set_search_uri' 'scryfall_set_uri' 'rulings_uri' 'prints_search_uri'
# 'collector_number' 'digital' 'rarity' 'flavor_text' 'card_back_id' 'artist' 'artist_ids' 'illustration_id'
# 'border_color' 'frame' 'security_stamp' 'full_art' 'textless' 'booster' 'story_spotlight' 'edhrec_rank' 'preview'
# 'previewed_at' 'prices' 'related_uris':{'tcgplayer_infinite_articles' 'tcgplayer_infinite_decks'} 'edhrec'
# 'purchase_uris':{'cardmarket' 'cardhoarder'}
# Gaffer: https://www.moxfield.com/decks/5TJaqTq0QUmxfZP5J5MY6w
# Teysa: https://www.moxfield.com/decks/mskhYkY4vUenK3khBTrcMg
import json
import mtg_parser
# from collections import Counter

# Loads the Scryfall card data from JSON to Python dictionary
print('Retrieving Card Data...')
dataform = str("oracle_cards.json").strip("'<>() ").replace('\'', '\"')
if dataform is None:
    exit('Error parsing card data')
with open(dataform, encoding='utf8') as json_file:
    carddata = json.load(json_file)


def check_legality(decklist):
    """
    Takes a decklist input and checks the legality of the deck, returning true if legal and false if illegal
    :param decklist:
    :return true if legal, false if illegal:
    """
    print('Checking deck legality...')
    commandercolours = decklist[0]['color_identity']
    print("Commander's colour identity: " + str(commandercolours))
    if not len(decklist) == 100:
        print('Legality error: Deck is not 100 cards')
        return False
    for card in decklist:
        if not all((elem in commandercolours for elem in card['color_identity'])):
            print(card['name'] + " not in commander's colour identity!")
            return False
        if card['legalities']['commander'] == 'not_legal' or card['legalities']['commander'] == 'banned':
            print('Legality Error: ' + card['name'] + ' not legal in commander!')
            return False
    print('Deck is legal!')
    return True


def basic_functions(decklist):
    """
    Takes a decklist input and provides a very basic analysis of the deck statistics
    :param decklist:
    """
    # Type distribution
    planeswalkers = creatures = sorceries = instants = artifacts = enchantments = lands = 0
    for card in decklist:
        if 'Planeswalker' in card['type_line']:
            planeswalkers += 1
            continue
        if 'Creature' in card['type_line']:
            creatures += 1
            continue
        if 'Sorcery' in card['type_line']:
            sorceries += 1
            continue
        if 'Instant' in card['type_line']:
            instants += 1
            continue
        if 'Artifact' in card['type_line']:
            artifacts += 1
            continue
        if 'Enchantment' in card['type_line']:
            enchantments += 1
            continue
        if 'Land' in card['type_line']:
            lands += 1

    # Average CMC, Power and Toughness
    avgcmc = avgpwr = avgtuf = 0.0
    cmccounter = statcounter = 0.0
    for card in decklist:
        if 'Land' not in card['type_line']:
            avgcmc += card['cmc']
            cmccounter += 1.0
        if 'Creature' in card['type_line']:
            avgpwr += float(card['power'])
            avgtuf += float(card['toughness'])
            statcounter += 1.0
    avgcmclands = avgcmc / (cmccounter + lands)
    avgcmc /= cmccounter
    avgpwr /= statcounter
    avgtuf /= statcounter

    # Print stats
    print('Average CMC: ' + str(round(avgcmc, 2)) + ' (including lands: ' + str(round(avgcmclands, 2)) + ')')
    print('Average Power and Toughness: ' + str(round(avgpwr, 2)) + ' / ' + str(round(avgtuf, 2)))
    print('Card Type Distributions:\n\tPlaneswalkers: ' + str(planeswalkers) + '\n\tCreatures: ' + str(creatures) +
          '\n\tSorceries: ' + str(sorceries) + '\n\tInstants: ' + str(instants) + '\n\tArtifacts: ' + str(artifacts) +
          '\n\tEnchantments: ' + str(enchantments) + '\n\tLands: ' + str(lands))


def process_deck(deckinput):
    """
    Takes deckinput from user, returns decklist, a list of card structs
    :param deckinput:
    :return decklist:
    """
    print('Processing now...')
    rawdecklist = mtg_parser.parse_deck(deckinput)
    # Creates a new decklist out of Scryfall data, using the decklist provided
    decklist = []
    for card in rawdecklist:
        i = 0
        for _ in carddata:
            if carddata[i].get('name') == card.name:
                j = 0
                while j < card.quantity:
                    decklist.append(carddata[i])
                    j += 1
            i += 1
    return decklist


def main():
    """
    Execute the main function, calling various other functions at the user's request, WIP
    """
    print('Please input your Moxfield deck URL below: ')
    decklist = process_deck('https://www.moxfield.com/decks/mskhYkY4vUenK3khBTrcMg')
    if not check_legality(decklist):
        exit("Deck illegal, exiting...")
    basic_functions(decklist)


if __name__ == '__main__':
    main()
