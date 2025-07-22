import React, { useState, useEffect } from 'react';
import Loader from '../Loader/Loader';
import './style.css';
import io from 'socket.io-client';
import JSZip from 'jszip';
import { saveAs } from 'file-saver';

const socket = io('http://localhost:5000');

const Attractions = () => {
  // State variables for input fields
  const [data1, setData1] = useState([{}])
  const [attractionCount1, setAttractionCount1] = useState(0)
  const [cityName, setCityName] = useState('');
  const [loading, setLoading] = useState(false)
  const [progress1, setProgress1] = useState(0)
  const [isDataAcquired1, setIsDataAcquired1] = useState(false)
  const defaultHeaders = [
    {
      key: 'User-Agent',
      value: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/109.0'
    },
    {
      key: 'Accept',
      value: 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,/;q=0.8'
    },
    {
      key: 'Accept-Language',
      value: 'en-US,en;q=0.5'
    },
    {
      key: 'Accept-Encoding',
      value: 'gzip, deflate'
    },
    {
      key: 'Connection',
      value: 'keep-alive'
    },
    {
      key: 'Upgrade-Insecure-Requests',
      value: '1'
    },
    {
      key: 'Sec-Fetch-Dest',
      value: 'document'
    },
    {
      key: 'Sec-Fetch-Mode',
      value: 'navigate'
    },
    {
      key: 'Sec-Fetch-Site',
      value: 'none'
    },
    {
      key: 'Sec-Fetch-User',
      value: '?1'
    },
    {
      key: 'Cache-Control',
      value: 'max-age=0'
    },
    {
      key: 'Referer',
      value: 'http://www.google.com/'
    }
  ];
  const [headers1, setHeaders1] = useState(defaultHeaders);
  const [urls, setUrls] = useState('');

  // useEffect(() => {
  //   const storedIsDataAcquired1 = localStorage.getItem('isDataAcquired1');
  //   if (storedIsDataAcquired1) {
  //     setIsDataAcquired1(JSON.parse(storedIsDataAcquired1));
  //   }
  // }, []);

  const handleAddHeader = () => {
    setHeaders1([...headers1, { key: '', value: '' }]);
    console.log('Added header:', headers1)
  };

  const handleDeleteHeader = (index) => {
    // if (index < defaultHeaders.length) {
    //   alert('Cannot delete default header');
    //   return;
    // }
    const updatedHeaders = [...headers1];
    updatedHeaders.splice(index, 1);
    setHeaders1(updatedHeaders);
  };

  const handleHeaderChange = (index, keyOrValue, value) => {
    const updatedHeaders = [...headers1];
    updatedHeaders[index][keyOrValue] = value;
    setHeaders1(updatedHeaders);
    console.log('Updated headers1:', headers1)
  };

const runPythonCode1 = async (e) => {
    e.preventDefault();
    setLoading(true);
    setIsDataAcquired1(false);
  
    const urlList = urls.split(',').map(url => url.trim());
  
    for (const url of urlList) {
      try {
        if (!isDataAcquired1) {
          // First get the attraction name
          const cityNameResponse = await fetch('http://127.0.0.1:5000/scraper2name', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              headers: headers1,
              urls: url
            }),
          });

          let attractionName = 'attraction';
          if (cityNameResponse.ok) {
            const cityNameData = await cityNameResponse.json();
            attractionName = cityNameData.city_name;
            setCityName(cityNameData.city_name);
          } else {
            console.log('Failed to fetch attraction name');
          }

          // Then get the review data
          const response = await fetch('http://127.0.0.1:5000/secondScraper', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              headers: headers1,
              attractionCount: attractionCount1,
              urls: url
            }),
          });
  
          if (response.ok) {
            const responseData = await response.json();
            
            // Download reviews CSV
            const reviewsBlob = new Blob([responseData.reviews_csv], { type: 'text/csv' });
            const reviewsUrl = window.URL.createObjectURL(reviewsBlob);
            const reviewsLink = document.createElement('a');
            reviewsLink.href = reviewsUrl;
            reviewsLink.setAttribute('download', `${attractionName}_reviews.csv`);
            document.body.appendChild(reviewsLink);
            reviewsLink.click();
            document.body.removeChild(reviewsLink);
            window.URL.revokeObjectURL(reviewsUrl);
            
            // Download images CSV
            const imagesBlob = new Blob([responseData.images_csv], { type: 'text/csv' });
            const imagesUrl = window.URL.createObjectURL(imagesBlob);
            const imagesLink = document.createElement('a');
            imagesLink.href = imagesUrl;
            imagesLink.setAttribute('download', `${attractionName}_images.csv`);
            document.body.appendChild(imagesLink);
            imagesLink.click();
            document.body.removeChild(imagesLink);
            window.URL.revokeObjectURL(imagesUrl);
            
            setData1(responseData.reviews_csv);
            setIsDataAcquired1(true);
          } else {
            console.log('Failed to fetch data');
          }
        }
      } catch (error) {
        console.log(error);
      }
    }
    setLoading(false);
    setIsDataAcquired1(false);
};

const runPythonCode2 = async (e) => {
  e.preventDefault();
  setLoading(true);
  setIsDataAcquired1(false);

  const timestamp = new Date().toISOString().replace(/[:.]/g, '-'); // Safe timestamp format
  const urlList = urls.split(',').map(url => url.trim());

  for (const url of urlList) {
    try {
      if (!isDataAcquired1) {
        // Fetch attraction name
        const cityNameResponse = await fetch('http://127.0.0.1:5000/scraper2name', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            headers: headers1,
            urls: url
          }),
        });

        let attractionName = 'attraction';
        if (cityNameResponse.ok) {
          const cityNameData = await cityNameResponse.json();
          attractionName = cityNameData.city_name;
          setCityName(cityNameData.city_name);
        } else {
          console.log('Failed to fetch attraction name');
        }

        // Fetch review data
        const response = await fetch('http://127.0.0.1:5000/secondScraper', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            headers: headers1,
            attractionCount: attractionCount1,
            urls: url
          }),
        });

        if (response.ok) {
          const responseData = await response.json();

          const folderName = `${attractionName}_${timestamp}`;
          // Download reviews CSV
          const reviewsBlob = new Blob([responseData.reviews_csv], { type: 'text/csv' });
          const reviewsUrl = window.URL.createObjectURL(reviewsBlob);
          const reviewsLink = document.createElement('a');
          reviewsLink.href = reviewsUrl;
          reviewsLink.setAttribute('download', `${folderName}/${attractionName}_reviews.csv`);
          document.body.appendChild(reviewsLink);
          reviewsLink.click();
          document.body.removeChild(reviewsLink);
          window.URL.revokeObjectURL(reviewsUrl);

          // Download and zip images
          const imagesCsv = responseData.images_csv;
          console.log("Image download has started");
          const imageUrls = imagesCsv.split('\n').slice(1); // Skip the header
          const zip = new JSZip();

          const fetchImagePromises = imageUrls.map(async (link, index) => {
            if (link.trim()) {
              const imageResponse = await fetch(link.trim());
              if (imageResponse.ok) {
                const blob = await imageResponse.blob();
                const ext = link.split('.').pop().split('?')[0]; // Extract extension
                zip.file(`image${index + 1}.${ext}`, blob); // Save image in the zip
              }
            }
          });

          await Promise.all(fetchImagePromises);
          const zipBlob = await zip.generateAsync({ type: 'blob' });
          saveAs(zipBlob, `${folderName}/${attractionName}_images.zip`);

          setData1(responseData.reviews_csv);
          setIsDataAcquired1(true);
        } else {
          console.log('Failed to fetch data');
        }
      }
    } catch (error) {
      console.log(error);
    }
  }
  setLoading(false);
  setIsDataAcquired1(false);
};


  useEffect(() => {
      socket.on('progress', ({ percentage }) => {
          setProgress1(percentage);
      });
      return () => {
          socket.off('progress');
      };
  }, []);

  return (
    <>
    <h1 className="page-heading">TripAdvisor Reviews Scraper</h1>{loading ?
      <>
        <div className='progress-section'>
          <label htmlFor='progress'>Progress:</label>
          <progress style={{ color: '#7A5CFA' }} id='progress' value={progress1} max='100'></progress>
        </div>
        <Loader />
      </>
      : (
    <>
      <div className='body'>
        <div className='input-section1'>
          {headers1.map((header, index) => (
            <div key={index} className="header-input-container">
              <input
                className='header-key-input'
                type='text'
                placeholder='Header Key'
                value={header.key}
                onChange={(e) => handleHeaderChange(index, 'key', e.target.value)}
              />
              <input
                className='header-value-input'
                type='text'
                placeholder='Header Value'
                value={header.value}
                onChange={(e) => handleHeaderChange(index, 'value', e.target.value)}
              />
              {/* {index >= defaultHeaders.length && ( */}
                <button type='button' onClick={() => handleDeleteHeader(index)}>Delete</button>
              {/* )} */}
            </div>
          ))}
            <br/>
            <button type='button' onClick={handleAddHeader}>Add Header</button>
        </div>
        {/* <div className='input-section'>
          <label htmlFor='headers'>Headers:</label>
          <textarea 
            id='headers'
            value={headers} 
            // onChange={handleHeadersChange}
            placeholder='Enter headers...' // Placeholder text for the textarea
            rows='7' // Make textarea bigger by specifying the number of rows
          />
          <br />
          <br />
            <button
              // onClick={handleUpdateHeaders}
            >Add Header</button>
        </div> */}
          <br/>
        <div className='input-section'>
          <label htmlFor='starterLinks'>Starter Links:</label>
          <textarea 
            id='starterLinks' 
            value={urls} 
            onChange={(e) => setUrls(e.target.value)} 
            placeholder='Enter starter links...(Comma Seperated)' // Placeholder text for the textarea
            rows='4' // Make textarea bigger by specifying the number of rows
          />
        </div>
        <div className='input-section'>
          <label htmlFor='numAttractions'>Number of Reviews:</label>
          <input 
            type='number' 
            id='numAttractions' 
            value={attractionCount1} 
            onChange={(e) => setAttractionCount1(e.target.value)} 
            placeholder='Enter attractions count... (Will round up to the nearest multiple of 10 or maximum, Enter 0 for all attractions).'
          />
        </div>
        <div className='input-section' style={{ display: 'flex', justifyContent: 'space-between' }}>
  <button onClick={runPythonCode1}>Scrape Reviews and Images (CSV)</button>
  <button onClick={runPythonCode2}>Scrape Reviews and Images (JPG)</button>
</div>
      </div>
    </>
  )}
  </>
  );
};

export default Attractions;