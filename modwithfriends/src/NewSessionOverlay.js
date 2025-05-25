import React from 'react';
import './NewSessionOverlay.css';
import x from './assets/x.png';

function NewSessionOverlay({setBody, setCreateSession}) {

  const generateID = () => {
    //replace with generation of id 
    setBody('000001');
    setCreateSession(false);
  }

  const closeOverlay = () => {
    setCreateSession(false);
  }

  return (
    <div className='dim'>
      <div className='overlay'>
        <div className='close'>
          <img src={x} className='x' onClick={closeOverlay}></img>
        </div>
        <div className='form'>
          <p className='session-type'>Session ID: </p>
        </div>
        <div className='form'>
          <p className='fill'>Name</p>
          <input className='input'></input>
        </div>
        <div className='form'>
          <p className='fill'>Password</p>
          <input className='input'></input>
        </div>
        <div className='create-session'>
          <button className='create-session' onClick={generateID}>Create Session</button>
        </div>
      </div>
    </div>
  )
}

export default NewSessionOverlay;