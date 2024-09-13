import React, { useEffect, useRef } from 'react';

const SearchBar = () => {
  const containerRef = useRef(null);

  useEffect(() => {
    const loadLottieAndInitSearch = async () => {
      if (typeof window !== 'undefined' && !window.lottie) {
        const lottieScript = document.createElement('script');
        lottieScript.src = 'https://cdnjs.cloudflare.com/ajax/libs/lottie-web/5.7.14/lottie.min.js';
        lottieScript.async = true;
        document.body.appendChild(lottieScript);

        await new Promise((resolve) => {
          lottieScript.onload = resolve;
        });
      }

      if (window.SearchModule) {
        window.SearchModule.init(containerRef.current.id, {
          customHtml: `
            <form id="search-form" class="relative">
              <div class="flex">
                <input type="text" class="w-full px-4 py-2 rounded-l-md bg-gray-700 text-white focus:outline-none" id="search-input" placeholder="Search for a company" required>
                <button class="px-4 py-2 bg-orange-500 text-white rounded-r-md hover:bg-orange-600 focus:outline-none" type="submit">Analyze</button>
              </div>
              <div id="autocomplete-results" class="absolute w-full bg-gray-800 text-white shadow-md mt-1 rounded-md"></div>
            </form>
            <div id="loading" class="hidden">
              <div id="lottie-container"></div>
              <p>Generating report... Please wait.</p>
            </div>
          `
        });
      }
    };

    loadLottieAndInitSearch();
  }, []);

  return <div id="search-container" ref={containerRef} className="mb-8"></div>;
};

export default SearchBar;