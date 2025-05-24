import React from 'react';
import './Header.css';
import logo from './assets/MWF_logo.png';

function Header({setBody}) {
  return (
    <div className='header'>
      <img src={logo} className='logo'></img>
      <div className='session-id'>
        <p className='bold'>
          Session ID:
        </p>
      </div>
      <div className='header-buttons'>
        <button className='session'>New Session</button>
        <button className='session'>Join Session</button>
      </div>
    </div>
  )
}

export default Header;