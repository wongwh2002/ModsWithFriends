import React from 'react';
import {useState, useEffect} from 'react';
import { useNavigate, useLocation } from "react-router-dom";
import './Overlay.css';
import x from './assets/x.png';
import { useStateContext } from './Context';

function JoinSessionOverlay({setJoinSession, body, setBody, setUsername}) {

  const navigate = useNavigate();
  const location = useLocation();
  
  const [sessionID, setSessionID] = useState("");
  const [name, setName] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  const { resetStates, setVerifiedURL, openFromHeader, setOpenFromHeader } = useStateContext();

  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const id = params.get("id");
    if (id && body !== id) {
      setSessionID(id);
    }
  }, []);

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
          semester_no: null,
        }),
        headers: {
          "Content-Type": "application/json; charset=UTF-8",
        },
      });

      if (response.ok) {
        setBody(sessionID);
        setUsername(name);
        resetStates();
        setVerifiedURL(true);
        setJoinSession(false);
        navigate(`/session?id=${sessionID}`);
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

  const handleKeyDown = (event) => {
    if (event.key === "Enter") {
      setLoading(true);
      generateID();
    }
  };

  const closeOverlay = () => {
    if (openFromHeader === false) {
      navigate('/');
    }
    setOpenFromHeader(false);
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
          <input className='input' value={sessionID} onChange={(e) => {setSessionID(e.target.value)}} onKeyDown={handleKeyDown}></input>
        </div>
        <div className='form'>
          <p className={name ? 'filled fill' : 'fill'}>Name</p>
          <input className='input' value={name} onChange={(e) => {setName(e.target.value)}} onKeyDown={handleKeyDown}></input>
        </div>
        <div className='form'>
          <p className={password ? 'filled fill' : 'fill'}>Password</p>
          <input className='input' type="password" value={password} onChange={(e) => {setPassword(e.target.value)}} onKeyDown={handleKeyDown}></input>
        </div>
        <div className='create-session'>
          <button className='create-session' onClick={generateID} disabled={loading}>{loading ? "Joining..." : "Join Session"}</button>
        </div>
      </div>
    </div>
  )
}

export default JoinSessionOverlay;