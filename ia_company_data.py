

COMPANIES = {

"Apple Inc.": "AAPL",
"Abbott Laboratories": "ABT",
"Aflac Inc.": "AFL",
"Akamai Technologies, Inc.": "AKAM",
"Advanced Micro Devices, Inc.": "AMD",
"Amgen Inc.": "AMGN",
"Amazon.com, Inc.": "AMZN",
"Aon plc": "AON",
"Activision Blizzard, Inc.": "ATVI",
"Booking Holdings Inc.": "BKNG",
"BlackRock, Inc.": "BLK",
"Boston Scientific Corporation": "BSX",
"Caterpillar Inc.": "CAT",
"Chubb Limited": "CB",
"Cboe Global Markets, Inc.": "CBOE",
"Carnival Corporation": "CCL",
"Cadence Design Systems, Inc.": "CDNS",
"Cigna Corporation": "CI",
"Cummins Inc.": "CMI",
"ConocoPhillips": "COP",
"Costco Wholesale Corporation": "COST",
"Campbell Soup Company": "CPB",
"Cisco Systems, Inc.": "CSCO",
"CVS Health Corporation": "CVS",
"Lockheed Martin Corporation": "LMT",
"Mastercard Incorporated": "MA",
"Marriott International, Inc.": "MAR",
"Mattel, Inc.": "MAT",
"Microchip Technology Incorporated": "MCHP",
"MGM Resorts International": "MGM",
"Monster Beverage Corporation": "MNST",
"Morgan Stanley": "MS",
"Microsoft Corporation": "MSFT",
"M&T Bank Corporation": "MTB",
"Netflix, Inc.": "NFLX",
"AT&T Inc.": "T"

}


from fuzzywuzzy import process
import yfinance as yf


def get_ticker_from_name(name):
    # Try fuzzy matching first
    match = process.extractOne(name.lower(), COMPANIES.keys())
    if match and match[1] >= 80:
        return COMPANIES[match[0]]
    
    # If no match, try yfinance
    try:
        ticker = yf.Ticker(name)
        info = ticker.info
        if 'symbol' in info:
            return info['symbol']
    except Exception as e:
        print(f"Error finding ticker for {name}: {str(e)}")
    
    # If all else fails, return the input as is
    return name