import React from 'react';
import {useEffect} from 'react';
import './Generated.css'
import GeneratedTimetable from './GeneratedTimetable';
import arrow from './assets/arrow.png';
import { Link } from 'react-router-dom';

function Generated({generationDone, generationError, imagesData}) {

  const timetables = ["https://modswithfriends.onrender.com/Server/1.png",
    "https://modswithfriends.onrender.com/Server/2.png",
    "https://modswithfriends.onrender.com/Server/3.png",
    "https://modswithfriends.onrender.com/Server/4.png",
    "https://modswithfriends.onrender.com/Server/5.png",
    "https://modswithfriends.onrender.com/Server/6.png",
    "https://modswithfriends.onrender.com/Server/7.png",
    "https://modswithfriends.onrender.com/Server/8.png",
    "https://modswithfriends.onrender.com/Server/9.png",
    "https://modswithfriends.onrender.com/Server/10.png",
  ];
  useEffect(() => {
    console.log(imagesData);
  }, [imagesData]);

  return (
    <div className='generated-wrapper'>
      <div className='generated-container'>
        <div className='back-container'>
          <Link to='/session' className='link'>
            <img className='back-arrow' src={arrow} />
          </Link>
        </div>
        {generationDone && !generationError ? imagesData.map(imageData => {
          return <GeneratedTimetable imageData={imageData}/>
        }) :  generationError ? 
        <div className='no-timetable-wrapper'>
          <p className='no-timetable'>There are no possible timetables</p> 
        </div> :
        <div className='loader-container'> 
          <span class="loader"></span>
        </div>}
      </div>
    </div>
  )
}

export default Generated;