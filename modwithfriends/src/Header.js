import React from 'react';
import './Header.css';
import { useNavigate } from "react-router-dom";
import logo from './assets/MWF_logo.png';
import { Link } from 'react-router-dom';
import { useStateContext } from './Context';

function Header({setCreateSession, setJoinSession, setShareSession, setBody, body}) {

  const { setOpenFromHeader } = useStateContext();

  const navigate = useNavigate();

  const createSession = () => {
    setCreateSession(true);
  }

  const joinSession = () => {
    setOpenFromHeader(true);
    setJoinSession(true);
  }

  const shareSession = () => {
    setShareSession(true);
  }

  const goToHome = () => {
    setBody('-');
    navigate('/');
  }

  return (
    <div className='header'>
      <img src={logo} className='logo' onClick={() => goToHome()}></img>
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