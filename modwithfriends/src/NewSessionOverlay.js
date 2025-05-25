import React, { use } from 'react';
import {useState} from 'react';
import './NewSessionOverlay.css';
import x from './assets/x.png';

function NewSessionOverlay({setBody, setCreateSession}) {

  const [name, setName] = useState("");
  const [password, setPassword] = useState("");

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
          <p className={name ? 'filled fill' : 'fill'}>Name</p>
          <input className='input' value={name} onChange={(e) => {setName(e.target.value)}}></input>
        </div>
        <div className='form'>
          <p className={password ? 'filled fill' : 'fill'}>Password</p>
          <input className='input' value={password} onChange={(e) => {setPassword(e.target.value)}}></input>
        </div>
        <div className='create-session'>
          <button className='create-session' onClick={generateID}>Create Session</button>
        </div>
      </div>
    </div>
  )
}

export default NewSessionOverlay;