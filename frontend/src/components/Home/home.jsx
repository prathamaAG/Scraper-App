import React, { useEffect } from 'react';
import introJs from 'intro.js';
import 'intro.js/introjs.css';
import Navbar from '../Navbar/Navbar'; // Import the Navbar component
import './HomePage.css'; // Import your CSS file for styling

const HomePage = () => {
  
  useEffect(() => {
    // Initialize the intro.js tutorial only if it hasn't been seen before
    if (!localStorage.getItem('tutorialSeen')) {
      const intro = introJs();
      
      intro.setOptions({
        steps: [
          {
            element: '#step1', // Linked to the welcome heading
            intro: 'Welcome to our Web Scraping App! This is the homepage.',
          },
          {
            element: '#step2', // Linked to the sidebar
            intro: 'This is the sidebar where you can navigate through the app.',
          },
          {
            element: '#step4', // Linked to "Scrape Attractions"
            intro: 'Click here to scrape attractions from TripAdvisor.',
          },
          {
            element: '#step5', // Linked to "Scrape TripAdvisor Reviews"
            intro: 'Scrape TripAdvisor Reviews with this option.',
          },
          {
            element: '#step6', // Linked to "Scrape Google Reviews"
            intro: 'Scrape Google Reviews with this option.',
          },
          {
            element: '#step7', // Linked to the welcome text
            intro: 'Start your scraping process by selecting an option from the sidebar.',
          }
        ],
        showProgress: true,  // Show progress bar at the top
        exitOnOverlayClick: false,  // Prevent tutorial from closing when clicking outside
        showBullets: false,  // Hide bullets in the steps navigation
        overlayOpacity: 0.7,  // Set the opacity of the overlay
        doneLabel: 'Finish',  // Customize button labels
        nextLabel: 'Next',
        prevLabel: 'Back',
      });
      
      // Start the tutorial automatically when the component is loaded
      intro.start();
      localStorage.setItem('tutorialSeen', 'true');
    }
  }, []);

  return (
    <div className="home-page" style={{ backgroundColor: '#2C2C2C', color: '#fff' }}>
      <Navbar />
      <div className="welcome-message">
        <h1 className="welcome-heading" id="step1">Welcome to our Web Scraping App</h1>
        <p className="welcome-text" id="step7">We help you scrape data easily. Let's get started!</p>
      </div>
    </div>
  );
};

export default HomePage;
