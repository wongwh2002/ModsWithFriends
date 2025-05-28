import React from 'react';
import './Days.css';

function Days({day, setDays}) {
  
  const toggle = () => {
    setDays(days =>
      days.map(listDay =>
        listDay == day ? {...listDay, "selected": !listDay["selected"]} : listDay
      )
    )
  }
  
  return (
    <div className={day["selected"] ? 'selected days-container' : 'days-container'} onClick={toggle}>
      <p className='day'>{day["day"]}</p>
    </div>
  )
}

export default Days;