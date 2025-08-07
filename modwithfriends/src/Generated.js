import React from 'react';
import {useEffect, useState} from 'react';
import './Generated.css'
import GeneratedTimetable from './GeneratedTimetable';
import arrow from './assets/arrow.png';
import { Link } from 'react-router-dom';
import tt from './assets/timetable.png';

function Generated({generationDone, generationError, imagesData}) {

  const [selectedImg, setSelectedImg] = useState(imagesData[0]);

  const timetables = ["http://localhost:4000/Server/1.png",
    "http://localhost:4000/Server/2.png",
    "http://localhost:4000/Server/3.png",
    "http://localhost:4000/Server/4.png",
    "http://localhost:4000/Server/5.png",
    "http://localhost:4000/Server/6.png",
    "http://localhost:4000/Server/7.png",
    "http://localhost:4000/Server/8.png",
    "http://localhost:4000/Server/9.png",
    "http://localhost:4000/Server/10.png",
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
        <div className='zoom-in-container'>
          <p className='zoom-in-text'>Display Selected Timetable</p>
          <img src={tt} className='zoom-in-pic'/>
        </div>
        <GeneratedTimetable imageData={tt} setSelectedImg={setSelectedImg}/>
        {generationDone && !generationError ? imagesData.map(imageData => {
          return <GeneratedTimetable imageData={imageData} setSelectedImg={setSelectedImg}/>
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