import React, { useState } from 'react';
import './googlereviews.css';

const GoogleReviews = () => {
  const [siteLinks, setSiteLinks] = useState(''); // For multiple links
  const [statusMessage, setStatusMessage] = useState('');

  const handleScrape = async () => {
    try {
      if (!siteLinks.trim()) {
        setStatusMessage('Please enter at least one valid link.');
        return;
      }

      {/*
      // Warn the user about Chrome windows
      const proceed = window.confirm(
        'Warning: Chrome windows will open during extraction. Please do not close/minimize any windows. Proceed?'
      );

      if (!proceed) {
        setStatusMessage('Scraping cancelled by the user.');
        return;
      }
      */}

      setStatusMessage('Scraping started... Please wait.');

      // Split links by new lines and clean up empty entries
      const linksArray = siteLinks
        .split('\n')
        .map((link) => link.trim())
        .filter((link) => link !== '');

      // Loop through links and send one by one
      for (let i = 0; i < linksArray.length; i++) {
        setStatusMessage(`Scraping link ${i + 1} of ${linksArray.length}...`);

        const response = await fetch('http://127.0.0.1:5000/scrape_reviews', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            link: linksArray[i], // Send one link at a time
          }),
        });

        if (response.ok) {
          const responseData = await response.json();
          setStatusMessage(
            `Link ${i + 1} scraped successfully. ${responseData.message}`
          );
        } else {
          const errorData = await response.json();
          setStatusMessage(
            `Failed to scrape link ${i + 1}: ${
              errorData.error || 'Unknown error'
            }`
          );
        }
      }

      setStatusMessage(
        `Scraping completed for all links. Files are saved in the 'scraped_outputs' folder inside your Downloads directory.`
      );
    } catch (error) {
      console.error('Error during scrape:', error);
      setStatusMessage('An error occurred during scraping.');
    }
  };

  return (
    <div className="App">
      <h1>Google Reviews Scraper</h1>
      <div className="form-group">
        <label htmlFor="site-links">
          Enter Site Links (one link per line):
        </label>
        <textarea
          id="site-links"
          value={siteLinks}
          onChange={(e) => setSiteLinks(e.target.value)}
          placeholder="Enter each Google reviews link on a new line"
          rows="8"
          cols="50"
        />
      </div>
      <button onClick={handleScrape}>Scrape Reviews</button>
      <p className="status-message">{statusMessage}</p>
    </div>
  );
};

export default GoogleReviews;
