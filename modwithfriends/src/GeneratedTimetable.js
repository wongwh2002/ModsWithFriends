import React, { useEffect, useState } from 'react';
import './GeneratedTimetable.css';

function GeneratedTimetable({imageData}) {
  return (
    <div className='gt-container'>
      <img src={imageData} className='gt-pic'/>
    </div>
  )
}

export default GeneratedTimetable;