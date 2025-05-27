import React from 'react';
import {useState, useEffect} from 'react';
import './Preference.css';
import './DropdownItem';
import DropdownItem from './DropdownItem';
import SelectedMods from './SelectedMods';

function Preference() {
  
  const [searchValue, setSearchValue] = useState("");
  const [moduleData, setModuleData] = useState([]);
  const [ac, setAc] = useState([]);
  const [selectedMods, setSelectedMods] = useState([]);

  useEffect(() => {
    fetch('/modules.json')
      .then(response => response.json())
      .then(data => setModuleData(data));
  }, []);

  const autocomplete = (value) => {
    setSearchValue(value);
    console.log(moduleData);
    if (value == "") {
      setAc([]);
    } else {
      setAc([])
      for (let i in moduleData) {
        if (moduleData[i]["moduleCode"].toLowerCase().match(value.toLowerCase())) {
          setAc(ac => [...ac, moduleData[i]]);
        }
      }
    }
  }
  
  return (
    <div className='preference-wrapper'>
      <div className='preference-body'>
        <p className='title text'>Preference</p>
        <div className='add-modules'>
          <p className='module text'>Modules: </p>
          <div className='dropdown-container'>
            <input className='search-module' value={searchValue} onChange={(e) => autocomplete(e.target.value)}></input>
            <div className={ac.length != 0 ? 'dropdown' : 'invisible dropdown'}>
              {ac.map(mod => {
                return <DropdownItem mod={mod} setSelectedMods={setSelectedMods} />
              })}
            </div>
          </div>
          {selectedMods.map(selectedMod => {
            return <SelectedMods selectedMod={selectedMod} setSelectedMods={setSelectedMods}/>
          })}
        </div>
      </div>
    </div>
  )
}

export default Preference;