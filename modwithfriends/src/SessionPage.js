import React from 'react';
import Header from './Header';
import Preference from './Preference';
import NewSessionOverlay from './NewSessionOverlay';
import ShareSessionOverlay from './ShareSessionOverlay';
import JoinSessionOverlay from './JoinSessionOverlay';

function SessionPage({createSession, setCreateSession, joinSession, setJoinSession, 
  shareSession, setShareSession, body, setBody, username, setUsername, 
  setGenerationDone, setGenerationError, setImagesData, semesterTwo, setSemesterTwo}) {
  return (
    <div>
      <Header setCreateSession={setCreateSession} setJoinSession={setJoinSession} 
      setShareSession={setShareSession} setBody={setBody} body={body}/>
      <Preference username={username} setGenerationDone={setGenerationDone} 
      setGenerationError={setGenerationError} setImagesData={setImagesData}
      semesterTwo={semesterTwo} body={body}/>
      {createSession ? <NewSessionOverlay setBody={setBody} 
      setCreateSession={setCreateSession} setUsername={setUsername}
      semseterTwo={semesterTwo} setSemesterTwo={setSemesterTwo}/>
      : <></>}
      {joinSession ? <JoinSessionOverlay setBody={setBody} setJoinSession={setJoinSession} setUsername={setUsername}/>
      : <></>}
      {shareSession ? <ShareSessionOverlay setShareSession={setShareSession}/>
      : <></>}
    </div>
  )
}

export default SessionPage;