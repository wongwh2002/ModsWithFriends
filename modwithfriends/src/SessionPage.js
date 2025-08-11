import React, { useRef } from 'react';
import {useEffect, useState} from 'react';
import { useLocation, useNavigate } from "react-router-dom";
import Header from './Header';
import Preference from './Preference';
import NewSessionOverlay from './NewSessionOverlay';
import ShareSessionOverlay from './ShareSessionOverlay';
import JoinSessionOverlay from './JoinSessionOverlay';
import { useStateContext } from './Context';

function SessionPage({createSession, setCreateSession, joinSession, setJoinSession, 
  shareSession, setShareSession, body, setBody, username, setUsername, 
  setGenerationDone, setGenerationError, setImagesData, semesterTwo, setSemesterTwo}) {

  const navigate = useNavigate();
  const location = useLocation();
  const { verifiedURL, setVerifiedURL } = useStateContext();

  useEffect(() => {
    const verifySessionID = async (newSessionID) => {
      await fetch("https://modswithfriends.onrender.com/is_session_exist", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          session_id: newSessionID,
        })
      }).then(request => request.json())
      .then(data => {
        const sessionExist = data["status"];
        if(sessionExist === false) {
          navigate('/');
        } else {
          setJoinSession(true);  
        }
      })
    }
    if (verifiedURL === false) {
      const params = new URLSearchParams(location.search);
      const id = params.get("id");
      if (id) {
        verifySessionID(id);
      } else {
        navigate('/');
      }
    }
  }, [])
  
  return ( 
    <div>
      <Header setCreateSession={setCreateSession} setJoinSession={setJoinSession} 
      setShareSession={setShareSession} setBody={setBody} body={body}/>
      { verifiedURL === true ? <>
      <Preference username={username} setGenerationDone={setGenerationDone} 
      setGenerationError={setGenerationError} setImagesData={setImagesData}
      semesterTwo={semesterTwo} body={body}/> </> : <></>}
      {createSession ? <NewSessionOverlay setBody={setBody} 
      setCreateSession={setCreateSession} setUsername={setUsername}
      semseterTwo={semesterTwo} setSemesterTwo={setSemesterTwo}/>
      : <></>}
      {joinSession ? <JoinSessionOverlay body={body} setBody={setBody} setJoinSession={setJoinSession} setUsername={setUsername}/>
      : <></>}
      {shareSession ? <ShareSessionOverlay setShareSession={setShareSession}/>
      : <></>}
    </div>
  )
}

export default SessionPage;