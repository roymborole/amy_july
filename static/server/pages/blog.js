(()=>{var e={};e.id=195,e.ids=[195,888,660],e.modules={7414:(e,t,s)=>{"use strict";s.r(t),s.d(t,{config:()=>S,default:()=>d,getServerSideProps:()=>f,getStaticPaths:()=>g,getStaticProps:()=>p,reportWebVitals:()=>x,routeModule:()=>y,unstable_getServerProps:()=>h,unstable_getServerSideProps:()=>v,unstable_getStaticParams:()=>P,unstable_getStaticPaths:()=>b,unstable_getStaticProps:()=>m});var r={};s.r(r),s.d(r,{default:()=>c});var i=s(7093),a=s(5244),l=s(1323),n=s(8824),u=s(6377);s(6689);var o=s(1163);function c(){return(0,o.useRouter)(),null}let d=(0,l.l)(r,"default"),p=(0,l.l)(r,"getStaticProps"),g=(0,l.l)(r,"getStaticPaths"),f=(0,l.l)(r,"getServerSideProps"),S=(0,l.l)(r,"config"),x=(0,l.l)(r,"reportWebVitals"),m=(0,l.l)(r,"unstable_getStaticProps"),b=(0,l.l)(r,"unstable_getStaticPaths"),P=(0,l.l)(r,"unstable_getStaticParams"),h=(0,l.l)(r,"unstable_getServerProps"),v=(0,l.l)(r,"unstable_getServerSideProps"),y=new i.PagesRouteModule({definition:{kind:a.x.PAGES,page:"/blog",pathname:"/blog",bundlePath:"",filename:""},components:{App:u.default,Document:n.default},userland:r})},6377:(e,t,s)=>{"use strict";s.r(t),s.d(t,{default:()=>i});var r=s(997);s(6764),s(6689),s(2015),s(4756);let i=function({Component:e,pageProps:t}){return r.jsx(e,{...t})}},8824:(e,t,s)=>{"use strict";s.r(t),s.d(t,{default:()=>n});var r=s(997),i=s(6859),a=s.n(i);class l extends a(){render(){return(0,r.jsxs)(i.Html,{children:[(0,r.jsxs)(i.Head,{children:[r.jsx("div",{id:"ticker-tape-root"}),r.jsx("link",{href:"https://fonts.googleapis.com/css2?family=Anton&family=Roboto:wght@400;700&display=swap",rel:"stylesheet"})]}),(0,r.jsxs)("body",{children:[r.jsx(i.Main,{}),r.jsx(i.NextScript,{}),r.jsx("script",{src:"/static/SearchModule.js",async:!0})]})]})}}let n=l},2015:(e,t,s)=>{"use strict";s.d(t,{e9:()=>l,Th:()=>i,iE:()=>a});let r=(0,require("contentful").createClient)({space:"gpifwsojf6z9",accessToken:"QYfgkZzWTgZIS4_yg9V46jt5JlqX4lb-JE5Jg-6fqqs"});async function i(){return(await r.getEntries({content_type:"featuredArticle",limit:1,include:2})).items[0]}async function a(e=5){let t=await r.getEntries({content_type:"asset",limit:e,order:"-sys.createdAt",select:["sys.id","fields.title","fields.image"]});return console.log("Raw Top Stories Response:",JSON.stringify(t,null,2)),t.items}async function l(e){return await r.getEntry(e)}},4756:()=>{},6764:()=>{},2785:e=>{"use strict";e.exports=require("next/dist/compiled/next-server/pages.runtime.prod.js")},6689:e=>{"use strict";e.exports=require("react")},6405:e=>{"use strict";e.exports=require("react-dom")},997:e=>{"use strict";e.exports=require("react/jsx-runtime")},7147:e=>{"use strict";e.exports=require("fs")},1017:e=>{"use strict";e.exports=require("path")},2781:e=>{"use strict";e.exports=require("stream")},9796:e=>{"use strict";e.exports=require("zlib")}};var t=require("../webpack-runtime.js");t.C(e);var s=e=>t(t.s=e),r=t.X(0,[859,77,163],()=>s(7414));module.exports=r})();