import React from 'react';
import {useState} from 'react';
import './Overlay.css';
import x from './assets/x.png';
import { Link } from 'react-router-dom';

function JoinSessionOverlay({setJoinSession, setBody}) {
  
  const [sessionID, setSessionID] = useState("");
  const [name, setName] = useState("");
  const [password, setPassword] = useState("");

  const generateID = () => {
    //replace with generation of id 
    setBody('000001');
    setJoinSession(false);
  }

  const closeOverlay = () => {
    setJoinSession(false);
  }

  return (
    <div className='dim'>
      <div className='overlay'>
        <div className='close'>
          <img src={x} className='x' onClick={closeOverlay}></img>
        </div>
        <div className='form'>
          <p className={sessionID ? 'filled fill' : 'fill'}>Session ID</p>
          <input className='input' value={sessionID} onChange={(e) => {setSessionID(e.target.value)}}></input>
        </div>
        <div className='form'>
          <p className={name ? 'filled fill' : 'fill'}>Name</p>
          <input className='input' value={name} onChange={(e) => {setName(e.target.value)}}></input>
        </div>
        <div className='form'>
          <p className={password ? 'filled fill' : 'fill'}>Password</p>
          <input className='input' value={password} onChange={(e) => {setPassword(e.target.value)}}></input>
        </div>
        <Link to='/session' className='link'> 
          <div className='create-session'>
            <button className='create-session' onClick={generateID}>Join Session</button>
          </div>
        </Link>
      </div>
    </div>
  )
}

export default JoinSessionOverlay;