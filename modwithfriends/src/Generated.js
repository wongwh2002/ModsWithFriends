import React from 'react';
import {useEffect} from 'react';
import './Generated.css'
import GeneratedTimetable from './GeneratedTimetable';

function Generated({generationDone, generationError, imagesData}) {

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