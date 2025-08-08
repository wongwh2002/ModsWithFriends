import React from 'react';
import {useState} from 'react';
import { useNavigate } from "react-router-dom";
import './Overlay.css';
import x from './assets/x.png';
import { useStateContext } from './Context';

function JoinSessionOverlay({setJoinSession, setBody, setUsername}) {

  const navigate = useNavigate();
  
  const [sessionID, setSessionID] = useState("");
  const [name, setName] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  const { resetStates } = useStateContext();

  const generateID = async () => {
    setLoading(true);
    //replace with generation of id 
    try {
      const response = await fetch("https://modswithfriends.onrender.com/join_session", {
        method: "POST",
        body: JSON.stringify({
          session_id: sessionID,
          name: name,
          password: password,
        }),
        headers: {
          "Content-Type": "application/json; charset=UTF-8",
        },
      });

      if (response.ok) {
        resetStates();
        setBody(sessionID);
        setUsername(name);
        setJoinSession(false);
        navigate('/session');
      } else {
        if (response.status === 400) {
          console.log("No such session");
          setSessionID("");
        } else if (response.status === 401) {
          console.log("Invalid login credentials");
          setName("");
          setPassword("");
        } else {
          console.log("Unknown error occurred:", response.status);
          setName("");
          setPassword("");
        }
      }
    } catch (error) {
      console.error("Network error:", error.message);
    } finally {
      setLoading(false);
    }
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
          <input className='input' type="password" value={password} onChange={(e) => {setPassword(e.target.value)}}></input>
        </div>
        <div className='create-session'>
          <button className='create-session' onClick={generateID} disabled={loading}>{loading ? "Joining..." : "Join Session"}</button>
        </div>
      </div>
    </div>
  )
}

export default JoinSessionOverlay;