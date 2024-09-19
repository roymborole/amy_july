document.addEventListener('DOMContentLoaded', function() {
    const tickerRoot = document.getElementById('ticker-tape-root');
    if (!tickerRoot) {
        console.error('Ticker tape root element not found');
        return;
    }

    const headlines = [
        { text: "The Spotify Paradox: When Soaring Growth Meets Shaky Foundations", link: 'https://finance.yahoo.com/quote/MRNA/' },
        { text: "Bulletproof Profits: Rheinmetall's Explosive 3-Year Surge", link: 'https://finance.yahoo.com/quote/MRNA/' },
        { text: "Rocket Science Meets Voodoo Economics: Intuitive Machines' Stellar Technical Analysis", link: 'https://finance.yahoo.com/quote/MRNA/' },
        { text: "SAAB Fundamental Analysis: A Deep Dive into Defense Industry Dynamics", link: 'https://finance.yahoo.com/quote/MRNA/' },
    ];

    const tickerContent = document.createElement('div');
    tickerContent.className = 'ticker-tape-content';

    headlines.forEach(headline => {
        const link = document.createElement('a');
        link.href = headline.link;
        link.textContent = headline.text;
        link.className = 'ticker-item';
        tickerContent.appendChild(link);
    });

    const tickerTape = document.createElement('div');
    tickerTape.className = 'ticker-tape';
    tickerTape.appendChild(tickerContent);

    // Clone the content for seamless looping
    tickerTape.appendChild(tickerContent.cloneNode(true));

    tickerRoot.appendChild(tickerTape);

    console.log('Ticker tape created:', tickerTape);
});