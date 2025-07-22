import React from 'react';
import './style.css'; // Make sure you have the appropriate CSS file
import { Link } from 'react-router-dom';

const Navbar = () => {
  return (
    <div>
      {/* Navbar */}
      <nav className="navbar" id="step2">
        <div className='connversehead'>
          <p id='Conn1'>Scrapper</p>
        </div>

        <ul className="nav-items">
          <li className="nav-item" id="step3">
            <Link to="/" className="nav-link">
              <span>Home</span>
            </Link>
          </li>
          <li className="nav-item" id="step4">
            <Link to="/scrape_attractions" className="nav-link">
              <span>Scrape Attractions</span>
            </Link>
          </li>
          <li className="nav-item" id="step5">
            <Link to="/scrapeTripAdvisorReviews" className="nav-link">
              <span>Scrape Reviews</span>
            </Link>
          </li>
          <li className="nav-item" id="step6">
            <Link to="/scrapeGoogleReviews" className="nav-link">
              <span>Scrape Google Reviews</span>
            </Link>
          </li>
        </ul>
      </nav>
    </div>
  );
};

export default Navbar;
