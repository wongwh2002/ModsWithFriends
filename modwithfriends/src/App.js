import './App.css';
import { BrowserRouter, Routes, Route } from "react-router-dom";
import HomePage from './HomePage';
import SessionPage from './SessionPage';
import { useState } from 'react';
import GeneratePage from './GeneratePage';

function App() {
  const [body, setBody] = useState('-');
  const [createSession, setCreateSession] = useState(false);
  const [joinSession, setJoinSession] = useState(false);
  const [shareSession, setShareSession] = useState(false);

  return (
    <BrowserRouter>
      <Routes>
        <Route path='/' element={<HomePage body={body} setBody={setBody} 
        createSession={createSession} setCreateSession={setCreateSession}
        joinSession={joinSession} setJoinSession={setJoinSession}
        shareSession={shareSession} setShareSession={setShareSession}/>} />
        <Route path='/session' element={<SessionPage createSession={createSession}
        setCreateSession={setCreateSession} joinSession={joinSession}
        setJoinSession={setJoinSession} shareSession={shareSession}
        setShareSession={setShareSession} body={body} setBody={setBody}/>} />
        <Route path='/generate' element={<GeneratePage createSession={createSession}
        setCreateSession={setCreateSession} joinSession={joinSession} 
        setJoinSession={setJoinSession} shareSession={shareSession}
        setShareSession={setShareSession} body={body} setBody={setBody}/>} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
