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
import { useStateContext } from './Context';

function Preference({username, setGenerationDone, setGenerationError, setImagesData,
  semesterTwo, body}) {

  const preferenceChangedRef = useRef(false);
  const intervalRef = useRef(null);

  const dropDownRef = useRef();
  const searchBarRef = useRef();
  const startTimeRef = useRef();
  const endTimeRef = useRef();
  const lunchStartRef = useRef();
  const lunchEndRef = useRef();
  const durationRef = useRef();
  const cModRef = useRef();
  const cTypeRef = useRef();
  const cLessonRef = useRef();
  const oModRef = useRef();
  const oTypeRef = useRef();
  
  const {moduleData, setModuleData, selectedMods, setSelectedMods,
      days, setDays, lunchCheck, setLunchCheck, clickStartTime, setClickStartTime,
      clickEndTime, setClickEndTime, startTime, setStartTime, endTime, setEndTime,
      clickLunchStart, setClickLunchStart, clickLunchEnd, setClickLunchEnd, lunchStart,
      setLunchStart, lunchEnd, setLunchEnd, clickDuration, setClickDuration, duration, 
      setDuration, clickCMod, setClickCMod, CMod, setCMod, clickCType, setClickCType,
      CType, setCType, clickCLesson, setClickCLesson, CLesson, setCLesson, clickOMod,
      setClickOMod, OMod, setOMod, clickOType, setClickOType, OType, setOType,
      newSession, setNewSession, isPreference, setIsPreference} = useStateContext();

  const [searchValue, setSearchValue] = useState("");
  const [ac, setAc] = useState([]);
  const [createRoom, setCreateRoom] = useState(false);
  const [rooms, setRooms] = useState([])
  const [openNewRoomOverlay, setOpenNewRoomOverlay] = useState(false);
  //const [imagesData, setImagesData] = useState([]);
  
  const timeOptions = ['0800', '0900', '1000', '1100', '1200', '1300', 
    '1400', '1500', '1600', '1700', '1800', '1900', '2000', '2100', '2200'];

  const durationOptions = ['1HR', '2HR', '3HR'];

  const getModuleInfo = async (modCode) => {
    const encoded = encodeURIComponent(modCode);
    const response = await fetch(`https://modswithfriends.onrender.com/modInfo?modCode=${encoded}` )
    const data = await response.json();
    return data.modInfo;
  }

  const getURL = async (url) => {
    const encoded = encodeURIComponent(url);
    const response = await fetch(`https://modswithfriends.onrender.com/expand?url=${encoded}` )
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
    setClickCLesson(false);
    setClickCMod(false);
    setClickCType(false);
    setClickOMod(false);
    setClickOType(false);
  }

  useEffect(() => {
    if (moduleData.length === 0) {
      fetch(`https://modswithfriends.onrender.com/sem${semesterTwo ? '2' : '1'}_data`)
        .then(response => response.json())
        .then(data => {setModuleData(data["sem_data"])});
    }
  }, [moduleData]);

  const inputPreferences = (preferences) => {
    if (preferences === null || preferences === undefined || preferences["selectedMods"] === undefined || preferences["selectedMods"] === null) {
      return;
    } 
    setSelectedMods(preferences["selectedMods"]);
    setLunchCheck(preferences["lunchCheck"]);
    setLunchStart(preferences["lunchStart"]);
    setLunchEnd(preferences["lunchEnd"]);
    setStartTime(preferences["startTime"]);
    setEndTime(preferences["endTime"]);
    setDays(preferences["days"]);
    setDuration(preferences["duration"]);
  }

  useEffect(() =>{
    const get_preferences = async () => {await fetch("https://modswithfriends.onrender.com/get_preferences", {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        "name" : usernameReference.current,
        "session_id" : bodyReference.current,
      })
    }).then(response => response.json())
    .then(data => inputPreferences(data.preferences))};
    
    console.log(semesterTwo);
    const get_mod_data = async () => {fetch(`https://modswithfriends.onrender.com/sem${semesterTwo ? '2' : '1'}_data`)
      .then(response => response.json())
      .then(data => {setModuleData(data["sem_data"])});};

    if (newSession) {
      usernameReference.current = username;
      bodyReference.current = body;
      get_preferences();
      get_mod_data();
      setNewSession(false);
    }
  }, [newSession])

  useEffect(() => {
    function handleClickOutside(e) {
      const refs = [
        dropDownRef.current,
        startTimeRef.current,
        endTimeRef.current,
        lunchStartRef.current,
        lunchEndRef.current,
        durationRef.current,
        cModRef.current,
        cTypeRef.current,
        cLessonRef.current,
        oModRef.current,
        oTypeRef.current
      ];
    
      const clickedInsideAny = refs
        .filter(ref => ref)
        .some(ref => ref.contains(e.target));
    
      if (!clickedInsideAny) {
        setAc([]);
        setSearchValue("");
        closeAll();
      }
    }

    document.addEventListener("mousedown", handleClickOutside);

    const handleKeyDown = (e) => {
      if (e.key === "Escape" && searchBarRef.current === document.activeElement) {
        setSearchValue("");
        setAc([]);
      }
    };

    window.addEventListener("keydown", handleKeyDown);

    //getURL("https://shorten.nusmods.com?shortUrl=pfayfa")
    //.then( data => console.log(data))

    //getURL("https://nusmods.com/timetable/sem-2/share?CDE2000=TUT:A4&CDE2310=LEC:1,LAB:1&CDE3301=LEC:1,LAB:G10&CG2023=LEC:03,LAB:05&CG2271=LAB:02,LEC:01&CS3240=LEC:1,TUT:3&EE2026=TUT:05,LEC:01,LAB:03&EE4204=PLEC:01,PTUT:01&IE2141=TUT:09,LEC:2&ta=CDE2310(LAB:1),CG2271(LAB:02)")
    //.then(data => console.log(data))

    if (!intervalRef.current) {
      intervalRef.current = setInterval(() => {
        //console.log("10 seconds triggered");
        if (preferenceChangedRef.current) {
          savePreferenceToBackend();
          preferenceChangedRef.current = false;
          /*fetch("https://modswithfriends.onrender.com/get_preferences", {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              "name" : username,
              "session_id" : body,
            })
          }).then(response => response.json())
          .then(data => console.log(`Retrieved: ${JSON.stringify(data.preferences, null, 2)}`));*/
        }
      }, 10000)
    }

    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
      window.removeEventListener("keydown", handleKeyDown);
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      };
    }
  }, []);

  useEffect(() => {
    /*let updatedRooms = [];
    updatedRooms = selectedMods.map(mod => ({
      module : mod.moduleCode,
      users : [],
      isOriginal: true
    }));
    setRooms(updatedRooms);
    console.log(rooms);*/
    const getRooms = async () => {
      await fetch("https://modswithfriends.onrender.com/get_session_groups", {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          "session_id" : body,
        })
      }).then(request => request.json())
      .then(data => {
        //console.log(data["groups"]);
        let mods = selectedMods.map(mod => mod.moduleCode);
        Object.keys(data["groups"]).forEach(key => {
          if (!mods.includes(key)) {
            delete data["groups"][key];
          }
        });
        //console.log(data["groups"]);
        setRooms(data["groups"]);
      })
    }
    getRooms();
  }, [isPreference]);

  const autocomplete = (value) => {
    setSearchValue(value);
    //console.log(moduleData);
    if (value == "") {
      setAc([]);
    } else {
      let matches = [];
      //const matches = moduleData.filter(mod =>
      //  mod.moduleCode.toLowerCase().startsWith(value.toLowerCase())
      //);
      for (module of Object.keys(moduleData)) {
        if (module.toLowerCase().startsWith(value.toLowerCase())) {
          matches.push({'moduleCode': module, 'title': moduleData[module]['title']});
        }
      }
      setAc(matches);
    }
  }

  useEffect(() => {
    console.log(moduleData);
  }, [moduleData]);

  const findModule = (code) => {
    let modData = moduleData[code];
    let classes = {};
    for (const key of Object.keys(modData)) {
        if (key === 'title') {
          continue;
        }
        classes[key] = [];
        for (const number of Object.keys(modData[key])) {
          classes[key].push(number);
        }
    }

    return {'moduleCode': code, 'title': modData['title'], 'classes': classes};
  }

  const handleLink = async (e) => {
    const pastedText = e.clipboardData.getData('text');
    if(pastedText.includes("http")) {
      const url = await getURL(pastedText);
      if (url === undefined) {
        setSearchValue("");
        return;
      }
      console.log(url);
      const matches = [...url.matchAll(/([A-Z]{2,4}[0-9]{4}[A-Z]{0,2})/g)].map(m => m[1]);
      const counts = matches.reduce((acc, code) => {
        acc[code] = (acc[code] || 0) + 1;
        return acc;
      }, {});
      const uniqueOnce = matches.filter(code => counts[code] === 1);
      const pastedMods = Array.from(uniqueOnce).map(code => {
        console.log(code);
        const mod = findModule(code);
        if (!mod) {
          console.warn("No module found for code:", code);
        }
        return mod;
      });
      /*
      let appendMods = [];
      for (const mod of pastedMods) {
        let classes = {};
        let data = await getModuleInfo(mod.moduleCode);
        for (const semester of data["semesterData"]) {
          if (semester.semester === 1) {
            for (const lesson of semester.timetable) {
              const lessonType = lesson.lessonType;
              const classNo = lesson.classNo;

              if (!classes[lessonType]) {
                  classes[lessonType] = [];
              }
              classes[lessonType].push(classNo);
            }
          }
        }
        appendMods.push({...mod, 'classes': classes});
      }*/
      setSelectedMods(pastedMods);
    }
    setSearchValue("");
  }

  function get24hr(timeStr) {
    if (timeStr == null || timeStr == "") {
      return null;
    }
    return parseInt(timeStr[0]+timeStr[1], 10);
  }

  const dayMapping = {
    "Mon": 1,
    "Tues": 2,
    "Weds": 3,
    "Thurs": 4,
    "Fri": 5
  };

  const abbreviations = {
    "Lecture": "LEC",
    "Laboratory": "LAB",
    "Tutorial": "TUT",
    "Packaged Lecture": "PLEC",
    "Packaged Tutorial": "PTUT",
    "Sectional Teaching": "SEC",
    "Recitation": "REC",
    "Design Lecture": "DLEC",
    "Seminar-style Module Teaching": "SEM",
    "Tutorial Type 2": "TUT2",
    "Tutorial Type 3": "TUT3",
    "Workshop": "WS",
  }

  const preferencesToJson = () => {
    let mods = selectedMods.map(mod => mod.moduleCode);
    let st = startTime === "" ? null : get24hr(startTime)*60;
    //console.log(`Start time = ${startTime}, Converted = ${st}`);
    let et = endTime === "" ? null : get24hr(endTime)*60;
    let lw = null;
    let ld = null;
    if (lunchCheck) {
      lw = st !== null && et !== null ? [get24hr(lunchStart)*60, get24hr(lunchEnd)*60] : null;
      ld = parseInt(duration[0], 10)*60;
    }
    const noClass = days
      .filter(day => day.selected)
      .map(day => dayMapping[day.day]);

    const optionalClass = selectedMods.reduce((acc, mod) => {
      if (mod.optional && mod.optional.length > 0) {
        const abbreviatedOptional = mod.optional.map(option => abbreviations[option]);
        acc[mod.moduleCode] = abbreviatedOptional;
      }
      return acc;
    }, {});

    const compulsoryClasses = selectedMods.reduce((acc, mod) => {
      if (mod.fixed && mod.fixed.length > 0) {
        const compulsoryData = mod.fixed.reduce((innerAcc, item) => {
          const classType = Object.keys(item)[0];
          const value = item[classType];
          const abbreviatedClass = abbreviations[classType];
          innerAcc[abbreviatedClass] = value;
          return innerAcc;
        }, {});
        acc[mod.moduleCode] = compulsoryData;
      }
      return acc;
    }, {});

    const jsonContent = JSON.stringify({
        modules: mods,
        semester: semesterTwo ? "2" : "1",
        earliest_start: st,
        latest_end: et,
        lunch_window: lw,
        lunch_duration: ld,
        days_without_lunch: [],
        days_without_class: noClass,
        optional_classes: optionalClass,
        compulsory_classes: compulsoryClasses,
        enable_lunch_break: lunchCheck,
      });
    return jsonContent;
  }

  const requestGeneration = async () => {
    setGenerationDone(false);
    setGenerationError(false);
    
    const jsonContent = preferencesToJson();
    //console.log(jsonContent);

    await fetch('https://modswithfriends.onrender.com//generate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: jsonContent
    }).then(response => {
      //console.log(`Status Returned: ${response.status}`);
      if (response.status === 500) {
        setGenerationError(true);  
      } 
      //setImagesData(data['images_data']);
      return response.json();
    }).then(({images_urls}) => {
      return Promise.all(
        images_urls.map(url => {
          return fetch(`https://modswithfriends.onrender.com/${url}`).then(res => res.blob()).then(blob => URL.createObjectURL(blob))
        })
      )
    }).then(setImagesData)
    .catch(console.error);
    setGenerationDone(true);
    console.log("Done generating");
  }

  const savePreferenceToBackend = async () => {
    console.log(JSON.stringify({
        "session_id" : bodyReference.current,
        "name" : usernameReference.current,
        "preferences" : {
          "selectedMods" : selectedModsReference.current,
          "lunchCheck" : lunchCheckReference.current,
          "lunchStart" : lunchStartReference.current,
          "lunchEnd" : lunchEndReference.current,
          "startTime" : startTimeReference.current,
          "endTime" : endTimeReference.current,
          "days" : daysReference.current,
          "duration" : durationReference.current,
        },
      }));
    await fetch('https://modswithfriends.onrender.com/save_preferences', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        "session_id" : bodyReference.current,
        "name" : usernameReference.current,
        "preferences" : {
          "selectedMods" : selectedModsReference.current,
          "lunchCheck" : lunchCheckReference.current,
          "lunchStart" : lunchStartReference.current,
          "lunchEnd" : lunchEndReference.current,
          "startTime" : startTimeReference.current,
          "endTime" : endTimeReference.current,
          "days" : daysReference.current,
          "duration" : durationReference.current,
        },
      }),
    });
  };

  const selectedModsReference = useRef(selectedMods);
  const lunchCheckReference = useRef(lunchCheck);
  const lunchStartReference = useRef(lunchStart);
  const lunchEndReference = useRef(lunchEnd);
  const startTimeReference = useRef(startTime);
  const endTimeReference = useRef(endTime);
  const daysReference = useRef(days);
  const durationReference = useRef(duration);
  const usernameReference = useRef(username);
  const bodyReference = useRef(body);

  useEffect(() => {
    // save preference
    selectedModsReference.current = selectedMods;
    lunchCheckReference.current = lunchCheck;
    lunchStartReference.current = lunchStart;
    lunchEndReference.current = lunchEnd;
    startTimeReference.current = startTime;
    endTimeReference.current = endTime;
    daysReference.current = days;
    durationReference.current = duration;
    preferenceChangedRef.current = true;
  }, [selectedMods, lunchCheck, lunchStart, lunchEnd, startTime, endTime, days, duration]);

  const addFixedMod = () => {
    if (CLesson === "") return;
    setSelectedMods(prevSelectedMods => 
      prevSelectedMods.map(mod => {
        if (mod.moduleCode === CMod) {
          if (!mod['fixed']) {
            mod['fixed'] = [];
          }
          const fixedIndex = mod['fixed'].findIndex(fixedMod => Object.keys(fixedMod)[0] === CType);

          if (fixedIndex !== -1) {
            mod['fixed'][fixedIndex] = {[CType]: CLesson};
          } else {
            mod['fixed'].push({[CType]: CLesson});
          }
          return {
            ...mod,
            'fixed': [...mod['fixed']]
          };
        }
        return mod;
      })
    );
    //console.log(selectedMods);
    setCMod("");
    setCType("");
    setCLesson("");
  }

  const addOptionalMod = () => {
    if (OType === "") return;
    setSelectedMods(prevSelectedMods => 
      prevSelectedMods.map(mod => {
        if (mod.moduleCode === OMod) {
          if (!mod['optional']) {
            mod['optional'] = [];
          }
          if (!mod['optional'].includes(OType)) {
            mod['optional'].push(OType);
          }
        }
        return mod;
      })
    )
    setOMod("");
    setOType("");
    //console.log(selectedMods);
  }
  
  const clearMods = () => {
    setSelectedMods([]);
  }

  const focusInput = () => {
    searchBarRef.current?.focus();
  }

  useEffect (() => {
    console.log(selectedMods);
  }, [selectedMods])

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
                onPaste={e => handleLink(e)} ref={searchBarRef}></input>
              <div className={ac.length != 0 ? 'dropdown' : 'invisible dropdown'}>
                {ac.map(mod => {
                  return <DropdownItem mod={mod} selectedMods={selectedMods} setSelectedMods={setSelectedMods} focusInput={focusInput} body={body} moduleData={moduleData}/>
                })}
              </div>
            </div>
          </div>
          {selectedMods.length === 0 ? <></> : 
          <div className='mod-modification'>
            <div className='compulsary-mods-container'>
              <p className='fm'>Preallocated / Decided classes: </p>
              <div className='longer-dd select-time' ref={cModRef} onClick={() => {closeAll(); setClickCMod(!clickCMod);}}>
                {clickCMod ? <div className='extend-dd time-dd dropdown'>
                  {(selectedMods).map(mod => {
                    return (
                      <div className='time-container' onClick={() => {setCMod(mod["moduleCode"]); setCType(""); setCLesson("");}}>
                        <p className='time'>{mod["moduleCode"]}</p>
                      </div>
                    )
                  })}     
                </div> : <></>}
                <p className={CMod === "" && !clickCMod ? 'placeholder time' : 'time'}> {CMod === "" && !clickCMod ? "Select Module" : CMod} </p>
                <img className='dd' src={dropdown} />
              </div>
              <div className='longer-dd select-time' ref={cTypeRef} onClick={() => {closeAll(); setClickCType(!clickCType);}}>
                {clickCType ? <div className='extend-dd time-dd dropdown'>
                  {selectedMods.map(module => {
                    if (module.moduleCode === CMod) {
                      return Object.keys(module["classes"]).map(type => {
                        return (
                          <div className='time-container' onClick={() => {setCType(type); setCLesson("")}}>
                            <p className='time'>{type}</p>
                          </div>
                        )
                      })
                    }
                  })}    
                </div> : <></>}
                <p className={CType === "" && !clickCType ? 'placeholder time' : 'time'}> {CType === "" && !clickCType ? "Select Lesson Type" : CType} </p>
                <img className='dd' src={dropdown} />
              </div>
              <div className='longer-dd select-time' ref={cLessonRef} onClick={() => {closeAll(); setClickCLesson(!clickCLesson);}}>
                {clickCLesson ? <div className='extend-dd time-dd dropdown'>
                  {selectedMods.map(module => {
                    if (module.moduleCode === CMod) {
                      return module["classes"][CType].map(lesson => {
                        return (
                          <div className='time-container' onClick={() => setCLesson(lesson)}>
                            <p className='time'>{lesson}</p>
                          </div>
                        )
                      })
                    }
                  })}     
                </div> : <></>}
                <p className={CLesson === "" && !clickCLesson ? 'placeholder time' : 'time'}> {CLesson === "" && !clickCLesson ? "Select Class No." : CLesson} </p>
                <img className='dd' src={dropdown} />
              </div>
              <div className={CLesson === "" ? 'unclickable add-item-container' : 'add-item-container'} onClick={() => addFixedMod()}>
                <p className='add'>Add Constraint</p>
              </div>
            </div>
            <div className='optional-mods-container'>
              <p className='om'>Classes you are skipping: </p>
              <div className='longer-dd select-time' ref={oModRef} onClick={() => {closeAll(); setClickOMod(!clickOMod);}}>
                {clickOMod ? <div className='extend-dd time-dd dropdown'>
                  {selectedMods.map(mod => {
                    return (
                      <div className='time-container' onClick={() => {setOMod(mod["moduleCode"]); setOType("");}}>
                        <p className='time'>{mod["moduleCode"]}</p>
                      </div>
                    )
                  })}     
                </div> : <></>}
                <p className={OMod === "" && !clickOMod ? 'placeholder time' : 'time'}> {OMod === "" && !clickOMod ? "Select Module" : OMod} </p>
                <img className='dd' src={dropdown} />
              </div>
              <div className='longer-dd select-time' ref={oTypeRef} onClick={() => {closeAll(); setClickOType(!clickOType);}}>
                {clickOType ? <div className='extend-dd time-dd dropdown'>
                  {selectedMods.map(module => {
                    if (module.moduleCode === OMod) {
                      return Object.keys(module["classes"]).map(type => {
                        return (
                          <div className='time-container' onClick={() => setOType(type)}>
                            <p className='time'>{type}</p>
                          </div>
                        )
                      })
                    }
                  })}     
                </div> : <></>}
                <p className={OType === "" && !clickOType ? 'placeholder time' : 'time'}> {OType === "" && !clickOType ? "Select Lesson Type" : OType} </p>
                <img className='dd' src={dropdown} />
              </div>
              <div className={OType === "" ? 'unclickable add-item-container' : 'add-item-container'} onClick={() => addOptionalMod()}>
                <p className='add'>Add Constraint</p>
              </div>
            </div> 
          </div>}
          {selectedMods.length === 0 ? <></> : <div className='clear-mods-container'>
            <div className='position-right add-item-container' onClick={() => clearMods()}>
              <p className='add'>Clear All Mods</p>
            </div>
          </div>}
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
            <input className='lo-checkbox' type="checkbox" checked={lunchCheck} onClick={() => {setLunchCheck(!lunchCheck)}}></input>
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
        <div className={Object.keys(rooms).length === 0 ? 'rooms-body': 'pad-top rooms-body'}>
          <div className='right-justified'>
            <button className='dark button' onClick={() => setOpenNewRoomOverlay(true)}>Create Room</button> 
          </div>
          { Object.keys(rooms).length === 0 ? 
          <div className='center-flex'>
            <p className='no-room-msg'>There are currently no rooms you can join</p> 
          </div>  :
          Object.entries(rooms).map(([moduleCode, roomList]) => {
            return Object.entries(roomList).map(([roomID, userList]) => (
              <RoomCard moduleCode ={moduleCode} roomID={roomID} userList={userList} 
              user={username} setRooms={setRooms} body={body}/>
            ))
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
        </div> }
      </div>
      <div className='generate-button-wrapper'>
        <div className='generate-button-container'>
          <Link to='/generate' className='link'>
            <button className='button' onClick={async () => await requestGeneration()}>Generate</button>
          </Link>
        </div>
      </div>
      {openNewRoomOverlay ? 
      <NewRoomOverlay setCreateRoom={setOpenNewRoomOverlay} selectedMods={selectedMods} setRooms={setRooms} username={username} body={body}/> : <></>}
    </div>
  )
}

export default Preference;