import React from 'react';
import './HomePage.css';
import Header from './Header';
import Hero from './Hero'
import {useState} from 'react';
import NewSessionOverlay from './NewSessionOverlay';
import JoinSessionOverlay from './JoinSessionOverlay';

function HomePage() {

  const [body, setBody] = useState('-');
  const [createSession, setCreateSession] = useState(false);
  const [joinSession, setJoinSession] = useState(false);

  return (
    <div className="background-color">
      <Header setCreateSession={setCreateSession} setJoinSession={setJoinSession} body={body}/>
      {body == '-' ? 
      <Hero setCreateSession={setCreateSession}/>
      : <></>}
      {createSession ? <NewSessionOverlay setBody={setBody} setCreateSession={setCreateSession}/>
      : <></>}
      {joinSession ? <JoinSessionOverlay setBody={setBody} setJoinSession={setJoinSession}/>
      : <></>}
    </div>
  )
}

export default HomePage;