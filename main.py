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
import math
import mtg_parser
import os.path
from collections import Counter
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Global variables
carddata = []
commandercolours = []
manasymbols = {'N': 0, 'C': 0, 'W': 0, 'U': 0, 'B': 0, 'R': 0, 'G': 0}
landmanasymbols = {'C': 0, 'W': 0, 'U': 0, 'B': 0, 'R': 0, 'G': 0}
typedist = {'planeswalkers': 0, 'creatures': 0, 'sorceries': 0, 'instants': 0, 'artifacts': 0, 'enchantments': 0,
            'lands': 0}


def main():
    """
    Execute the main function, calling various other functions at the user's request
    """
    if not os.path.isfile(r"C:\Users\Fred\Desktop\CommanderCraft\decklist.json"):
        print('Please input your deck URL below:')
        decklist = process_deck('https://www.moxfield.com/decks/mskhYkY4vUenK3khBTrcMg')
    else:
        print('Deck located on file! Retrieving...')
        dataform = str("decklist.json").strip("'<>() ").replace('\'', '\"')
        with open(dataform, encoding='utf8') as json_file:
            decklist = json.load(json_file)
    if not check_legality(decklist):
        exit("Deck is illegal, exiting...")
    # basic_functions(decklist)
    tagger_functions(decklist)


def process_deck(deckinput):
    """
    Takes deckinput from user, loads oracle card data and creates a decklist.json out of it, including tags
    :param deckinput:
    :return decklist:
    """
    # Loads the Scryfall card data from JSON to Python dictionary
    print('Retrieving Card Data...')
    dataform = str("oracle_cards.json").strip("'<>() ").replace('\'', '\"')
    if dataform is None:
        exit('Error parsing card data')
    with open(dataform, encoding='utf8') as json_file:
        carddata = json.load(json_file)

    # Creates a new decklist out of Scryfall data, using the decklist provided
    print('Processing now...')
    rawdecklist = mtg_parser.parse_deck(deckinput)
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
    card_tags(decklist)
    print('Writing new decklist txt file...')
    with open('decklist.json', 'x') as deck_file:
        deck_file.write(json.dumps(decklist))
    return decklist


def card_tags(decklist):
    print('Beginning tag search...')
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.experimental_options['prefs'] = {
        'profile.managed_default_content_settings.images': 2
    }
    driver = webdriver.Chrome(options)
    for card in decklist:
        if 'Basic Land' not in card['type_line']:
            url = 'https://tagger.scryfall.com/card/' + card['set'] + '/' + str(card['collector_number'])
            driver.get(url)
            WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//*[contains(text(),"
                                                                                        "'artwork')]")))
            page = driver.page_source
            soup = BeautifulSoup(page, 'html.parser')
            container = soup.find_all('div', attrs={'class': 'tag-row'})

            arttags = []
            functiontags = []
            for element in container:
                element = str(element)
                if element.find('/tags/artwork/') > 0:
                    arttag = ''
                    substr = element.find('/tags/artwork/') + 14
                    for char in element[substr:]:
                        if char.isalpha() or char.isnumeric() or char == '-' or char == ' ':
                            arttag = arttag + char
                        else:
                            break
                    arttags.append(arttag)
                if element.find('/tags/card/') > 0:
                    functiontag = ''
                    substr = element.find('/tags/card/') + 11
                    for char in element[substr:]:
                        if char.isalpha() or char.isnumeric() or char == '-' or char == ' ':
                            functiontag = functiontag + char
                        else:
                            break
                    functiontags.append(functiontag)
            print('Art Tags:', card['name'], arttags)
            print('Function Tags:', card['name'], functiontags)
            card['arttags'] = arttags
            card['functiontags'] = functiontags
    driver.quit()


def check_legality(decklist):
    """
    Takes a decklist input and checks the legality of the deck, returning true if legal and false if illegal
    :param decklist:
    :return true if legal, false if illegal:
    """
    print('Checking deck legality...')
    commandercolours.extend(decklist[0]['color_identity'])
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
    Takes a decklist input and prints a basic analysis of the deck statistics
    :param decklist:
    """
    # Type distribution
    for card in decklist:
        if 'Planeswalker' in card['type_line']:
            typedist['planeswalkers'] += 1
            continue
        if 'Creature' in card['type_line']:
            typedist['creatures'] += 1
            continue
        if 'Sorcery' in card['type_line']:
            typedist['sorceries'] += 1
            continue
        if 'Instant' in card['type_line']:
            typedist['instants'] += 1
            continue
        if 'Artifact' in card['type_line']:
            typedist['artifacts'] += 1
            continue
        if 'Enchantment' in card['type_line']:
            typedist['enchantments'] += 1
            continue
        if 'Land' in card['type_line']:
            typedist['lands'] += 1

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
    avgcmclands = avgcmc / (cmccounter + typedist['lands'])
    avgcmc /= cmccounter
    avgpwr /= statcounter
    avgtuf /= statcounter

    # Mana symbols and card colours
    for card in decklist:
        if 'Land' not in card['type_line']:
            for char in card['mana_cost']:
                if char.isalpha():
                    manasymbols[char] += 1
        else:
            if 'produced_mana' in card:
                for char in card['produced_mana']:
                    if char.isalpha():
                        landmanasymbols[char] += 1
    totalsymbols = manasymbols['W'] + manasymbols['U'] + manasymbols['B'] + manasymbols['R'] + manasymbols['G']
    totallandsymbols = (landmanasymbols['C'] + landmanasymbols['W'] + landmanasymbols['U'] + landmanasymbols['B'] +
                        landmanasymbols['R'] + landmanasymbols['G'])

    # Most common artist and set
    artists = []
    sets = []
    types = []
    for card in decklist:
        artists.append(card['artist'])
        if 'Creature' in card['type_line']:
            creaturetypes = card['type_line'].split('—', 1)
            types.extend(creaturetypes[1].split())
        if 'Basic Land' not in card['type_line']:
            sets.append(card['set'])
    commonartists = Counter(artists)
    commonsets = Counter(sets)
    commontypes = Counter(types)

    # EDHREC Rank
    edhrectotal = 0
    for card in decklist:
        if 'edhrec_rank' in card:
            edhrectotal += card['edhrec_rank']
    edhrectotal /= 100

    # Print stats
    print('Average CMC: ' + str(round(avgcmc, 2)) + ' (including lands: ' + str(round(avgcmclands, 2)) + ')')
    print('Average Power and Toughness: ' + str(round(avgpwr, 2)) + ' / ' + str(round(avgtuf, 2)))
    print('Card Type Distributions: ')
    for cardtype in typedist.keys():
        print('\t' + cardtype, typedist[cardtype])
    for symbol in manasymbols:
        if not manasymbols[symbol] == 0:
            percentage = math.ceil((manasymbols[symbol] / totalsymbols) * 100)
            print(str(percentage) + '% of all mana symbols are ' + symbol)
    for symbol in landmanasymbols:
        if (not landmanasymbols[symbol] == 0 and symbol in commandercolours) or symbol == 'C':
            percentage = math.ceil((landmanasymbols[symbol] / totallandsymbols) * 100)
            print(landmanasymbols[symbol], 'out of', typedist['lands'], 'lands produce', symbol, 'mana (', percentage,
                  '% of all mana symbols on lands )')
    print(max(commonartists, key=commonartists.get), 'is the most common artist (consisting of',
          max(commonartists.values()), 'cards)')
    print(max(commonsets, key=commonsets.get), 'is the most common set (consisting of', max(commonsets.values()),
          'cards)')
    print(max(commontypes, key=commontypes.get), 'is the most common creature type (consisting of',
          max(commontypes.values()), 'cards)')
    print('Average EDHREC rank:', edhrectotal)


def tagger_functions(decklist):
    allarttags = []
    allfunctags = []
    removalcards = []
    for card in decklist:
        if 'Basic Land' not in card['type_line']:
            allarttags.extend(card['arttags'])
            allfunctags.extend(card['functiontags'])
            for tag in card['functiontags']:
                if 'removal' in tag:
                    removalcards.append(card)
                    break
    commonart = Counter(allarttags)
    commonfunc = Counter(allfunctags)
    print(max(commonart, key=commonart.get), 'is the most common art tag (consisting of',
          max(commonart.values()), 'cards)')
    print(max(commonfunc, key=commonfunc.get), 'is the most common art tag (consisting of',
          max(commonfunc.values()), 'cards)')

    print('You have', len(removalcards), 'pieces of removal:')
    cardstr = ''
    for card in removalcards:
        cardstr = cardstr + '[' + card['name'] + '], '
    print(cardstr)


if __name__ == '__main__':
    main()
