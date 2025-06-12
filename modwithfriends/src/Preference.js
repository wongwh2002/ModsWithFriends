import React, { useRef } from 'react';
import {useState, useEffect} from 'react';
import './Preference.css';
import './DropdownItem';
import DropdownItem from './DropdownItem';
import SelectedMods from './SelectedMods';
import Days from './Days';
import dropdown from './assets/dropdown.png';
import { Link } from 'react-router-dom';

function Preference() {

  const dropDownRef = useRef();
  const startTimeRef = useRef();
  const endTimeRef = useRef();
  const lunchStartRef = useRef();
  const lunchEndRef = useRef();
  const durationRef = useRef();
  
  const [searchValue, setSearchValue] = useState("");
  const [moduleData, setModuleData] = useState([]);
  const [ac, setAc] = useState([]);
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
  const [startTime, setStartTime] = useState(null);
  const [endTime, setEndTime] = useState(null);
  const [clickLunchStart, setClickLunchStart] = useState(false);
  const [clickLunchEnd, setClickLunchEnd] = useState(false);
  const [lunchStart, setLunchStart] = useState(null);
  const [lunchEnd, setLunchEnd] = useState(null);
  const [clickDuration, setClickDuration] = useState(false);
  const [duration, setDuration] = useState("");
  
  const timeOptions = ['8:00AM', '9:00AM', '10:00AM', '11:00AM', '12:00PM', '1:00PM', 
    '2:00PM', '3:00PM', '4:00PM', '5:00PM', '6:00PM'];

  const durationOptions = ['1HR', '2HR', '3HR'];

  const getURL = async (url) => {
    const encoded = encodeURIComponent(url);
    const response = await fetch(`http://localhost:4000/expand?url=${encoded}` )
    const data = await response.json();
    return data.expandedUrl;
  }

  const startTimeOptions = timeOptions.filter((time, index) => {
    if (endTime) {
      return index < timeOptions.indexOf(endTime);
    }
    return true;
  });

  const endTimeOptions = timeOptions.filter((time, index) => {
    if (startTime) {
      return index > timeOptions.indexOf(startTime);
    }
    return true;
  });

  const lunchStartOptions = timeOptions.filter((time, index) => {
    if (lunchEnd) {
      return index > timeOptions.indexOf(lunchEnd);
    }
    return true;
  });

  const lunchEndOptions = timeOptions.filter((time, index) => {
    if (lunchStart) {
      return index > timeOptions.indexOf(lunchStart);
    }
    return true;
  });

  const closeAll = () => {
    setClickEndTime(false);
    setClickStartTime(false);
    setClickLunchEnd(false);
    setClickLunchStart(false);
    setClickDuration(false);
  }

  useEffect(() => {
    fetch('/modules.json')
      .then(response => response.json())
      .then(data => setModuleData(data));

    function handleClickOutside(e) {
      const refs = [
        dropDownRef.current,
        startTimeRef.current,
        endTimeRef.current,
        lunchStartRef.current,
        lunchEndRef.current,
        durationRef.current
      ];
    
      const clickedInsideAny = refs
        .filter(ref => ref) // Remove null or unmounted refs
        .some(ref => ref.contains(e.target));
    
      if (!clickedInsideAny) {
        setAc([]);
        setSearchValue("");
        closeAll();
      }
    }

    document.addEventListener("mousedown", handleClickOutside);

    //getURL("https://shorten.nusmods.com?shortUrl=pfayfa")
    //.then( data => console.log(data))

    //getURL("https://nusmods.com/timetable/sem-2/share?CDE2000=TUT:A4&CDE2310=LEC:1,LAB:1&CDE3301=LEC:1,LAB:G10&CG2023=LEC:03,LAB:05&CG2271=LAB:02,LEC:01&CS3240=LEC:1,TUT:3&EE2026=TUT:05,LEC:01,LAB:03&EE4204=PLEC:01,PTUT:01&IE2141=TUT:09,LEC:2&ta=CDE2310(LAB:1),CG2271(LAB:02)")
    //.then(data => console.log(data))

    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    }
  }, []);

  const autocomplete = (value) => {
    setSearchValue(value);
    console.log(moduleData);
    if (value == "") {
      setAc([]);
    } else {
      setAc([])
      for (let i in moduleData) {
        if (moduleData[i]["moduleCode"].toLowerCase().startsWith(value.toLowerCase())) {
          setAc(ac => [...ac, moduleData[i]]);
        }
      }
    }
  }

  const handleLink = async (e) => {
    const pastedText = e.clipboardData.getData('text');
    if(pastedText.includes("http")) {
      const url = await getURL(pastedText);
      if (url === undefined) {
        setSearchValue("");
        return;
      }
      const matches = [...url.matchAll(/([A-Z]{2,4}[0-9]{4})/g)];
      const moduleCodes = new Set(matches.map(match => match[1]));
      const pastedMods = Array.from(moduleCodes).map(code => ({ moduleCode: code }));
      setSelectedMods(pastedMods);
    }
    setSearchValue("");
  }
  
  return (
    <div className='preference-overall'>
      <div className='preference-wrapper'>
        <div className='preference-body'>
          <p className='title text'>Preference</p>
          <div className='add-modules'>
            <p className='module text'>Modules: </p>
            <div className='dropdown-container' ref={dropDownRef}>
              <input className='search-module' placeholder='Search Module / Paste NUSMODS link' 
                value={searchValue} onChange={(e) => autocomplete(e.target.value)}
                onPaste={e => handleLink(e)}></input>
              <div className={ac.length != 0 ? 'dropdown' : 'invisible dropdown'}>
                {ac.map(mod => {
                  return <DropdownItem mod={mod} selectedMods={selectedMods} setSelectedMods={setSelectedMods} />
                })}
              </div>
            </div>
            {selectedMods.map((selectedMod, index) => {
              return <SelectedMods selectedMod={selectedMod} setSelectedMods={setSelectedMods}/>
            })}
          </div>
          <div className='attending-container flex-row'>
            <p className='dwm'>Days without modules: </p> 
            {days.map(day => {
              return <Days day={day} setDays={setDays} />
            })}
          </div>
          <div className='start-time flex-row'>
            <p className='st'>Earliest start class timing: </p>
            <div className='select-time' ref={startTimeRef} onClick={() => {closeAll(); setClickStartTime(!clickStartTime);}}>
              {clickStartTime ? <div className='time-dd dropdown'>
                {startTimeOptions.map(time => {
                  return (
                    <div className='time-container' onClick = {() => setStartTime(time)}>
                      <p className='time'>{time}</p>
                    </div>
                  )
                })}
              </div> : <></>}
              <p className='time'> {startTime} </p>
              <img className='dd' src={dropdown} />
            </div>
          </div>
          <div className='end-time flex-row'>
            <p className='et'>Lastest end class timing:</p>
            <div className='select-time' ref={endTimeRef} onClick={() => {closeAll(); setClickEndTime(!clickEndTime);}}>
              {clickEndTime ? <div className='time-dd dropdown'>
                {endTimeOptions.map(time => {
                  return (
                    <div className='time-container' onClick={() => setEndTime(time)}>
                      <p className='time'>{time}</p>
                    </div>
                  )
                })}     
              </div> : <></>}
              <p className='time'> {endTime} </p>
              <img className='dd' src={dropdown} />
            </div>
          </div>
          <div className='lunch-option flex-row'>
            <p className='lo'>Lunch?</p>
            <input className='lo-checkbox' type="checkbox" onClick={() => {setLunchCheck(!lunchCheck)}}></input>
          </div>
          {lunchCheck ? <>
          <div className='lunch-timing flex-row'>
            <p className='lt'>Prefered lunch timing: </p>
            <div className='select-time' ref={lunchStartRef} onClick={() => {closeAll(); setClickLunchStart(!clickLunchStart);}}>
              {clickLunchStart ? <div className='time-dd dropdown'>
                {lunchStartOptions.map(time => {
                  return (
                    <div className='time-container' onClick={() => setLunchStart(time)}>
                      <p className='time'>{time}</p>
                    </div>
                  )
                })}     
              </div> : <></>}
              <p className='time'> {lunchStart} </p>
              <img className='dd' src={dropdown} />
            </div>
            <p className='dash'>-</p>
            <div className='select-time' ref={lunchEndRef} onClick={() => {closeAll(); setClickLunchEnd(!clickLunchEnd);}}>
              {clickLunchEnd ? <div className='time-dd dropdown'>
                {lunchEndOptions.map(time => {
                  return (
                    <div className='time-container' onClick={() => setLunchEnd(time)}>
                      <p className='time'>{time}</p>
                    </div>
                  )
                })}     
              </div> : <></>}
              <p className='time'> {lunchEnd} </p>
              <img className='dd' src={dropdown} />
            </div>
          </div> 
          <div className="lunch-duration flex-row">
            <p className='duration'>Duration:</p>
            <div className='select-time' ref={durationRef} onClick={() => {closeAll(); setClickDuration(!clickDuration);}}>
              {clickDuration ? <div className='time-dd dropdown'>
                {durationOptions.map(duration => {
                  return (
                    <div className='time-container' onClick={() => setDuration(duration)}>
                      <p className='time'>{duration}</p>
                    </div>
                  )
                })}     
              </div> : <></>}
              <p className='time'> {duration} </p>
              <img className='dd' src={dropdown} />
            </div>
          </div> </> : <></>}
        </div>
      </div>
      <Link to='/generate' className='link'>
        <div className='generate-button-wrapper'>
          <div className='generate-button-container'>
            <button className='generate-button'>Generate</button>
          </div>
        </div>
      </Link>
    </div>
  )
}

export default Preference;