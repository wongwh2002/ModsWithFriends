import React from 'react';
import { useState } from 'react';
import './DropdownItem.css';

function DropdownItem({mod, selectedMods, setSelectedMods, focusInput, body, moduleData}) {

  const [loading, setLoading] = useState(false);

  const getModuleInfo = async (modCode) => {
    const encoded = encodeURIComponent(modCode);
    const response = await fetch(`https://modswithfriends.onrender.com/modInfo?modCode=${encoded}` )
    const data = await response.json();
    return data.modInfo;
  }

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
  
  const addSelectedMods = async () => {
    if (loading === true) {
      return;
    }
    if (!selectedMods.some(selectedMod => selectedMod["moduleCode"] == mod["moduleCode"])) {
      setLoading(true);
      let classes = {};
      /*
      let data = await getModuleInfo(mod.moduleCode);
      console.log(data);
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
      }*/
      
      const moduleToAdd = findModule(mod.moduleCode);

      setSelectedMods(selectedMods => [...selectedMods, moduleToAdd]);
      focusInput();
      setLoading(false);
      //console.log(selectedMods);
    }
  }

  return (
    <div className='dropdown-item-container' onClick={addSelectedMods}>
      <p className='text'>{`${mod["moduleCode"]} ${mod["title"]}`}</p>
    </div>
  )
}

export default DropdownItem;