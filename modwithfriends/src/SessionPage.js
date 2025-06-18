import React from 'react';
import Header from './Header';
import Preference from './Preference';
import NewSessionOverlay from './NewSessionOverlay';
import ShareSessionOverlay from './ShareSessionOverlay';
import JoinSessionOverlay from './JoinSessionOverlay';

function SessionPage({createSession, setCreateSession, joinSession, setJoinSession, 
  shareSession, setShareSession, body, setBody, username, setUsername}) {
  return (
    <div>
      <Header setCreateSession={setCreateSession} setJoinSession={setJoinSession} setShareSession={setShareSession} setBody={setBody} body={body}/>
      <Preference username={username}/>
      {createSession ? <NewSessionOverlay setBody={setBody} setCreateSession={setCreateSession}/>
      : <></>}
      {joinSession ? <JoinSessionOverlay setBody={setBody} setJoinSession={setJoinSession} setUsername={setUsername}/>
      : <></>}
      {shareSession ? <ShareSessionOverlay setShareSession={setShareSession} setUsername={setUsername}/>
      : <></>}
    </div>
  )
}

export default SessionPage;