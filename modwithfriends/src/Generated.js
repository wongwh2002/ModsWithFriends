import React from 'react';
import './Generated.css'
import GeneratedTimetable from './GeneratedTimetable';

function Generated() {

  const timetables = [1,2,3,4,5];

  return (
    <div className='generated-wrapper'>
      <div className='generated-container'>
        {timetables.map(timetable => {
          return <GeneratedTimetable/>
        })}
      </div>
    </div>
  )
}

export default Generated;