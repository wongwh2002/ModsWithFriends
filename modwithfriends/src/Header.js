import React from 'react';
import './Header.css';
import logo from './assets/MWF_logo.png';

function Header({setCreateSession, setJoinSession, body}) {

  const createSession = () => {
    setCreateSession(true);
  }

  const joinSession = () => {
    setJoinSession(true);
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
        {body == '-' ? <button className='session' onClick={joinSession}>Join Session</button>
        : <button className='session'>Share Session</button>}
      </div>
    </div>
  )
}

export default Header;