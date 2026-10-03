import {ANIMAL_GROUPS, unknownAnimal, validateAnimal} from './animal-model.mjs';
export function animalPicker(document, prefix, changed = () => {}) {
  const get = suffix => document.getElementById(`${prefix}-animal-${suffix}`);
  const group = get('group'), species = get('species');
  group.replaceChildren(...ANIMAL_GROUPS.map(([id,label]) => {
    const option=document.createElement('option'); option.value=id; option.textContent=label; return option;
  }));
  function render() {
    const entry=ANIMAL_GROUPS.find(([id]) => id===group.value) || ANIMAL_GROUPS[0];
    get('summary').textContent=entry[1]; get('guidance').textContent=entry[2];
  }
  group.addEventListener('change',()=>{species.value='';render();changed();});
  species.addEventListener('input',changed);
  const picker={
    value(){return validateAnimal({group:group.value,species:species.value.trim(),basis:'observer-declared'});},
    set(value){const checked=validateAnimal(value ?? unknownAnimal());group.value=checked.group;species.value=checked.species;render();},
    lock(locked){group.disabled=locked;species.disabled=locked;get('lock').hidden=!locked;}
  };
  picker.set(); return picker;
}
