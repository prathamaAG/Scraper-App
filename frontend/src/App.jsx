import React from 'react';
import Navbar from './components/Navbar/Navbar';
import Attractions from './components/Scrape_attractions/attractions';
import Reviews from './components/Scrape_reviews/Reviews';
import HomePage from './components/Home/home';

import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import GoogleReviews from './components/ScrapeGoogleReviews/googlereviews';

const Home1 = () => {
  return (
    <>
      <Navbar />
      <HomePage />
    </>
  );
};

const ScrapeAttractions1 = () => {
  return (
    <>
      <Navbar />
      <Attractions/>
      {/* Add other components or content for the Members page */}
    </>
  );
};

const ScrapeReviews1 = () => {
  return (
    <>
      <Navbar />
      <Reviews/>
      {/* Add other components or content for the Members page */}
    </>
  );
};

const ScrapeGoogleReviews = () => {
  return (
    <>
      <Navbar />
      <GoogleReviews/>
      {/* Add other components or content for the Members page */}
    </>
  );
};

const App = () => {
  return (
    <Router>
      <Routes>
      <Route path="/" element={<Home1/>} />
        <Route path="/scrape_attractions" element={<ScrapeAttractions1/>} />
        <Route path="/scrapeTripAdvisorReviews" element={<ScrapeReviews1/>} />
        <Route path="/scrapeGoogleReviews" element={<ScrapeGoogleReviews/>} />
      </Routes>
    </Router>
  );
};

export default App;
