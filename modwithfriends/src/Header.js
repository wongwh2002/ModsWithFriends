import React, { useState } from 'react';
import './Header.css';
import { useNavigate } from "react-router-dom";
import logo from './assets/MWF_logo.png';
import clipboard from './assets/copy.png';
import { useStateContext } from './Context';

function Header({setCreateSession, setJoinSession, setShareSession, setBody, body}) {

  const { setOpenFromHeader } = useStateContext();
  const [copyDescription, setCopyDescription] = useState(false);
  const [copyMessage, setCopyMessage] = useState("Copy Share Link");

  const navigate = useNavigate();

  const createSession = () => {
    setCreateSession(true);
  }

  const joinSession = () => {
    setOpenFromHeader(true);
    setJoinSession(true);
  }

  const handleCopy = () => {
    setCopyMessage("Copied!");
    navigator.clipboard.writeText(window.location.href);
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
        <div className='copy-wrapper'>
          {body === '-' ? <></> : 
          <img src={clipboard} className='clipboard-icon' 
            onMouseEnter={() => setCopyDescription(true)} onMouseLeave={() => {setCopyDescription(false); setCopyMessage("Copy Share Link");}}
            onClick={handleCopy} />
          }
          {copyDescription ? 
          <div className='copy-description'>
            <p className='no-margin'>{copyMessage}</p>
          </div> : <></>
          }
        </div>
      </div>
      <div className='header-buttons'>
        <button className='session' onClick={createSession}>New Session</button>
        <button className='session' onClick={joinSession}>Join Session</button>
        {/*body === '-' ? <></> : <button className='session' onClick={shareSession}>Share Session</button>*/}
      </div>
    </div>
  )
}

export default Header;