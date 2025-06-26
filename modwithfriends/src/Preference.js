import React, { useRef } from 'react';
import {useState, useEffect} from 'react';
import './Preference.css';
import './DropdownItem';
import DropdownItem from './DropdownItem';
import SelectedMods from './SelectedMods';
import Days from './Days';
import dropdown from './assets/dropdown.png';
import { Link } from 'react-router-dom';
import NewRoomOverlay from './NewRoomOverlay';
import RoomCard from './RoomCard';
import e from 'cors';

function Preference({username, setGenerationDone, setGenerationError}) {

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
  const [createRoom, setCreateRoom] = useState(false);
  const [rooms, setRooms] = useState([])
  const [isPreference, setIsPreference] = useState(true);
  
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

  useEffect(() => {
    let updatedRooms = selectedMods.map(mod => ({
      module : mod.moduleCode,
      users : []
    }));
    setRooms(updatedRooms);
  }, [isPreference]);

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

  const findModule = (code) => {
    return moduleData.find(mod => mod.moduleCode === code)
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
      const pastedMods = Array.from(moduleCodes).map(code => findModule(code));
      setSelectedMods(pastedMods);
    }
    setSearchValue("");
  }

  function get24hr(timeStr) {
    const date = new Date("1970-01-01T" + timeStr);
    return date.getHours();
  }

  const requestGeneration = async () => {
    setGenerationDone(false);
    setGenerationError(false);
    let mods = selectedMods.map(mod => mod.moduleCode)
    let st = get24hr(startTime)*60
    let et = get24hr(endTime)*60
    let lw = (0,0)
    if (lunchCheck) {
      lw = (get24hr(lunchStart)*60, get24hr(lunchEnd)*60)
    }
    let ld = parseInt(duration[0], 10)*60
    let no_class = []

    fetch('http://127.0.0.1:4000/generate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        modules: mods,
        semester: 2,
        earliest_start: st,
        latest_end: et,
        lunch_window: lw,
        lunch_duration: ld,
        days_without_lunch: [],
        days_without_class: no_class,
        optional_classes: {},
        compulsory_classes: {},
        weights: {
          morning_class: 1,
          afternoon_class: 5,
          day_length_penalty: -0.01,
          day_present_penalty: -10,
        },
        enable_lunch_break: lunchCheck,
        enable_late_start: false,
        enable_early_end: false,
        enable_weights: true,
      })
    }).then(response => {
      //console.log(`Status Returned: ${response.status}`);
      if (response.status === 500) {
        setGenerationError(true);  
      }
      setGenerationDone(true);
      console.log("Done generating");
    })
  }
  
  return (
    <div className='preference-overall'>
      <div className='preference-wrapper'>
        <div className='tabs'>
          <div className={isPreference ? 'stranslate-1 square' : 'mask-dark stranslate-1 square'}></div>
          <div className='ctranslate-1 circle'></div>
          <div className='stranslate-2 square'></div>
          <div className={isPreference ? 'ctranslate-2 circle' : 'mask-dark ctranslate-1 circle'}></div>
          <div className='stranslate-3 square'></div>
          <div className={isPreference ? 'mask-light ctranslate-3 circle' : 'ctranslate-3 circle'}></div>
          <div className={isPreference ? 'mask-dark stranslate-4 square' : 'stranslate-4 square'}></div>
          <div className='ctranslate-4 circle'></div>
          <div className={isPreference? 'tab' : 'inactive tab'} onClick={() => setIsPreference(true)}>
            <p className='preference'>Preference</p>
          </div>
          <div className={isPreference ? 'inactive tab' : 'tab'} onClick={() => setIsPreference(false)}>
            <p className='rooms'>Rooms</p>
          </div>
        </div>
        {isPreference ? 
        <div className='preference-body'>
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
          </div>
          {selectedMods.length === 0 ? <></> :
          <div className='sm-container'>
            {selectedMods.map((selectedMod, index) => {
              return <SelectedMods selectedMod={selectedMod} setSelectedMods={setSelectedMods}/>
            })}
          </div>}
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
        </div> : 
        <div className={rooms.length === 0 ? 'rooms-body': 'pad-top rooms-body'}>
          { rooms.length === 0 ? <></> :
            rooms.map(room => {
              return <RoomCard roomInfo={room} />
            })
          }
          {/*{rooms.length === 0 ? 
          <button className='new-room-button button' onClick={() => setCreateRoom(true)}>
            Create New Room
          </button> : <></>}
          {rooms.map(room => {
            return (<RoomCard roomInfo={room} />)
          })}
          {rooms.length === 0 ? <></> : 
          <div className='circle-button' onClick={() => setCreateRoom(true)}>
            <p className='plus'>+</p>
          </div>}
          {createRoom ? <NewRoomOverlay setCreateRoom={setCreateRoom} selectedMods={selectedMods}
            setRooms={setRooms} username={username}/> : <></>}*/}
        </div>}
      </div>
      <div className='generate-button-wrapper'>
        <div className='generate-button-container'>
          <Link to='/generate' className='link'>
            <button className='button' onClick={async () => await requestGeneration()}>Generate</button>
          </Link>
        </div>
      </div>
    </div>
  )
}

export default Preference;