import React from 'react';
import './Header.css';
import logo from './assets/MWF_logo.png';

function Header({setCreateSession, body}) {

  const createSession = () => {
    setCreateSession(true);
  }

  return (
    <div className='header'>
      <img src={logo} className='logo'></img>
      <div className='session-id'>
        <p className='bold'>
          Session ID: {body}
        </p>
      </div>
      <div className='header-buttons'>
        <button className='session' onClick={createSession}>New Session</button>
        <button className='session'>
          {body == '-' ?
          'Join Session'
          : 'Share Session'}
        </button>
      </div>
    </div>
  )
}

export default Header;