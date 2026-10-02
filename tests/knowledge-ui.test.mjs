import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
test('evidence search coexists with site search and filters multiple terms',()=>{
 const input={value:'',addEventListener(event,fn){this.oninput=fn;}};
 const count={textContent:''},empty={hidden:true};
 const rows=[{dataset:{search:'fungi slow signals'},hidden:false},{dataset:{search:'bird calls'},hidden:false}];
 const context=vm.createContext({document:{getElementById:id=>({'graph-search':input,'graph-count':count,'graph-empty':empty})[id],querySelectorAll:()=>rows}});
 // The shared classic site script already declares this binding.
 vm.runInContext('const search = null;',context);
 vm.runInContext(fs.readFileSync(new URL('../web/assets/knowledge.js',import.meta.url),'utf8'),context);
 input.value='FUNGI slow';input.oninput();assert.equal(rows[0].hidden,false);assert.equal(rows[1].hidden,true);assert.match(count.textContent,/1 evidence/);
 input.value='unmatched';input.oninput();assert.equal(empty.hidden,false);
 input.value='';input.oninput();assert.equal(empty.hidden,true);assert.equal(rows.filter(r=>!r.hidden).length,2);
});
