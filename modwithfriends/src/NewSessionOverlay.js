import React from 'react';
import {useState} from 'react';
import './Overlay.css';
import x from './assets/x.png';
import { Link } from 'react-router-dom';

function NewSessionOverlay({setBody, setCreateSession, setUsername, semesterTwo, 
  setSemesterTwo}) {

  const [name, setName] = useState("");
  const [password, setPassword] = useState("");

  const generateID = async () => {
    await fetch("http://localhost:4000/get_new_session", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({})
    })
    .then(response => {
      if (!response.ok) {
        throw new Error("Failed to get session ID");
      }
      return response.text();
    })
    .then(sessionID => setBody(sessionID));
    setUsername(name);
    setCreateSession(false);
    fetch("http://localhost:4000/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({'name': name, 'password': password})
    });
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