import React from 'react';
import { useEffect } from 'react';
import './SelectedMods.css';
import bin from './assets/bin.png';

function SelectedMods({selectedMod, setSelectedMods}) {

  const removeMod = () => {
    setSelectedMods(selectedMods => selectedMods.filter(mod => mod != selectedMod));
  }

  const removeFixedMod = (key) => {
    setSelectedMods(selectedMods => 
      selectedMods.map(mod => {
        if (mod === selectedMod) {
          console.log(selectedMod);
            const updatedFixed = mod.fixed.map(fixed => {
              const updatedFixedItem = { ...fixed };
              delete updatedFixedItem[key];

              return updatedFixedItem; 
            }); 

          return {
            ...mod,
            fixed: updatedFixed
          };
        }
        return mod;
      })
    )
  }

  const removeOptionalMod = (optional) => {
    setSelectedMods(selectedMods => {
      return selectedMods.map(mod => {
        if (mod === selectedMod) {
          const updatedOptional = mod['optional'].filter(opMod => opMod != optional);
          return {...mod, 'optional': updatedOptional};
        }
        return mod;
      })
    })
  }

  return (
    <div className='selected-mods-container'>
      <p className='mod-name'>{selectedMod["moduleCode"]}</p>
      <p className='mod-description'>{selectedMod["title"]}</p>
      {selectedMod["fixed"] ?
        selectedMod["fixed"].map( fixedType => {
          return (
            Object.entries(fixedType).map(([key, value]) => (
              <p className='mod-config' onClick={() => removeFixedMod(key)}>Fixed {key.substring(0,3)} {value}</p>
            ))
          )
        }
      ): <></>}
      {selectedMod['optional'] ? 
        selectedMod['optional'].map(optionalMod => {
          return (
            <p className='mod-config' onClick={() => removeOptionalMod(optionalMod)}>Optional {optionalMod.substring(0,3)}</p>
          )
        }) : <></>
      }
      <div className='add-padd'></div>
      <div className='bin-container' onClick={removeMod}>
        <img className='bin' src={bin} />
      </div>
    </div>
  )
}

export default SelectedMods;