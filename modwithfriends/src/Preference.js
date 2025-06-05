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
  const [startTime, setStartTime] = useState("");
  const [endTime, setEndTime] = useState("");
  
  const timeOptions = ['8:00AM', '9:00AM', '10:00AM', '11:00AM', '12:00PM', '1:00PM', 
    '2:00PM', '3:00PM', '4:00PM', '5:00PM', '6:00PM'];

  useEffect(() => {
    fetch('/modules.json')
      .then(response => response.json())
      .then(data => setModuleData(data));

    function handleClickOutside(e) {
      if (dropDownRef.current && !dropDownRef.current.contains(e.target)) {
        setAc([]);
        setSearchValue("");
      }
    }

    document.addEventListener("mousedown", handleClickOutside);

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
  
  return (
    <div className='preference-overall'>
      <div className='preference-wrapper'>
        <div className='preference-body'>
          <p className='title text'>Preference</p>
          <div className='add-modules'>
            <p className='module text'>Modules: </p>
            <div className='dropdown-container' ref={dropDownRef}>
              <input className='search-module' value={searchValue} onChange={(e) => autocomplete(e.target.value)}></input>
              <div className={ac.length != 0 ? 'dropdown' : 'invisible dropdown'}>
                {ac.map(mod => {
                  return <DropdownItem mod={mod} selectedMods={selectedMods} setSelectedMods={setSelectedMods} />
                })}
              </div>
            </div>
            {selectedMods.map(selectedMod => {
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
            <div className='select-time' onClick={() => {setClickStartTime(!clickStartTime); setClickEndTime(false)}}>
              {clickStartTime ? <div className='time-dd dropdown'>
                {timeOptions.map(time => {
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
            <div className='select-time' onClick={() => {setClickEndTime(!clickEndTime); setClickStartTime(false)}}>
              {clickEndTime ? <div className='time-dd dropdown'>
                {timeOptions.map(time => {
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
          {lunchCheck ?
          <div className='lunch-timing flex-row'>
            <p className='lt'>Prefered lunch timing: </p>
          </div> : <></>}
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