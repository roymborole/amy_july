document.addEventListener('DOMContentLoaded', function() {
    const tickerRoot = document.getElementById('ticker-tape-root');
    const tickerContent = tickerRoot.querySelector('.ticker-tape-content');
    
    if (!tickerRoot || !tickerContent) {
        console.error('Ticker tape elements not found');
        return;
    }

    const headlines = [
        // { text: " 💶 Bulletproof Profits: Rheinmetall's Explosive 3-Year Surge 💶 ", link: 'https://finance.yahoo.com/quote/MRNA/' },
        { text: " 🚀 Rocket Science Meets Voodoo Economics: Intuitive Machines' Stellar Technical Analysis 🚀 ", link: 'https://100-x.club/blog/post/3abTjGqoimsasrZcwSL9rj' },
        { text: " 💭 Digital Dreams vs. Analog Reality: Hasbro and Mattel's Diverging Paths 💭", link: 'https://100-x.club/blog/post/2OUYofH0N0nqL7uWoC1Jl3' },
        { text: "🧶 Beyond Butt Plugs and Doilies: Etsy's Unconventional Path to E-commerce Success 🧶", link: 'https://100-x.club/blog/post/4SEQrEmyLFVsmMURJCNzz2' },
        { text: " 💭From Facepalm to Face Mask: Why Pinterest Might Outlast the Social Media Hangover 🧶", link: 'http://100-x.club/blog/post/5LHFusXfrAJCchHktB2n9w' }
    ];


    headlines.forEach((headline, index) => {
        const link = document.createElement('a');
        link.href = headline.link;
        link.textContent = headline.text;
        link.className = 'ticker-item';
        tickerContent.appendChild(link);

        // Add spacing after each headline, except the last one
        if (index < headlines.length - 1) {
            const spacing = document.createElement('span');
            spacing.textContent = '      '; // 6 space characters
            spacing.className = 'ticker-spacing';
            tickerContent.appendChild(spacing);
        }
    });

    console.log('Ticker tape updated');
});