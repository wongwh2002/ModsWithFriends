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
  const [username, setUsername] = useState("");
  const [generationDone, setGenerationDone] = useState(true);
  const [generationError, setGenerationError] = useState(false);
  const [imagesData, setImagesData] = useState([]);
  const [semesterTwo, setSemesterTwo] = useState(false);

  return (
    <BrowserRouter>
      <Routes>
        <Route path='/' element={<HomePage body={body} setBody={setBody} 
        createSession={createSession} setCreateSession={setCreateSession}
        joinSession={joinSession} setJoinSession={setJoinSession}
        shareSession={shareSession} setShareSession={setShareSession}
        username={username} setUsername={setUsername} semesterTwo={semesterTwo}
        setSemesterTwo={setSemesterTwo}/>} />
        <Route path='/session' element={<SessionPage createSession={createSession}
        setCreateSession={setCreateSession} joinSession={joinSession}
        setJoinSession={setJoinSession} shareSession={shareSession}
        setShareSession={setShareSession} body={body} setBody={setBody}
        username={username} setUsername={setUsername} setGenerationDone={setGenerationDone}
        setGenerationError={setGenerationError} setImagesData={setImagesData}
        semesterTwo={semesterTwo} setSemesterTwo={setSemesterTwo}/>} />
        <Route path='/generate' element={<GeneratePage createSession={createSession}
        setCreateSession={setCreateSession} joinSession={joinSession} 
        setJoinSession={setJoinSession} shareSession={shareSession}
        setShareSession={setShareSession} body={body} setBody={setBody}
        username={username} setUsername={setUsername} generationDone={generationDone}
        generationError={generationError} imagesData={imagesData}
        semesterTwo={semesterTwo} setSemesterTwo={setSemesterTwo}/>} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
