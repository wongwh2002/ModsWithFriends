import React from 'react';
import Header from './Header';
import NewSessionOverlay from './NewSessionOverlay';
import Generated from './Generated';
import ShareSessionOverlay from './ShareSessionOverlay';
import JoinSessionOverlay from './JoinSessionOverlay';

function GeneratePage({createSession, setCreateSession, joinSession, setJoinSession, 
  shareSession, setShareSession, body, setBody, username, setUsername}) {
  return (
    <div>
      <Header setCreateSession={setCreateSession} setJoinSession={setJoinSession} setShareSession={setShareSession} setBody={setBody} body={body}/>
      <Generated />
      {createSession ? <NewSessionOverlay setBody={setBody} setCreateSession={setCreateSession}/>
      : <></>}
      {joinSession ? <JoinSessionOverlay setBody={setBody} setJoinSession={setJoinSession}/>
      : <></>}
      {shareSession ? <ShareSessionOverlay setShareSession={setShareSession}/>
      : <></>}
    </div>
  )
}

export default GeneratePage;