import React from 'react';
import './Preference.css';

function Preference() {
  return (
    <div className='preference-wrapper'>
      <div className='preference-body'>
        <p className='title'>Preference</p>
        <div className='add-modules'>
          <p className='module'>Modules: </p>
          <input className='search-module'></input>
        </div>
      </div>
    </div>
  )
}

export default Preference;