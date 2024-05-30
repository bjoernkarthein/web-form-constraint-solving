When codeql tries to create the database from the respective files we get:

CodeQL did not detect any code written in languages supported by CodeQL. This can occur if the specified build commands failed to compile or process any code.

- Confirm that there is some source code for the specified language in the project.
- For codebases written in Go, JavaScript, TypeScript, and Python, do not specify
  an explicit --command.
- For other languages, the --command must specify a "clean" build which compiles
  all the source code files without reusing existing build artefacts."

This seems to be due to the fact that there is CSS styling in this JS file:

```js
*/var oe=typeof Symbol=="function"&&Symbol.for,_c=oe?Symbol.for("react.element"):60103,Ac=oe?Symbol.for("react.portal"):60106,mo=oe?Symbol.for("react.fragment"):60107,po=oe?Symbol.for("react.strict_mode"):60108,ho=oe?Symbol.for("react.profiler"):60114,fo=oe?Symbol.for("react.provider"):60109,go=oe?Symbol.for("react.context"):60110,Mc=oe?Symbol.for("react.async_mode"):60111,bo=oe?Symbol.for("react.concurrent_mode"):60111,yo=oe?Symbol.for("react.forward_ref"):60112,ko=oe?Symbol.for("react.suspense"):60113,y0=oe?Symbol.for("react.suspense_list"):60120,vo=oe?Symbol.for("react.memo"):60115,wo=oe?Symbol.for("react.lazy"):60116,k0=oe?Symbol.for("react.block"):60121,v0=oe?Symbol.for("react.fundamental"):60117,w0=oe?Symbol.for("react.responder"):60118,x0=oe?Symbol.for("react.scope"):60119;function De(e){if(typeof e=="object"&&e!==null){var t=e.$$typeof;switch(t){case _c:switch(e=e.type,e){case Mc:case bo:case mo:case ho:case po:case ko:return e;default:switch(e=e&&e.$$typeof,e){case go:case yo:case wo:case vo:case fo:return e;default:return t}}case Ac:return t}}}function gf(e){return De(e)===bo}U.AsyncMode=Mc,U.ConcurrentMode=bo,U.ContextConsumer=go,U.ContextProvider=fo,U.Element=_c,U.ForwardRef=yo,U.Fragment=mo,U.Lazy=wo,U.Memo=vo,U.Portal=Ac,U.Profiler=ho,U.StrictMode=po,U.Suspense=ko,U.isAsyncMode=function(e){return gf(e)||De(e)===Mc},U.isConcurrentMode=gf,U.isContextConsumer=function(e){return De(e)===go},U.isContextProvider=function(e){return De(e)===fo},U.isElement=function(e){return typeof e=="object"&&e!==null&&e.$$typeof===_c},U.isForwardRef=function(e){return De(e)===yo},U.isFragment=function(e){return De(e)===mo},U.isLazy=function(e){return De(e)===wo},U.isMemo=function(e){return De(e)===vo},U.isPortal=function(e){return De(e)===Ac},U.isProfiler=function(e){return De(e)===ho},U.isStrictMode=function(e){return De(e)===po},U.isSuspense=function(e){return De(e)===ko},U.isValidElementType=function(e){return typeof e=="string"||typeof e=="function"||e===mo||e===bo||e===ho||e===po||e===ko||e===y0||typeof e=="object"&&e!==null&&(e.$$typeof===wo||e.$$typeof===vo||e.$$typeof===fo||e.$$typeof===go||e.$$typeof===yo||e.$$typeof===v0||e.$$typeof===w0||e.$$typeof===x0||e.$$typeof===k0)},U.typeOf=De,ff.exports=U;var S0=ff.exports,bf=S0,E0={$$typeof:!0,render:!0,defaultProps:!0,displayName:!0,propTypes:!0},C0={$$typeof:!0,compare:!0,defaultProps:!0,displayName:!0,propTypes:!0,type:!0},yf={};yf[bf.ForwardRef]=E0,yf[bf.Memo]=C0;const j0=typeof __SENTRY_DEBUG__>"u"||__SENTRY_DEBUG__;function $0(e){const t=e.match(/^([^.]+)/);return t!==null&&parseInt(t[0])>=17}const kf={componentStack:null,error:null,eventId:null};function P0(e,t){const n=new WeakMap;function a(r,i){if(!n.has(r)){if(r.cause)return n.set(r,!0),a(r.cause,i);r.cause=i}}a(e,t)}class Rc extends k.Component{constructor(t){super(t),Rc.prototype.__init.call(this),this.state=kf,this._openFallbackReportDialog=!0;const n=xe();n&&n.on&&t.showDialog&&(this._openFallbackReportDialog=!1,n.on("afterSendEvent",a=>{!a.type&&a.event_id===this._lastEventId&&df({...t.dialogOptions,eventId:this._lastEventId})}))}componentDidCatch(t,{componentStack:n}){const{beforeCapture:a,onError:r,showDialog:i,dialogOptions:o}=this.props;dh(s=>{if($0(k.version)&&ac(t)){const u=new Error(t.message);u.name=`React ErrorBoundary ${t.name}`,u.stack=n,P0(t,u)}a&&a(s,t,n);const l=ch(t,{captureContext:{contexts:{react:{componentStack:n}}},mechanism:{handled:!!this.props.fallback}});r&&r(t,n,l),i&&(this._lastEventId=l,this._openFallbackReportDialog&&df({...o,eventId:l})),this.setState({error:t,componentStack:n,eventId:l})})}componentDidMount(){const{onMount:t}=this.props;t&&t()}componentWillUnmount(){const{error:t,componentStack:n,eventId:a}=this.state,{onUnmount:r}=this.props;r&&r(t,n,a)}__init(){this.resetErrorBoundary=()=>{const{onReset:t}=this.props,{error:n,componentStack:a,eventId:r}=this.state;t&&t(n,a,r),this.setState(kf)}}render(){const{fallback:t,children:n}=this.props,a=this.state;if(a.error){let r;return typeof t=="function"?r=t({error:a.error,componentStack:a.componentStack,resetError:this.resetErrorBoundary,eventId:a.eventId}):r=t,k.isValidElement(r)?r:(t&&j0&&z.warn("fallback did not produce a valid ReactElement"),null)}return typeof n=="function"?n():n}}class Fc extends k.Component{constructor(){super(...arguments);Q(this,"handleLoad",()=>{this.setupFrameBaseStyle()})}componentDidMount(){this.node.addEventListener("load",this.handleLoad)}componentWillUnmout(){this.node.removeEventListener("load",this.handleLoad)}setupFrameBaseStyle(){this.node.contentDocument&&(this.iframeHtml=this.node.contentDocument.documentElement,this.iframeHead=this.node.contentDocument.head,this.iframeRoot=this.node.contentDocument.body,this.forceUpdate())}render(){const{children:n,head:a,title:r="",style:i={},dataTestId:o="",...s}=this.props;return c.jsxs("iframe",{srcDoc:"<!DOCTYPE html>","data-testid":o,ref:l=>this.node=l,title:r,style:i,frameBorder:"0",...s,children:[this.iframeHead&&nc.createPortal(a,this.iframeHead),this.iframeRoot&&nc.createPortal(n,this.iframeRoot)]})}}const Lc=e=>k.createElement("svg",{id:"Regular",xmlns:"http://www.w3.org/2000/svg",viewBox:"0 0 24 24",...e},k.createElement("defs",null,k.createElement("style",null,".cls-1{fill:none;stroke:currentColor;stroke-linecap:round;stroke-linejoin:round;stroke-width:0.8px;}")),k.createElement("circle",{className:"cls-1",cx:12,cy:9.75,r:5.25}),k.createElement("path",{className:"cls-1",d:"M18.913,20.876a9.746,9.746,0,0,0-13.826,0"}),k.createElement("circle",{className:"cls-1",cx:12,cy:12,r:11.25})),vf=`
    .gh-portal-avatar {
        position: relative;
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
        margin: 0 0 8px 0;
        border-radius: 999px;
    }

    .gh-portal-avatar img {
        position: absolute;
        display: block;
        top: -2px;
        right: -2px;
        bottom: -2px;
        left: -2px;
        width: calc(100% + 4px);
        height: calc(100% + 4px);
        opacity: 1;
        max-width: unset;
    }
`,N0=({style:e={}})=>({avatarContainer:{...e.avatarContainer||{}},gravatar:{...e.avatarContainer||{}},userIcon:{width:"34px",height:"34px",color:"#fff",...e.userIcon||{}}});function Oc({gravatar:e,style:t}){let n=N0({style:t});return c.jsxs("figure",{className:"gh-portal-avatar",style:n.avatarContainer,children:[c.jsx(Lc,{style:n.userIcon}),e?c.jsx("img",{style:n.gravatar,src:e,alt:""}):null]})}const T=L.createContext({site:{},member:{},action:"",lastPage:"",brandColor:"",pageData:{},onAction:(e,t)=>({action:e,data:t})}),T0=e=>k.createElement("svg",{width:21,height:24,viewBox:"0 0 21 24",fill:"none",xmlns:"http://www.w3.org/2000/svg",...e},k.createElement("path",{d:"M10.533 11.267c2.835 0 5.134-2.299 5.134-5.134C15.667 3.298 13.368 1 10.533 1 7.698 1 5.4 3.298 5.4 6.133s2.298 5.134 5.133 5.134zM1 23c0-2.529 1.004-4.953 2.792-6.741 1.788-1.788 4.213-2.792 6.741-2.792 2.529 0 4.954 1.004 6.741 2.792 1.788 1.788 2.793 4.212 2.793 6.74",stroke:"#fff",strokeWidth:1.5,strokeLinecap:"round",strokeLinejoin:"round"})),I0=e=>k.createElement("svg",{width:24,height:24,viewBox:"0 0 24 24",xmlns:"http://www.w3.org/2000/svg",...e},k.createElement("g",{fill:"none",fillRule:"evenodd"},k.createElement("path",{stroke:"#FFF",strokeWidth:1.5,strokeLinecap:"round",d:"M12.5 2v20M2 12.5h20"}))),z0=e=>k.createElement("svg",{width:25,height:24,viewBox:"0 0 25 24",fill:"none",xmlns:"http://www.w3.org/2000/svg",...e},k.createElement("path",{d:"M23.5 6v14.25c0 .597-.237 1.169-.659 1.591-.422.422-.994.659-1.591.659s-1.169-.237-1.591-.659c-.422-.422-.659-.994-.659-1.591V3c0-.398-.158-.78-.44-1.06-.28-.282-.662-.44-1.06-.44h-15c-.398 0-.78.158-1.06.44C1.157 2.22 1 2.601 1 3v17.25c0 .597.237 1.169.659 1.591.422.422.994.659 1.591.659h18M4.75 15h10.5M4.75 18h6",stroke:"#fff",strokeWidth:1.5,strokeLinecap:"round",strokeLinejoin:"round"}),k.createElement("path",{d:"M14.5 5.25h-9c-.414 0-.75.336-.75.75v4.5c0 .414.336.75.75.75h9c.414 0 .75-.336.75-.75V6c0-.414-.336-.75-.75-.75z",stroke:"#fff",strokeWidth:1.5,strokeLinecap:"round",strokeLinejoin:"round"})),D0=e=>k.createElement("svg",{width:24,height:18,viewBox:"0 0 24 18",fill:"none",xmlns:"http://www.w3.org/2000/svg",...e},k.createElement("path",{d:"M21.75 1.5H2.25c-.828 0-1.5.672-1.5 1.5v12c0 .828.672 1.5 1.5 1.5h19.5c.828 0 1.5-.672 1.5-1.5V3c0-.828-.672-1.5-1.5-1.5zM15.687 6.975L19.5 10.5M8.313 6.975L4.5 10.5",stroke:"#fff",strokeWidth:1.5,strokeLinecap:"round",strokeLinejoin:"round"}),k.createElement("path",{d:"M22.88 2.014l-9.513 6.56C12.965 8.851 12.488 9 12 9s-.965-.149-1.367-.426L1.12 2.014",stroke:"#fff",strokeWidth:1.5,strokeLinecap:"round",strokeLinejoin:"round"})),_0=e=>k.createElement("svg",{width:26,height:26,viewBox:"0 0 26 26",fill:"none",xmlns:"http://www.w3.org/2000/svg",...e},k.createElement("path",{d:"M17.903 12.016c-.332-1.665-1.491-3.032-3.031-3.654M11.037 8.4C9.252 9.163 8 10.935 8 13c0 .432.055.85.158 1.25M10.44 17.296c.748.447 1.624.704 2.56.704 1.71 0 3.22-.858 4.12-2.167M15.171 21.22c3.643-.96 6.329-4.276 6.329-8.22 0-1.084-.203-2.121-.573-3.075M18.611 6.615C17.114 5.3 15.151 4.5 13 4.5c-2.149 0-4.112.797-5.608 2.113M5.112 9.826c-.395.98-.612 2.052-.612 3.174 0 4.015 2.783 7.38 6.526 8.27",stroke:"#fff",strokeWidth:1.5,strokeLinecap:"round"}),k.createElement("path",{d:"M8.924 24.29c1.273.46 2.645.71 4.076.71 5.52 0 10.17-3.727 11.57-8.803M6.712 2.777C3.285 4.89 1 8.678 1 13c0 3.545 1.537 6.731 3.982 8.928M24.849 11.089C23.933 5.369 18.977 1 13 1c-.69 0-1.367.058-2.025.17",stroke:"#fff",strokeWidth:1.5,strokeLinecap:"round"})),Uc=`
    /* Colors
    /* ----------------------------------------------------- */
    :root {
        --black: #000;
        --blackrgb: 0,0,0;
        --grey0: #1d1d1d;
        --grey1: #333;
        --grey1rgb: 33, 33, 33;
        --grey2: #3d3d3d;
        --grey3: #474747;
        --grey4: #515151;
        --grey5: #686868;
        --grey6: #7f7f7f;
        --grey7: #979797;
        --grey8: #aeaeae;
        --grey9: #c5c5c5;
        --grey10: #dcdcdc;
...
```
