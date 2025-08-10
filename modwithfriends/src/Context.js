import React, { createContext, useState, useContext, useEffect } from 'react';

const StateContext = createContext();

export const useStateContext = () => useContext(StateContext);

export const StateProvider = ({ children }) => {
  const [moduleData, setModuleData] = useState({});
  const [selectedMods, setSelectedMods] = useState([]);
  const [days, setDays] = useState([
    {"day":"Mon", "selected":false}, 
    {"day":"Tues", "selected":false},
    {"day":"Weds", "selected":false}, 
    {"day":"Thurs", "selected":false}, 
    {"day":"Fri", "selected":false}]);
  const [lunchCheck, setLunchCheck] = useState(false);
  const [clickStartTime, setClickStartTime] = useState(false);
  const [clickEndTime, setClickEndTime] = useState(false);
  const [startTime, setStartTime] = useState("");
  const [endTime, setEndTime] = useState("");
  const [clickLunchStart, setClickLunchStart] = useState(false);
  const [clickLunchEnd, setClickLunchEnd] = useState(false);
  const [lunchStart, setLunchStart] = useState("");
  const [lunchEnd, setLunchEnd] = useState("");
  const [clickDuration, setClickDuration] = useState(false);
  const [duration, setDuration] = useState("");
  const [clickCMod, setClickCMod] = useState(false);
  const [CMod, setCMod] = useState("");
  const [clickCType, setClickCType] = useState(false);
  const [CType, setCType] = useState("");
  const [clickCLesson, setClickCLesson] = useState(false);
  const [CLesson, setCLesson] = useState("");
  const [clickOMod, setClickOMod] = useState(false);
  const [OMod, setOMod] = useState("");
  const [clickOType, setClickOType] = useState(false);
  const [OType, setOType] = useState("");
  const [newSession, setNewSession] = useState(false);
  const [isPreference, setIsPreference] = useState(true);

  const resetStates = () => {
    setModuleData({});
    setSelectedMods([]);
    setDays([
    {"day":"Mon", "selected":false}, 
    {"day":"Tues", "selected":false},
    {"day":"Weds", "selected":false}, 
    {"day":"Thurs", "selected":false}, 
    {"day":"Fri", "selected":false}]);
    setLunchCheck(false);
    setClickStartTime(false);
    setClickEndTime(false);
    setStartTime("");
    setEndTime("");
    setClickLunchStart(false);
    setClickLunchEnd(false);
    setLunchStart("");
    setLunchEnd("");
    setClickDuration(false);
    setDuration("");
    setClickCMod(false);
    setCMod("");
    setClickCType(false);
    setCType("");
    setClickCLesson(false);
    setCLesson("");
    setClickOMod(false);
    setOMod("");
    setClickOType(false);
    setOType("");
    setNewSession(true);
    setIsPreference(true);
  }

  return (
    <StateContext.Provider value={{moduleData, setModuleData, selectedMods, setSelectedMods,
      days, setDays, lunchCheck, setLunchCheck, clickStartTime, setClickStartTime,
      clickEndTime, setClickEndTime, startTime, setStartTime, endTime, setEndTime,
      clickLunchStart, setClickLunchStart, clickLunchEnd, setClickLunchEnd, lunchStart,
      setLunchStart, lunchEnd, setLunchEnd, clickDuration, setClickDuration, duration, 
      setDuration, clickCMod, setClickCMod, CMod, setCMod, clickCType, setClickCType,
      CType, setCType, clickCLesson, setClickCLesson, CLesson, setCLesson, clickOMod,
      setClickOMod, OMod, setOMod, clickOType, setClickOType, OType, setOType, resetStates, 
      newSession, setNewSession, isPreference, setIsPreference}}>
        {children}
      </StateContext.Provider>
  )
}