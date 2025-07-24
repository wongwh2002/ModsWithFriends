import React from 'react';
import './Header.css';
import logo from './assets/MWF_logo.png';
import { Link } from 'react-router-dom';

function Header({setCreateSession, setJoinSession, setShareSession, setBody, body}) {

  const createSession = () => {
    setCreateSession(true);
  }

  const joinSession = () => {
    setJoinSession(true);
  }

  const shareSession = () => {
    setShareSession(true);
  }

  return (
    <div className='header'>
      <Link to="/" onClick={() => setBody('-')}>
        <img src={logo} className='logo'></img>
      </Link>
      <div className='session-id'>
        <p className='bold'>
          Session ID: {body}
        </p>
      </div>
      <div className='header-buttons'>
        <button className='session' onClick={createSession}>New Session</button>
        <button className='session' onClick={joinSession}>Join Session</button>
        {body === '-' ? <></> : <button className='session' onClick={shareSession}>Share Session</button>}
      </div>
    </div>
  )
}

export default Header;