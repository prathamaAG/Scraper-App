import React, { useState, useEffect } from 'react';
import Loader from '../Loader/Loader';
import io from 'socket.io-client';
import './style.css';
const socket = io('http://localhost:5000');

const Attractions = () => {
  // State variables for input fields
  const [data, setData] = useState([{}])
  const [attractionCount, setAttractionCount] = useState(0)
  const [cityName, setCityName] = useState('');
  const [loading, setLoading] = useState(false)
  const [isDataAcquired, setIsDataAcquired] = useState(false)
  const [progress, setProgress] = useState(0)
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
  const [headers, setHeaders] = useState(defaultHeaders);
  const [urls, setUrls] = useState('');

  // useEffect(() => {
  //   const storedIsDataAcquired = localStorage.getItem('isDataAcquired');
  //   if (storedIsDataAcquired) {
  //     setIsDataAcquired(JSON.parse(storedIsDataAcquired));
  //   }
  // }, []);

  const handleAddHeader = () => {
    setHeaders([...headers, { key: '', value: '' }]);
    console.log('Added header:', headers)
  };

  const handleDeleteHeader = (index) => {
    // if (index < defaultHeaders.length) {
    //   alert('Cannot delete default header');
    //   return;
    // }
    const updatedHeaders = [...headers];
    updatedHeaders.splice(index, 1);
    setHeaders(updatedHeaders);
  };

  const handleHeaderChange = (index, keyOrValue, value) => {
    const updatedHeaders = [...headers];
    updatedHeaders[index][keyOrValue] = value;
    setHeaders(updatedHeaders);
    console.log('Updated headers:', headers)
  };

  const runPythonCode = async (e) => {
    e.preventDefault();
    setLoading(true);
  
    const urlList = urls.split(',').map(url => url.trim());
  
    for (const url of urlList) {
      try {
        if (!isDataAcquired) {
          const response = await fetch('http://127.0.0.1:5000/firstScraper', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              headers: headers,
              attractionCount: attractionCount,
              urls: url
            }),
          });
  
          if (response.ok) {
            const responseData = await response.text();
            setData(responseData);
  
            const cityNameResponse = await fetch('http://127.0.0.1:5000/scraper1name', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json'
              },
              body: JSON.stringify({
                headers: headers,
                urls: url
              }),
            });
  
            if (cityNameResponse.ok) {
              const cityNameData = await cityNameResponse.json();
              setCityName(cityNameData.city_name);
              setIsDataAcquired(true);
            } else {
              console.log('Failed to fetch city name');
            }
          } else {
            console.log('Failed to fetch data');
          }
        }
      } catch (error) {
        console.log(error);
      }
    }
    setLoading(false);
  };  

  // const runPythonCode = async (e) => {
  //   setLoading(true)
  //   console.log('Running Python code with initial data:', data)
  //   e.preventDefault()
  //   try {
  //     const response = await fetch('/firstScraper', {
  //       method: 'POST',
  //       headers: {
  //         'Content-Type': 'application/json'
  //       },
  //       body: JSON.stringify({
  //         headers: headers,
  //         attractionCount: attractionCount,
  //         urls: urls,
  //         // urls: urls.split(',').map(url => url.trim()), // Split URLs by comma and remove leading/trailing whitespaces
  //       }),
  //     })
  //     if (response.ok) {
  //       const responseData = await response.json()
  //       setData(responseData)
  //       console.log(data)
  //       setLoading(false)
  //       // Fetch city name
  //       const cityNameResponse = await fetch('/scraper1name', {
  //         method: 'POST',
  //         headers: {
  //           'Content-Type': 'application/json'
  //         },
  //         body: JSON.stringify({
  //           headers: headers,
  //           urls: urls
  //         }),
  //       });
  //       if (cityNameResponse.ok) {
  //         const cityNameData = await cityNameResponse.json();
  //         setCityName(cityNameData.city_name);
  //       } else {
  //         console.log('Failed to fetch city name');
  //       }
  //       setIsDataAcquired(true)
  //     } else {
  //       console.log('Failed to fetch')
  //       setLoading(false)
  //     }
  //   } catch (error) {
  //     console.log(error)
  //     setLoading(false)
  //   }
  //   setLoading(false)
  // };

  // const convertToCSV = () => {
  //   // Extract column names from the first object in the data array
  //   const columnNames = Object.keys(data[0]);

  //   // Concatenate column names with data rows
  //   const csvContent = `data:text/csv;charset=utf-8,${columnNames.join(',')}\n${
  //     data.map(row => columnNames.map(name => row[name]).join(',')).join('\n')
  //   }`;

  //   // Create a downloadable link
  //   const encodedURI = encodeURI(csvContent);
  //   const link = document.createElement('a');
  //   link.setAttribute('href', encodedURI);
  //   link.setAttribute('download', `${cityName}_${attractionCount}_Attractions.csv`);
  //   document.body.appendChild(link);
  //   link.click();
  // };

  // const convertToCSV = () => {
  //   const csvContent = "data:text/csv;charset=utf-8," + 
  //                      data.map(row => Object.values(row).join(',')).join('\n');
  //   const encodedURI = encodeURI(csvContent);
  //   const link = document.createElement('a');
  //   link.setAttribute('href', encodedURI);
  //   link.setAttribute('download', `${cityName}_${attractionCount}_Attractions.csv`);
  //   document.body.appendChild(link);
  //   link.click();
  // };
  
  // const convertToCSV = () => {
  //     // Extract column names from the first object in the data array
  //     const columnNames = Object.keys(data[0]);

  //     // Concatenate column names with data rows
  //     const csvContent = `data:text/csv;charset=utf-8,${columnNames.join(',')}\n${
  //       data.map(row => 
  //         columnNames.map(name => {
  //           // If the value contains a comma, enclose it within double quotes
  //           if (typeof row[name] === 'string' && row[name].includes(',')) {
  //             return `"${row[name]}"`;
  //           }
  //           return row[name];
  //         }).join(',')
  //       ).join('\n')
  //     }`;

  //     // Create a downloadable link
  //     const encodedURI = encodeURI(csvContent);
  //     const link = document.createElement('a');
  //     link.setAttribute('href', encodedURI);
  //     link.setAttribute('download', `${cityName}_${attractionCount}_Attractions.csv`);
  //     document.body.appendChild(link);
  //     link.click();
  // };

  const downloadCSV = () => {
      try {
          const csvData = data
          // Create a Blob from CSV data
          const blob = new Blob([csvData], { type: 'text/csv' });
          // Create a URL for the Blob
          const url = window.URL.createObjectURL(blob);
          // Create a link element and simulate click to initiate download
          const a = document.createElement('a');
          a.href = url;
          a.download = `${cityName}_Attractions.csv`;
          a.click();
          // Clean up by revoking the object URL
          window.URL.revokeObjectURL(url);
      } catch (error) {
          console.error('Error downloading CSV:', error);
      }
  };

  useEffect(() => {
    if (isDataAcquired) {
      downloadCSV();
      setProgress(0);
      setIsDataAcquired(false);
    }
  }, [isDataAcquired]);

  useEffect(() => {
      socket.on('progress', ({ percentage }) => {
          setProgress(percentage);
      });
      return () => {
          socket.off('progress');
      };
  }, []);

  return (
    <>
    <h1 className="page-heading">Attractions Scraper</h1>
    {loading ? 
    <>
        <div className='progress-section'>
          <label htmlFor='progress'>Progress:</label>
          <progress color='#7A5CFA' id='progress' value={progress} max='100'></progress>
        </div>
        <Loader />
    </> : (
    <>
      <div className='body'>
        <div className='input-section1'>
          {headers.map((header, index) => (
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
          <label htmlFor='numAttractions'>Number of Attractions:</label>
          <input 
            type='number' 
            id='numAttractions' 
            value={attractionCount} 
            onChange={(e) => setAttractionCount(e.target.value)} 
            placeholder='Enter attractions count... (Will round up to the nearest multiple of 30 or maximum, Enter 0 for all attractions).'
          />
        </div>
        <div className='input-section' style={{ textAlign: 'right' }}>
          <button onClick={runPythonCode}>Scrape Attractions</button>
        </div>
      </div>
    </>
  )}
  </>
  );
};

export default Attractions;
