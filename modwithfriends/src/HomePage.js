import React from 'react';
import './HomePage.css';
import Header from './Header';
import Hero from './Hero'
import {useState} from 'react';
import NewSessionOverlay from './NewSessionOverlay';

function HomePage() {

  const [body, setBody] = useState('-');
  const [createSession, setCreateSession] = useState(false);

  return (
    <div className="background-color">
      <Header setCreateSession={setCreateSession} body={body}/>
      {body == '-' ? 
      <Hero setCreateSession={setCreateSession}/>
      : <></>}
      {createSession ? <NewSessionOverlay setBody={setBody} setCreateSession={setCreateSession}/>
      : <></>}
    </div>
  )
}

export default HomePage;