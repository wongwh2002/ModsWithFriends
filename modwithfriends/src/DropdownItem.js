import React from 'react';
import './DropdownItem.css';

function DropdownItem({mod, selectedMods, setSelectedMods}) {

  const getModuleInfo = async (modCode) => {
    const encoded = encodeURIComponent(modCode);
    const response = await fetch(`http://localhost:4000/modInfo?modCode=${encoded}` )
    const data = await response.json();
    return data.modInfo;
  }
  
  const addSelectedMods = async () => {
    if (!selectedMods.some(selectedMod => selectedMod["moduleCode"] == mod["moduleCode"])) {
      let classes = {};
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
      }

      setSelectedMods(selectedMods => [...selectedMods, {...mod, 'classes': classes}]);
      console.log(selectedMods);
    }
  }

  return (
    <div className='dropdown-item-container' onClick={addSelectedMods}>
      <p className='text'>{`${mod["moduleCode"]} ${mod["title"]}`}</p>
    </div>
  )
}

export default DropdownItem;