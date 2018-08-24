(function(t){function e(e){for(var a,s,o=e[0],u=e[1],c=e[2],d=0,m=[];d<o.length;d++)s=o[d],i[s]&&m.push(i[s][0]),i[s]=0;for(a in u)Object.prototype.hasOwnProperty.call(u,a)&&(t[a]=u[a]);l&&l(e);while(m.length)m.shift()();return r.push.apply(r,c||[]),n()}function n(){for(var t,e=0;e<r.length;e++){for(var n=r[e],a=!0,o=1;o<n.length;o++){var u=n[o];0!==i[u]&&(a=!1)}a&&(r.splice(e--,1),t=s(s.s=n[0]))}return t}var a={},i={app:0},r=[];function s(e){if(a[e])return a[e].exports;var n=a[e]={i:e,l:!1,exports:{}};return t[e].call(n.exports,n,n.exports,s),n.l=!0,n.exports}s.m=t,s.c=a,s.d=function(t,e,n){s.o(t,e)||Object.defineProperty(t,e,{enumerable:!0,get:n})},s.r=function(t){"undefined"!==typeof Symbol&&Symbol.toStringTag&&Object.defineProperty(t,Symbol.toStringTag,{value:"Module"}),Object.defineProperty(t,"__esModule",{value:!0})},s.t=function(t,e){if(1&e&&(t=s(t)),8&e)return t;if(4&e&&"object"===typeof t&&t&&t.__esModule)return t;var n=Object.create(null);if(s.r(n),Object.defineProperty(n,"default",{enumerable:!0,value:t}),2&e&&"string"!=typeof t)for(var a in t)s.d(n,a,function(e){return t[e]}.bind(null,a));return n},s.n=function(t){var e=t&&t.__esModule?function(){return t["default"]}:function(){return t};return s.d(e,"a",e),e},s.o=function(t,e){return Object.prototype.hasOwnProperty.call(t,e)},s.p="/";var o=window["webpackJsonp"]=window["webpackJsonp"]||[],u=o.push.bind(o);o.push=e,o=o.slice();for(var c=0;c<o.length;c++)e(o[c]);var l=u;r.push([0,"chunk-vendors"]),n()})({0:function(t,e,n){t.exports=n("56d7")},"1ae5":function(t,e,n){"use strict";var a=n("f50c"),i=n.n(a);i.a},"56d7":function(t,e,n){"use strict";n.r(e);n("cadf"),n("551c");var a=n("2b0e"),i=function(){var t=this,e=t.$createElement,n=t._self._c||e;return n("div",{attrs:{id:"app"}},[n("h1",{staticClass:"label"},[t._v("NLP-sovellus")]),n("toolbar",{attrs:{"current-comp":t.currentComp}}),n("div",{staticClass:"container"},[n(t.currentComp,{tag:"component"})],1)],1)},r=[],s=n("a322"),o=(n("20d6"),n("7f7f"),n("55dd"),n("2f62")),u=n("0e44"),c=n("a78e"),l=n("b054"),d=n.n(l),m=function(){var t=this,e=t.$createElement,n=t._self._c||e;return n("div",[n("button",{staticClass:"switch summarize",attrs:{disabled:"summarize-wizard"===t.currentComp},on:{click:function(e){t.switchComponent("summarize-wizard")}}},[t._v("Lauseiden valinta")]),n("button",{staticClass:"switch ner",attrs:{disabled:"named-entity-recognition"===t.currentComp},on:{click:function(e){t.switchComponent("named-entity-recognition")}}},[t._v("Henkilötietojen piilottaminen")])])},f=[],p={props:{currentComp:{type:String,required:!0}},methods:{switchComponent:function(t){nt.$emit("switchComp",t)}}},h=p,v=(n("a66f"),n("2877")),g=Object(v["a"])(h,m,f,!1,null,"a8ee1186",null),_=g.exports,b=function(){var t=this,e=t.$createElement,n=t._self._c||e;return n("form-wizard",{attrs:{"start-index":0,title:"Henkilötietojen piilottaminen",subtitle:"Korvaa erisnimet ja henkilötunnukset tekstistä",color:"#e67e22","back-button-text":"Edellinen","next-button-text":"Seuraava","finish-button-text":"Korvaa"},on:{"on-complete":t.onComplete,"on-loading":t.setLoading,"on-error":t.handleErrorMessage,"on-validate":t.fetchNERs}},[n("tab-content",{attrs:{title:"Tiedosto","before-change":t.validateNerFile,icon:"ti-user"}},[n("p",[t._v(" Anna tiedosto, joka sisältää korvattavan tekstin. ")]),n("input",{attrs:{id:"ner_file",type:"file",accept:"application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document,text/plain"},on:{change:function(e){t.setNerFile(e)}}}),n("div",[n("input",{directives:[{name:"model",rawName:"v-model",value:t.checked,expression:"checked"}],attrs:{type:"checkbox",id:"detect_hetu"},domProps:{checked:Array.isArray(t.checked)?t._i(t.checked,null)>-1:t.checked},on:{change:function(e){var n=t.checked,a=e.target,i=!!a.checked;if(Array.isArray(n)){var r=null,s=t._i(n,r);a.checked?s<0&&(t.checked=n.concat([r])):s>-1&&(t.checked=n.slice(0,s).concat(n.slice(s+1)))}else t.checked=i}}}),n("label",{attrs:{for:"detect_hetu"}},[t._v("Hae samalla HETUT (muodossa 010101-1234) korvattavaksi. ")])])]),n("tab-content",{attrs:{title:"Valitse korvattavat sanat",icon:"ti-settings","before-change":t.validateChosenNERs}},[t.loadingWizard?n("p",[t._v(" Haetaan erisnimiä. Tässä menee 1 - 4 minuuttia. ")]):t._e(),n("div",{directives:[{name:"show",rawName:"v-show",value:t.$store.state.ners_fetched,expression:"$store.state.ners_fetched"}]},[n("fieldset",[n("legend",[t._v("Valitse korvattavat sanat")]),n("div",{staticClass:"ner-row"},[n("input",{attrs:{type:"checkbox",id:"select_all",value:"select_all",name:"feature"},on:{change:function(e){t.selectAllNERs(e)}}}),n("label",{attrs:{for:"select_all"}},[n("b",[t._v("Valitse kaikki sanat")])])]),n("div",{staticClass:"ner-container"},t._l(this.$store.state.nernames,function(e,a){return n("div",{key:a,staticClass:"ner-row"},[n("input",{attrs:{type:"checkbox",id:e.name,name:"feature"},domProps:{value:e.name},on:{change:function(e){t.addNERToBeSubstituted(e)}}}),n("label",{attrs:{for:e.name}},[t._v(t._s(e.name))]),n("input",{attrs:{type:"text",id:e.name+"-substitute",placeholder:"Korvike"},domProps:{value:e.substitute},on:{change:function(e){t.changeSubstitute(e)}}})])}))])])]),n("tab-content",{attrs:{title:"Syötetiedoston muoto",icon:"ti-check","before-change":t.replaceWords}},[n("h3",[t._v("Korvataan sanat ")]),n("div",{staticClass:"substitute-pairs"},t._l(this.$store.state.nernames.filter(function(t){return t.selected}),function(e,a){return n("span",{key:a,staticClass:"sub-pair"},[t._v(t._s(e.name)+" => "+t._s(e.substitute)+" ")])})),n("br"),n("br"),t._v("\n      Missä muodossa haluat tiedoston ulos?\n      "),n("select",{attrs:{id:"returnType"},on:{change:function(e){t.changeNerReturnType(e)}}},[n("option",{attrs:{value:"docx"}},[t._v("Docx (word) tiedosto ")]),n("option",{attrs:{value:"txt"}},[t._v("Teksi (.txt) tiedosto ")])])]),t.loadingWizard?n("div",{staticClass:"loader"}):t._e(),t.errorMsg?n("div",[n("span",{staticClass:"error"},[t._v(t._s(t.errorMsg))])]):t._e()],1)},y=[],k=(n("7514"),n("2ee4")),T=n.n(k),E=(n("da93"),n("2440"));n("28a5");function S(t){var e="ABCDEFGHIJKLMNOPQRSTUWXYZ".split(""),n=t>0?Math.ceil(t/e.length):1,a=t%e.length,i=e[a];return Array(n+1).join(i)}function N(t,e){for(var n=!1,a=0;a<t.length;a++)-1!==e.name.indexOf(t[a])&&(n=!0);return n}function x(t){return new Promise(function(e,n){var a=!1,i=[".pdf",".docx",".txt"];if(t){for(var r=0;r<t.length;r++)if(a=N(i,t[r]),!a)break;a?e(!0):n("Tiedosto ei kelpaa, anna yksi seuraavista "+i)}else n("Anna tiedosto.")})}n("6be9");function C(t,e){var n=t.state.nernames.filter(function(t){return t.selected}),a=n.length,i=S(a),r={name:e,substitute:i};t.commit("TOGGLE_SUBSTITION",e),""==t.state.nernames.find(function(t){return t.name==e}).substitute&&t.commit("CHANGE_SUBSTITION",r)}a["a"].use(T.a);var w={data:function(){return{loadingWizard:!1,errorMsg:null,count:0}},methods:{setNerFile:function(t){this.$store.commit("SET_NER_FILE",t.currentTarget.files[0])},onComplete:function(){alert("Tässä menee pieni hetki.")},setLoading:function(t){this.loadingWizard=t},handleErrorMessage:function(t){this.errorMsg=t},validateChosenNERs:function(){var t=this.$store.state;return new Promise(function(e,n){0==t.nernames.length&&n("Henkilötiedot eivät ole vielä latautuneet tai yhtäkään ei löytynyt."),0==t.nernames.filter(function(t){return t.selected}).length&&n("Valitse ainakin yksi henkilötieto korvattavaksi.");var a=t.nernames.filter(function(t){return t.selected&&(null==t.substitute||""==t.substitute)});a.length>0&&n("Anna korvikkeet henkilötiedoille: "+a.map(function(t){return t.name}).join(", ")+" "),e(!0)})},validateNerFile:function(){var t=this.$store.state.nerFile;return x(t?[t]:void 0)},fetchNERs:function(){var t=this,e=this.$store.state.nerFile,n=this.$store.state.apiurl,a=this.$store.state.nerSearchPersonid,i=n+"/entities/directory";i+="?return_type=json&",i+="person_ids="+a;var r=new FormData;r.append("file-0",e),fetch(i,{method:"POST",body:r}).then(function(t){return t.json()}).then(function(e){t.setLoading(!1);for(var n=e.names,a=n.filenames.map(function(t){return n[t]})[0],i=0;i<a.length;i++){var r=0!=t.$store.state.nernames.length&&t.$store.state.nernames.some(function(t){return t.name==a[i]});r||t.$store.commit("ADD_NER_NAME",{name:a[i],selected:!1,substitute:""})}}).catch(function(e){t.setLoading(!1),console.error(e)}),this.setLoading(!0)},addNERToBeSubstituted:function(t){var e=t.currentTarget.value;C(this.$store,e)},selectAllNERs:function(t){var e=t.currentTarget.checked,n=document.getElementsByName(t.currentTarget.name);for(var a in n){var i=n[a];if(i instanceof HTMLInputElement){var r=i.checked!==e;i.checked=e,"select_all"!=i.value&&r&&C(this.$store,i.value)}}},replaceWords:function(){var t=this.$store.state.nernames.filter(function(t){return t.selected}),e=t.map(function(t){return t.name}),n=t.map(function(t){return t.substitute}),a=this.$store.state.nerFile,i=this.$store.state.apiurl,r=this.$store.state.nerReturnType,s=i+"/entities/replace",o=new FormData;o.append("file-0",a),s+="?return_type="+r+"&",s+="nerlist="+encodeURIComponent(JSON.stringify(e))+"&",s+="substitutes="+encodeURIComponent(JSON.stringify(n)),fetch(s,{method:"POST",body:o}).then(function(t){return t.blob()}).then(function(t){Object(E["saveAs"])(t)}).catch(function(t){error.log(t)})},changeSubstitute:function(t){var e=t.currentTarget.id,n=e.substring(0,e.length-11),a=t.currentTarget.value;this.$store.commit("CHANGE_SUBSTITION",{name:n,substitute:a})},changeNerReturnType:function(t){var e=t.currentTarget.options[t.currentTarget.selectedIndex].value;this.$store.commit("CHANGE_NER_RETURN_TYPE",e)}},computed:{checked:{get:function(){return this.$store.state.nerSearchPersonid},set:function(t){this.$store.commit("CHANGE_NER_TOGGLE_SEARCH_PERSONID")}}}},M=w,R=(n("1ae5"),Object(v["a"])(M,b,y,!1,null,"69b0645d",null)),O=R.exports,j=function(){var t=this,e=t.$createElement,n=t._self._c||e;return n("form-wizard",{attrs:{title:"Automaattinen tiivistäminen",subtitle:"Valitsee laskennallisesti merkityksellisimmät lauseet",shape:"circle",color:"gray","error-color":"#e74c3c","back-button-text":"Edellinen","next-button-text":"Seuraava","finish-button-text":"Tiivistä"},on:{"on-complete":t.onComplete,"on-loading":t.setLoading,"on-error":t.handleErrorMessage}},[n("tab-content",{attrs:{title:"Tiivistettävät tiedostot","before-change":t.validateFileInput,icon:"ti-user"}},[n("p",[t._v(" Anna tiivistettävät tiedostot. ")]),n("input",{attrs:{id:"summary_files",type:"file",accept:"application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document,text/plain",multiple:""},on:{change:function(e){t.setSummaryFiles(e)}}})]),n("tab-content",{attrs:{title:"Käytettävä tiivistelmä menetelmä",icon:"ti-settings"}},[n("div",{staticClass:"summary-method"},[n("div",{staticClass:"input-row"},[n("input",{attrs:{type:"radio",id:"summary-method-embedding",name:"summary-method",checked:""},on:{change:function(e){t.addSummaryMethod("embedding")}}}),n("label",{attrs:{for:"summary-method-embedding"}},[t._v(" Sanastoon perustuva tiivistys-menetelmä    ")]),n("div",{staticClass:"tooltip"},[t._v("Lisätietoja\n                     "),n("span",{staticClass:"tooltiptext"},[t._v("Valitsee lauseet, joiden sanojen yhteenlaskettu semanttinen etäisyys alkuperäisestä tekstistä on pienin mahdollinen.")])]),t._v("\n                     \n                   "),n("div",{staticClass:"tooltip"},[n("a",{on:{click:function(e){t.openLinkInNewTab("http://www.aclweb.org/anthology/D15-1232")}}},[t._v("Artikkeli ")]),n("span",{staticClass:"tooltiptext"},[t._v('  Kobayashi, Hayato, Masaki Noguchi, and Taichi Yatsuka. "Summarization based on embedding distributions." Proceedings of the 2015 Conference on Empirical Methods in Natural Language Processing. 2015.')])])]),n("div",{staticClass:"input-row"},[n("input",{attrs:{type:"radio",id:"summary-method-graph",name:"summary-method"},on:{change:function(e){t.addSummaryMethod("graph")}}}),n("label",{attrs:{for:"summary-method-graph"}},[t._v(" Sanoihin sanoihin perustuva tiivistys-menetelmä  ")]),n("div",{staticClass:"tooltip"},[t._v("Lisätietoja\n                     "),n("span",{staticClass:"tooltiptext"},[t._v("Valitsee lauseet, joissa on eniten samoja sanoja, kuin muissa lauseissa.")])]),t._v("\n                     \n                   "),n("div",{staticClass:"tooltip"},[n("a",{on:{click:function(e){t.openLinkInNewTab("https://www.jair.org/index.php/jair/article/view/10396/24901")}}},[t._v("Artikkeli ")]),n("span",{staticClass:"tooltiptext"},[t._v('Erkan, Günes, and Dragomir R. Radev. "Lexrank: Graph-based lexical centrality as salience in text summarization." Journal of artificial intelligence research 22 (2004): 457-479.')])])])])]),n("tab-content",{attrs:{title:"Tiivistelmän pituus",icon:"ti-check","before-change":t.validateMethodLength}},[n("div",[n("p",[t._v("Tiivistelmän pituus sanoissa ")]),n("input",{attrs:{type:"number",name:"quantity",min:"10",max:"300",value:"25"},on:{change:function(e){t.setSummaryLength(e)}}})])]),n("tab-content",{attrs:{title:"Syötetiedoston muoto",icon:"ti-check"}},[n("h3",[t._v("Lähetetään tiedostot palvelimelle")]),n("div",[t._v("Syötetyt tiedostot:\n                 "),t._l(t.summaryFileNames,function(e,a){return n("span",{key:a},[t._v(" "+t._s(e)+" ")])})],2),n("div",[t._v("Käytettävä menetelmä:\n                 "),n("span",[t._v(t._s(this.$store.state.summaryMethod))])]),n("div",[t._v("Tiivistelmän pituus sanoissa:\n                 "),n("span",[t._v(t._s(this.$store.state.summaryLength))])]),t._v("\n           Missä tiedostomuodossa tiivistelmä tulostetaan?\n           "),n("select",{attrs:{id:"returnType"},on:{change:function(e){t.changeSummaryReturnType(e)}}},[n("option",{attrs:{value:"docx"}},[t._v("Word (.docx) tiedosto ")]),n("option",{attrs:{value:"txt"}},[t._v("Teksti (.txt) tiedosto ")])]),n("br"),t.loadingWizard?n("p",[t._v("Tiedostot lähetetty palvelimelle Tässä voi mennä useita minutteja, riippuen tiedostojen koosta.")]):t._e()]),t.loadingWizard?n("div",{staticClass:"loader"}):t._e(),t.errorMsg?n("div",[n("span",{staticClass:"error"},[t._v(t._s(t.errorMsg))])]):t._e()],1)},L=[];n("ac6a"),n("456d"),n("8ee8");a["a"].use(T.a);var A,$={data:function(){return{loadingWizard:!1,errorMsg:null,count:0,rules:{summaryLength:[{required:!0,message:"Please input Activity name",trigger:"blur",min:10,max:300}]}}},methods:{openLinkInNewTab:function(t){window.open(t,"_blank")},setLoading:function(t){this.loadingWizard=t},handleErrorMessage:function(t){this.errorMsg=t},setSummaryFiles:function(t){this.$store.commit("SET_SUMMARY_FILES",t.currentTarget.files)},addSummaryMethod:function(t){this.$store.commit("SET_SUMMARY_METHOD",t)},validateFileInput:function(){var t=this.$store.state.summaryFiles;return x(t)},setSummaryLength:function(t){this.$store.commit("SET_SUMMARY_LENGTH",t.currentTarget.value)},validateMethodLength:function(){var t=this;return new Promise(function(e,n){var a=t.$store.state.summaryLength;a<10||a>300?n("Pituuden on oltava 10 - 300 sanaa."):e(!0)})},changeSummaryReturnType:function(t){var e=t.currentTarget.options[t.currentTarget.selectedIndex].value;this.$store.commit("CHANGE_SUMMARY_RETURN_TYPE",e)},onComplete:function(){for(var t=this,e=this.$store.state,n=e.summaryFiles,a=e.summaryMethod,i=e.summaryLength,r=e.summaryReturnType,s=e.apiurl,o=s+"/summarize/directory",u=new FormData,c=0;c<n.length;c++)u.append("file-"+c,n[c]);o+="?return_type="+r+"&",o+="method="+a+"&",o+="summary_length="+i,fetch(o,{method:"POST",body:u}).then(function(t){return t.blob()}).then(function(e){t.setLoading(!1),Object(E["saveAs"])(e)}).catch(function(e){t.setLoading(!1),error.log(e)}),this.setLoading(!0)}},computed:{summaryFileNames:function(){var t=this.$store.state.summaryFiles;return Object.keys(t).map(function(e){return t[e].name})}}},I=$,P=(n("be8e"),Object(v["a"])(I,j,L,!1,null,null,null)),F=P.exports,H="SET_NER_FILE",G="ADD_NER_NAME",U="TOGGLE_SUBSTITION",z="CHANGE_SUBSTITION",D="CHANGE_NER_RETURN_TYPE",Y="CHANGE_NER_TOGGLE_SEARCH_PERSONID",W="SET_SUMMARY_FILES",B="SET_SUMMARY_METHOD",K="SET_SUMMARY_LENGTH",J="CHANGE_SUMMARY_RETURN_TYPE";function V(){var t=new XMLHttpRequest;t.open("GET","/config",!1),t.send(null);var e=JSON.parse(t.responseText);return e.apiurl}var q=V();a["a"].use(o["a"]);var X=new o["a"].Store({state:{nerFile:null,nernames:[],ners_fetched:!1,apiurl:q,nerReturnType:"docx",nerSearchPersonid:!0,summaryFiles:[],summaryMethod:"embedding",summaryLength:25,summaryReturnType:"docx",summarySent:!1},mutations:(A={},Object(s["a"])(A,H,function(t,e){t.nerFile=e,t.ners_fetched=!1,t.nernames=[]}),Object(s["a"])(A,G,function(t,e){t.nernames.push(e),t.nernames=t.nernames.sort(function(t,e){return t.name>e.name}),t.ners_fetched=!0}),Object(s["a"])(A,U,function(t,e){var n=t.nernames.findIndex(function(t){return t.name==e});t.nernames[n].selected=!t.nernames[n].selected}),Object(s["a"])(A,z,function(t,e){var n=t.nernames.findIndex(function(t){return t.name==e.name});t.nernames[n].substitute=e.substitute}),Object(s["a"])(A,D,function(t,e){t.nerReturnType=e}),Object(s["a"])(A,Y,function(t){t.nerSearchPersonid=!t.nerSearchPersonid}),Object(s["a"])(A,W,function(t,e){t.summaryFiles=e}),Object(s["a"])(A,B,function(t,e){t.summaryMethod=e}),Object(s["a"])(A,K,function(t,e){t.summaryLength=e}),Object(s["a"])(A,J,function(t,e){t.summaryReturnType=e}),A),plugins:[Object(u["a"])({storage:{getItem:function(t){return c["get"](t)},setItem:function(t,e){return c["set"](t,e,{expires:3,secure:!0})},removeItem:function(t){return c["remove"](t)}}}),d()()]}),Q={el:"#app",store:X,data:function(){return{currentComp:"named-entity-recognition"}},created:function(){var t=this;nt.$on("switchComp",function(e){t.currentComp=e})},components:{toolbar:_,"named-entity-recognition":O,"summarize-wizard":F}},Z=Q,tt=(n("8e86"),Object(v["a"])(Z,i,r,!1,null,"24b07928",null)),et=tt.exports;n.d(e,"bus",function(){return nt}),a["a"].config.productionTip=!1;var nt=new a["a"];new a["a"](et).$mount("#app")},"6be9":function(t,e,n){},"8e86":function(t,e,n){"use strict";var a=n("d5c4"),i=n.n(a);i.a},"8ee8":function(t,e,n){},a66f:function(t,e,n){"use strict";var a=n("e02f"),i=n.n(a);i.a},be8e:function(t,e,n){"use strict";var a=n("df2d"),i=n.n(a);i.a},d5c4:function(t,e,n){},df2d:function(t,e,n){},e02f:function(t,e,n){},f50c:function(t,e,n){}});
//# sourceMappingURL=app.5a5fce36.js.map