import React from 'react';
import Header from './Header';
import Preference from './Preference';
import NewSessionOverlay from './NewSessionOverlay';
import JoinSessionOverlay from './JoinSessionOverlay';

function SessionPage({createSession, setCreateSession, joinSession, setJoinSession, body, setBody}) {
  return (
    <div>
      <Header setCreateSession={setCreateSession} setJoinSession={setJoinSession} body={body}/>
      <Preference />
      {createSession ? <NewSessionOverlay setBody={setBody} setCreateSession={setCreateSession}/>
      : <></>}
      {joinSession ? <JoinSessionOverlay setBody={setBody} setJoinSession={setJoinSession}/>
      : <></>}
    </div>
  )
}

export default SessionPage;