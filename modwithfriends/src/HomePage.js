import React from 'react';
import './HomePage.css';
import Header from './Header';
import Hero from './Hero'
import {useState} from 'react';
import NewSessionOverlay from './NewSessionOverlay';
import JoinSessionOverlay from './JoinSessionOverlay';
import Preference from './Preference';

function HomePage({body, setBody, createSession, setCreateSession, joinSession, setJoinSession, shareSession, setShareSession}) {

  return (
    <div className="background-color">
      <Header setCreateSession={setCreateSession} setJoinSession={setJoinSession} shareSession={shareSession} setShareSession={setShareSession} setBody={setBody} body={body}/>
      <Hero setCreateSession={setCreateSession}/>
      {createSession ? <NewSessionOverlay setBody={setBody} setCreateSession={setCreateSession}/>
      : <></>}
      {joinSession ? <JoinSessionOverlay setBody={setBody} setJoinSession={setJoinSession}/>
      : <></>}
    </div>
  )
}

export default HomePage;