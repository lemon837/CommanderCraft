"""
A multiuse EDH deck analyser
"""
import json
import math
import mtg_parser
import os.path
import numpy as np
from scipy.stats import hypergeom
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
manasymbols = {'N': 0, 'C': 0, 'W': 0, 'U': 0, 'B': 0, 'R': 0, 'G': 0, 'P': 0, 'X': 0}
landmanasymbols = {'C': 0, 'W': 0, 'U': 0, 'B': 0, 'R': 0, 'G': 0}
typedist = {'planeswalkers': 0, 'creatures': 0, 'sorceries': 0, 'instants': 0, 'artifacts': 0, 'enchantments': 0,
            'lands': 0}
allarttags = []
allfunctags = []
tokens = []


def main():
    """
    Execute the main function, calling various other functions
    """
    print('Enter below either an existing deck name, or the name of the new deck you would like to create:')
    deckname = input()
    if not os.path.isfile('C:\\Users\\Fred\\Desktop\\CommanderCraft\\' + deckname + '.json'):
        print('New deck! Please input your deck URL below:')
        url = input()
        decklist = process_deck(url, deckname)
    else:
        print('Deck located on file! Retrieving...')
        dataform = str(deckname + '.json').strip("'<>() ").replace('\'', '\"')
        with open(dataform, encoding='utf8') as json_file:
            decklist = json.load(json_file)
    if not check_legality(decklist):
        exit("Deck is illegal, exiting...")
    basic_functions(decklist)
    tagger_functions(decklist)


def process_deck(deckinput, deckname):
    """
    Takes deckinput from user, loads oracle card data and creates a json file out of it, including tags
    :param deckname:
    :param deckinput:
    :return decklist:
    """
    # Loads the Scryfall card data from JSON to Python dictionary
    print('\n---------- Retrieving Card Data and Creating Deck ----------')
    print('Retrieving oracle card data...')
    dataform = str("default-cards.json").strip("'<>() ").replace('\'', '\"')
    if dataform is None:
        exit('Error parsing card data')
    with open(dataform, encoding='utf8') as json_file:
        carddata = json.load(json_file)

    # Creates a new decklist out of Scryfall data, using the decklist provided
    print('Creating deck...')
    rawdecklist = mtg_parser.parse_deck(deckinput)
    decklist = []
    for card in rawdecklist:
        i = 0
        for _ in carddata:
            if (carddata[i].get('name') == card.name and carddata[i].get('collector_number') == card.number
                    and carddata[i].get('set') == card.extension):
                j = 0
                while j < card.quantity:
                    decklist.append(carddata[i])
                    j += 1
            i += 1
    card_tags(decklist)
    print('Writing new decklist txt file...')
    with open(deckname + '.json', 'x') as deck_file:
        deck_file.write(json.dumps(decklist))
    print('Done!')
    return decklist


def card_tags(decklist):
    print('\n---------- Adding Tags ----------')
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.experimental_options['prefs'] = {'profile.managed_default_content_settings.images': 2}
    driver = webdriver.Chrome(options)
    for card in decklist:
        if 'Basic Land' not in card['type_line']:
            arttags = []
            functiontags = []
            hasmisctags = False
            url = 'https://tagger.scryfall.com/card/' + card['set'] + '/' + str(card['collector_number'])
            driver.get(url)
            WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//*[contains(text(),"
                                                                                        "'artwork')]")))
            page = driver.page_source
            soup = BeautifulSoup(page, 'html.parser')

            # Finds all non-inherited tags ('tag-row')
            container = soup.find_all('div', attrs={'class': 'tag-row'})
            for element in container:
                element = str(element)
                if element.find('/tags/artwork/') > 0:
                    arttag = ''
                    substr = element.find('/tags/artwork/') + 14
                    for char in element[substr:]:
                        if char.isalpha() or char.isnumeric() or char == '-' or char == ' ':
                            arttag += char
                        else:
                            break
                    arttags.append(arttag)
                elif element.find('/tags/card/') > 0:
                    functiontag = ''
                    substr = element.find('/tags/card/') + 11
                    for char in element[substr:]:
                        if char.isalpha() or char.isnumeric() or char == '-' or char == ' ':
                            functiontag += char
                        else:
                            break
                    functiontags.append(functiontag)
                else:
                    misctags = {'better-than': [], 'worse-than': [], 'mirror': [], 'colorshifted': [], 'with-body': [],
                                'without-body': [], 'similar-to': []}
                    hasmisctags = True
                    for tag in misctags:
                        if element.find(tag) > 0:
                            foundtag = ''
                            substr = element.find('rel="nofollow">') + 15
                            for char in element[substr:]:
                                if char.isalpha() or char.isnumeric() or char == '-' or char == ' ' or char == '\'':
                                    foundtag += char
                                else:
                                    break
                            misctags[tag].append(foundtag)

            # Finds all inherited tags ('tagging-ancestors')
            container = soup.find_all('div', attrs={'class': 'tagging-ancestors'})
            container = str(container)
            index = 0
            while index < len(container):
                arttag = ''
                index = container.find('/tags/artwork/', index)
                if index == -1:
                    break
                for char in container[(index + 14):]:
                    if char.isalpha() or char.isnumeric() or char == '-' or char == ' ':
                        arttag += char
                    else:
                        break
                arttags.append(arttag)
                index += 14
            index = 0
            while index < len(container):
                functiontag = ''
                index = container.find('/tags/card/', index)
                if index == -1:
                    break
                for char in container[(index + 11):]:
                    if char.isalpha() or char.isnumeric() or char == '-' or char == ' ':
                        functiontag += char
                    else:
                        break
                functiontags.append(functiontag)
                index += 11

            unwanted_tags = {'plane', 'location', 'character', 'artist-signature', 'cycle', 'card-names', 'cycle-land'}
            arttags = [ele for ele in arttags if ele not in unwanted_tags]
            functiontags = [ele for ele in functiontags if ele not in unwanted_tags]
            card['arttags'] = arttags
            card['functiontags'] = functiontags
            print(card['name'])
            print(arttags)
            print(functiontags)
            if hasmisctags:
                print(misctags)
                card['misctags'] = misctags
    driver.quit()


def check_legality(decklist):
    """
    Takes a decklist input and checks the legality of the deck, returning true if legal and false if illegal
    :param decklist:
    :return true if legal, false if illegal:
    """
    print('\n---------- Checking deck legality ----------')
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
    tokennames = []
    avgcmc = avgpwr = avgtuf = 0.0
    cmccounter = statcounter = 0.0
    artists = []
    sets = []
    types = []
    edhrectotal = 0

    print('\n---------- Performing Basic Analysis ----------')
    # Token information
    for card in decklist:
        if 'all_parts' in card:
            for part in card['all_parts']:
                if 'component' in part:
                    if 'token' in part['component']:
                        tokens.append(part)
    for token in tokens:
        for duptoken in tokens:
            if token['name'] == duptoken['name']:
                tokens.remove(duptoken)
    for token in tokens:
        tokennames.append(token['name'])

    # Type distribution
    for card in decklist:
        if 'card_faces' in card:
            tempcard = card['card_faces'][0]
        else:
            tempcard = card
        if 'Planeswalker' in tempcard['type_line']:
            typedist['planeswalkers'] += 1
            continue
        if 'Creature' in tempcard['type_line']:
            typedist['creatures'] += 1
            continue
        if 'Sorcery' in tempcard['type_line']:
            typedist['sorceries'] += 1
            continue
        if 'Instant' in tempcard['type_line']:
            typedist['instants'] += 1
            continue
        if 'Land' in tempcard['type_line']:
            typedist['lands'] += 1
            continue
        if 'Artifact' in tempcard['type_line']:
            typedist['artifacts'] += 1
            continue
        if 'Enchantment' in tempcard['type_line']:
            typedist['enchantments'] += 1
            continue

    # Average CMC, Power and Toughness
    for card in decklist:
        if 'card_faces' not in card:
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
            if 'mana_cost' in card:
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
    for card in decklist:
        if 'Creature' in card['type_line']:
            creaturetypes = card['type_line'].split('—', 1)
            types.extend(creaturetypes[1].split())
        if 'Basic Land' not in card['type_line']:
            sets.append(card['set'])
            artists.append(card['artist'])
    commonartists = Counter(artists)
    commonsets = Counter(sets)
    commontypes = Counter(types)

    # EDHREC Rank
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
        if not symbol == 'P' and not symbol == 'X':
            if not manasymbols[symbol] == 0:
                percentage = math.ceil((manasymbols[symbol] / totalsymbols) * 100)
                print(str(percentage) + '% of all mana symbols are ' + symbol)
    for symbol in landmanasymbols:
        if (not landmanasymbols[symbol] == 0 and symbol in commandercolours) or symbol == 'C':
            percentage = math.ceil((landmanasymbols[symbol] / totallandsymbols) * 100)
            print(landmanasymbols[symbol], 'out of', typedist['lands'], 'lands produce', symbol, 'mana (', percentage,
                  '% of all mana symbols on lands )')
    print('\nAverage EDHREC rank:', edhrectotal)
    print('\nTokens required:', tokennames)
    print('\n[' + str(max(commonartists, key=commonartists.get)) + ']', 'is the most common artist',
          max(commonartists.values()), 'cards)')
    print('\t', commonartists.most_common(10))
    print('[' + str(max(commonsets, key=commonsets.get)) + ']', 'is the most common set', max(commonsets.values()),
          'cards)')
    print('\t', commonsets.most_common(10))
    print('[' + str(max(commontypes, key=commontypes.get)) + ']', 'is the most common creature type',
          max(commontypes.values()), 'cards)')
    print('\t', commontypes.most_common(5))


def tagger_functions(decklist):
    removalcards = []
    rampcards = []
    drawcards = []

    print('\n---------- Performing Tag Analysis ----------')
    """
    for card in decklist:
        if 'misctags' in card:
            for tag in card['misctags']:
    """

    # Compile the allarttags and allfunctiontags lists to find the most common of both lists
    for card in decklist:
        if 'Basic Land' not in card['type_line']:
            allarttags.extend(card['arttags'])
            allfunctags.extend(card['functiontags'])
            if 'removal' in card['functiontags']:
                removalcards.append(card)
            if ('draw' in card['functiontags'] or 'rummage' in card['functiontags'] or
                    'loot' in card['functiontags']):
                drawcards.append(card)
            if 'ramp' in card['functiontags']:
                rampcards.append(card)

    print('Most common art tags:\n\t', Counter(allarttags).most_common(10))
    print('Most common function tags:\n\t', Counter(allfunctags).most_common(10))
    print('\nYou have', len(removalcards), 'pieces of removal:')
    cardstr = ''
    for card in removalcards:
        cardstr = cardstr + '[' + card['name'] + '], '
    print('\t', cardstr)
    result = hypergeo_probability(len(removalcards), 5, 1)
    print('Hypergeometric: By turn FIVE, there is a', str(result) + '%', 'chance that you will have drawn at least '
                                                                         'one removal spell')
    print('\nYou have', len(drawcards), 'pieces of card draw: (counting loot and rummage effects)')
    cardstr = ''
    for card in drawcards:
        cardstr = cardstr + '[' + card['name'] + '], '
    print('\t', cardstr)
    result = hypergeo_probability(len(drawcards), 3, 1)
    print('Hypergeometric: By turn THREE, there is a', str(result) + '%', 'chance that you will have drawn at least '
                                                                          'one card draw spell')
    print('\nYou have', len(rampcards), 'pieces of ramp:')
    cardstr = ''
    for card in rampcards:
        cardstr = cardstr + '[' + card['name'] + '], '
    print('\t', cardstr)
    result = hypergeo_probability(len(rampcards), 3, 1)
    print('Hypergeometric: By turn THREE, there is a', str(result) + '%', 'chance that you will have drawn at least '
                                                                          'one ramp spell')


def hypergeo_probability(cardsindeck, gameturn, wantinhand):
    """
    Calculate the cumulative hypergeometric probabilities of drawing x or more of a card type, by n turn, where there
    is k number of that type of card in your 100 card deck
    :param cardsindeck: Number of cardtype in deck
    :param gameturn: Game turn number
    :param wantinhand: Desired number of that cardtype in hand
    """
    cardsinhand = 7 + gameturn
    exactlyone = hypergeom.pmf(wantinhand, 100, cardsindeck, cardsinhand)
    oneorless = hypergeom.cdf(wantinhand, 100, cardsindeck, cardsinhand)
    k = np.arange(wantinhand)
    zero = hypergeom.pmf(k, 100, cardsindeck, cardsinhand)
    oneormore = 1 - zero[0]
    # print(round(exactlyone * 100, 2))
    # print(round(oneorless * 100, 2))
    # print(round(zero[0] * 100, 2))
    result = round(oneormore * 100, 2)
    return result


if __name__ == '__main__':
    main()
