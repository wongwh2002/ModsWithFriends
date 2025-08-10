import React, { useEffect } from "react";
import { useState } from "react";
import "./Overlay.css";
import x from "./assets/x.png";
import { Link } from "react-router-dom";
import { useStateContext } from "./Context";

function NewSessionOverlay({
  setBody,
  setCreateSession,
  setUsername,
  semesterTwo,
  setSemesterTwo,
}) {
  const [name, setName] = useState("");
  const [password, setPassword] = useState("");
  const [newSessionID, setNewSessionID] = useState(0);
  const [loading, setLoading] = useState(false);

  const { resetStates } = useStateContext();

  useEffect(() => {
    const fetchNewSession = async () => {
      try {
        const response = await fetch("https://modswithfriends.onrender.com/get_new_session", {
          method: "GET",
        });

        const data = await response.json(); 

        if (response.ok) {
          setNewSessionID(data.new_id);
        } else {
          console.log(data.error);
        }
      } catch (error) {
        console.log("Error fetching new session:", error);
      }
    };
    fetchNewSession();
  }, []);

  const generateID = async () => {
    setLoading(true);
    //replace with generation of id
    resetStates();
    setBody(newSessionID);
    setUsername(name);
    setCreateSession(false);
    console.log("Creating session with name:");
    await fetch("https://modswithfriends.onrender.com/new_session", {
      method: "POST",
      body: JSON.stringify({
        session_id: newSessionID,
        name: name,
        password: password,
        semester_no: semesterTwo ? "2" : "1"
      }),
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({'name': name, 'password': password})
    });
    setLoading(false);
  }

  const closeOverlay = () => {
    setCreateSession(false);
  };

  return (
    <div className="dim">
      <div className="overlay">
        <div className="close">
          <img src={x} className="x" onClick={closeOverlay}></img>
        </div>
        <div className="flex-jb">
          <div className="form">
            <p className="session-type">Session ID: {newSessionID}</p>
          </div>
          <div className="switch-container">
            <p className="sem">Semester</p>
            <label
              class="switch"
              onChange={() => {
                setSemesterTwo((prev) => !prev);
              }}
            >
              <input type="checkbox" checked={semesterTwo} />
              <span class="slider"></span>
            </label>
          </div>
        </div>
        <div className="form">
          <p className={name ? "filled fill" : "fill"}>Name</p>
          <input
            className="input"
            value={name}
            onChange={(e) => {
              setName(e.target.value);
            }}
          ></input>
        </div>
        <div className="form">
          <p className={password ? "filled fill" : "fill"}>Password</p>
          <input
            className="input"
            type="password"
            value={password}
            onChange={(e) => {
              setPassword(e.target.value);
            }}
          ></input>
        </div>
        <Link to="/session" className="link">
          <div className="create-session">
            <button className="create-session" disbaled={loading} onClick={generateID}>
              { loading ? "Creating..." : "Create Session" }
            </button>
          </div>
        </Link>
      </div>
    </div>
  );
}

export default NewSessionOverlay;
