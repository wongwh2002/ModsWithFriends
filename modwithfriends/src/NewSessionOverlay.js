import React from 'react';
import {useState} from 'react';
import './Overlay.css';
import x from './assets/x.png';
import { Link } from 'react-router-dom';

function NewSessionOverlay({setBody, setCreateSession, setUsername, semesterTwo, 
  setSemesterTwo}) {

  const [name, setName] = useState("");
  const [password, setPassword] = useState("");

  const generateID = () => {
    //replace with generation of id 
    setBody('000001');
    setUsername(name);
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
        <div className='flex-jb'>
          <div className='form'>
            <p className='session-type'>Session ID: </p>
          </div>
          <div className='switch-container'>
            <p className='sem'>Semester</p>
            <label class="switch" onChange={() => {setSemesterTwo(prev => !prev);}}>
              <input type="checkbox" checked={semesterTwo}/>
              <span class="slider"></span>
            </label>
          </div>
        </div>
        <div className='form'>
          <p className={name ? 'filled fill' : 'fill'}>Name</p>
          <input className='input' value={name} onChange={(e) => {setName(e.target.value)}}></input>
        </div>
        <div className='form'>
          <p className={password ? 'filled fill' : 'fill'}>Password</p>
          <input className='input' type="password" value={password} onChange={(e) => {setPassword(e.target.value)}}></input>
        </div>
        <Link to='/session' className='link'>
          <div className='create-session'>
            <button className='create-session' onClick={generateID}>Create Session</button>
          </div>
        </Link>
      </div>
    </div>
  )
}

export default NewSessionOverlay;