import React, { useEffect, useState } from 'react';
import { getTopStories } from '../utils/contentful';
import '../styles/TickerTape.css';

const TickerTape = () => {
  const [stories, setStories] = useState([]);

  useEffect(() => {
    async function fetchStories() {
      const fetchedStories = await getTopStories(10);
      setStories(fetchedStories.map(story => story.fields.title));
    }
    fetchStories();
  }, []);

  return (
    <div className="ticker-tape bg-black text-white py-2 overflow-hidden">
      <div className="ticker-tape-content">
        {stories.map((story, index) => (
          <span key={index} className="mx-4">{story}</span>
        ))}
      </div>
    </div>
  );
};

export default TickerTape;