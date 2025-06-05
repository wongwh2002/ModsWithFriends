import React from 'react';
import Header from './Header';
import NewSessionOverlay from './NewSessionOverlay';
import JoinSessionOverlay from './JoinSessionOverlay';
import Generated from './Generated';

function GeneratePage({createSession, setCreateSession, joinSession, setJoinSession, body, setBody}) {
  return (
    <div>
      <Header setCreateSession={setCreateSession} setJoinSession={setJoinSession} body={body}/>
      <Generated />
      {createSession ? <NewSessionOverlay setBody={setBody} setCreateSession={setCreateSession}/>
      : <></>}
      {joinSession ? <JoinSessionOverlay setBody={setBody} setJoinSession={setJoinSession}/>
      : <></>}
    </div>
  )
}

export default GeneratePage;