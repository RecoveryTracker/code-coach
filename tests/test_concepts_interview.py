"""The interview bank: shape, and every runnable claim held to real node.

The prose rules (length, no duplicates, follow-ups are questions) are checked
for every topic, this bank's included, by tests/test_concepts.py. This file
checks what that cannot: that the bank sits where it should, and that the
JavaScript the answers describe really prints what the answers say.

The oracle rule: each expected output in CLAIMS was worked out by hand from
the language's rules before it was run, never pasted from node. A claim also
names the phrase it comes from, and the test fails if that phrase is not in
the answer, so the snippet and the prose cannot drift apart.
"""

from __future__ import annotations

import shutil
import unittest

from code_coach.concepts import bank4, topic, topics
from code_coach.engine import run_code

HAS_NODE = shutil.which("node") is not None

# Topics about the platform rather than the language, offered to everyone.
SHARED = {
    "web-rendering-performance",
    "web-security-storage",
    "web-http-fetch-caching",
    "web-testing-tooling",
}

# (topic id, text in the question, phrase the answer says, snippet, stdout).
# The snippets are the answers' own examples. Where an answer talks about
# a number of milliseconds the snippet measures a generous bound instead.
CLAIMS: list[tuple[str, str, str, str, str]] = [
    # --- closures and scope
    ("js-closures-scope", "counter function", "1 then 2",
     r"function makeCounter(){ let n=0; return ()=>++n } const a=makeCounter(), b=makeCounter(); console.log(a(), a(), b())",
     "1 2 1"),
    ("js-closures-scope", "timers in a var loop", "3, 3, 3",
     r"const out=[]; for (var i=0;i<3;i++) setTimeout(()=>out.push(i)); setTimeout(()=>console.log(out.join(', ')),10)",
     "3, 3, 3"),
    ("js-closures-scope", "timers in a var loop", "0, 1, 2",
     r"const out=[]; for (let i=0;i<3;i++) setTimeout(()=>out.push(i)); setTimeout(()=>console.log(out.join(', ')),10)",
     "0, 1, 2"),
    ("js-closures-scope", "lexical scope", "top-level value",
     r"const x='global'; function show(){ return x } function run(){ const x='local'; return show() } console.log(run())",
     "global"),
    ("js-closures-scope", "IIFE", "typeof on it gives undefined",
     r"(function(){ var secret=1 })(); console.log(typeof secret)",
     "undefined"),
    ("js-closures-scope", "typeof throw", "gives the string undefined",
     r"console.log(typeof neverDeclared)",
     "undefined"),
    ("js-closures-scope", "typeof throw", "throws a ReferenceError",
     r"try { console.log(typeof x) } catch (e) { console.log(e.name) } let x=1",
     "ReferenceError"),
    ("js-closures-scope", "memoize", "runs the original only twice",
     r"function memoize(fn){ const c=new Map(); return x=>{ if(!c.has(x)) c.set(x, fn(x)); return c.get(x) } } let calls=0; const f=memoize(n=>{ calls++; return n*2 }); f(2); f(2); f(3); console.log(calls)",
     "2"),
    ("js-closures-scope", "currying", "gives 5",
     r"const add=a=>b=>a+b; console.log(add(2)(3), [1,2].map(add(5)))",
     "5 [ 6, 7 ]"),
    ("js-closures-scope", "make state private", "outside code gets undefined",
     r"class A{ #x=1; get(){ return this.#x } } const a=new A(); console.log(a.x, Object.keys(a).length, a.get())",
     "undefined 0 1"),
    ("js-closures-scope", "once(fn)", "leaves the counter at 1",
     r"function once(fn){ let done=false, r; return (...a)=>{ if(!done){ done=true; r=fn(...a) } return r } } let n=0; const f=once(()=>++n); f(); f(); console.log(n)",
     "1"),
    # --- this, call, apply, bind
    ("js-this-binding", "call, apply and bind", "all give 6",
     r"function f(a,b){ return this.n+a+b } const o={n:1}; console.log(f.call(o,2,3), f.apply(o,[2,3]), f.bind(o,2)(3))",
     "6 6 6"),
    ("js-this-binding", "wrong this", "g() gives undefined while o.get() gives 1",
     r"'use strict'; const o={n:1, get(){ return this?.n }}; const g=o.get; console.log(g(), o.get())",
     "undefined 1"),
    ("js-this-binding", "arrow functions differ", "throws a TypeError",
     r"try { new (()=>{}) } catch (e) { console.log(e.name) }",
     "TypeError"),
    ("js-this-binding", "arrow functions differ", "can read this.n directly",
     r"const o={n:5, m(){ return [1].map(()=>this.n)[0] }}; console.log(o.m())",
     "5"),
    ("js-this-binding", "the wrong choice", "this.n is undefined",
     r"const o={n:1, m:()=>this?.n}; console.log(o.m())",
     "undefined"),
    ("js-this-binding", "new operator", "hands back that object instead",
     r"function F(){ this.a=1; return {b:2} } console.log(new F())",
     "{ b: 2 }"),
    ("js-this-binding", "new operator", "returning a primitive like 5 is ignored",
     r"function G(){ this.a=1; return 5 } console.log(new G())",
     "G { a: 1 }"),
    ("js-this-binding", "Function.prototype.bind", "ignores the bound this",
     r"function P(x){ this.x=x } const B=P.bind({ignored:true},7); const b=new B(); console.log(b.x, b instanceof P, b.ignored)",
     "7 true undefined"),
    ("js-this-binding", "event handler", "this === t prints true",
     r"const t=new EventTarget(); t.addEventListener('x', function(){ console.log(this===t) }); t.dispatchEvent(new Event('x'))",
     "true"),
    ("js-this-binding", "top level", "this === module.exports is true",
     r"console.log(this===module.exports)",
     "true"),
    ("js-this-binding", "top level", "globalThis when sloppy and undefined",
     r"console.log((function(){ return this===globalThis })(), (function(){ 'use strict'; return this })())",
     "true undefined"),
    ("js-this-binding", "class method used as a callback", "throws a TypeError",
     r"class C{ n=1; h=()=>this.n; m(){ return this.n } } const c=new C(); const {h,m}=c; console.log(h()); try { m() } catch (e) { console.log(e.name) }",
     "1\nTypeError"),
    ("js-this-binding", "already bound function", "still reports 1",
     r"function f(){ return this.n } const b1=f.bind({n:1}); const b2=b1.bind({n:2}); console.log(b2())",
     "1"),
    ("js-this-binding", "already bound function", "ignore the this you supply",
     r"const o={n:1}; const a=()=>this===o; console.log(a.call(o))",
     "false"),
    # --- prototypes and classes
    ("js-prototypes-classes", "Object.create(null)", "is false, while in a plain object it is true",
     r"const d=Object.create(null); d.x=1; console.log('toString' in d, 'toString' in {})",
     "false true"),
    ("js-prototypes-classes", "Object.create(null)", "although hi is not an own property",
     r"const base={ hi(){ return 'hi' } }; const o=Object.create(base); console.log(o.hi(), Object.hasOwn(o,'hi'))",
     "hi false"),
    ("js-prototypes-classes", "real classes", "typeof a class is function",
     r"class A{ m(){} } console.log(typeof A, Object.keys(A.prototype).length)",
     "function 0"),
    ("js-prototypes-classes", "real classes", "throws a TypeError instead of quietly running",
     r"class A{} try { A() } catch (e) { console.log(e.name) }",
     "TypeError"),
    ("js-prototypes-classes", "derived constructor", "throws a ReferenceError",
     r"class A{} class B extends A{ constructor(){ try { this.x=1 } catch (e) { console.log(e.name) } super() } } new B()",
     "ReferenceError"),
    ("js-prototypes-classes", "static, prototype", "typeof a.s is undefined and typeof A.m is undefined",
     r"class A{ static s(){ return 's' } m(){ return 'm' } } const a=new A(); console.log(typeof a.s, typeof A.m, a.m())",
     "undefined undefined m"),
    ("js-prototypes-classes", "instanceof", "makes the check false for it",
     r"function F(){} const f=new F(); F.prototype={}; console.log(f instanceof F)",
     "false"),
    ("js-prototypes-classes", "for...in, Object.keys", "for...in sees b then a, while Object.keys sees only b",
     r"const p={a:1}; const o=Object.create(p); o.b=2; const seen=[]; for (const k in o) seen.push(k); console.log(seen.join(), Object.keys(o).join())",
     "b,a b"),
    ("js-prototypes-classes", "before the class keyword", "instanceof the parent is true",
     r"function P(n){ this.n=n } P.prototype.hi=function(){ return this.n }; function C(n){ P.call(this,n) } C.prototype=Object.create(P.prototype); C.prototype.constructor=C; const c=new C('x'); console.log(c.hi(), c instanceof P)",
     "x true"),
    ("js-prototypes-classes", "property descriptors", "silently does nothing",
     r"const o={}; Object.defineProperty(o,'k',{value:1}); o.k=2; console.log(o.k, Object.keys(o).length)",
     "1 0"),
    ("js-prototypes-classes", "array on a prototype", "makes the length 1 when read through another",
     r"function F(){} F.prototype.list=[]; const a=new F(), b=new F(); a.list.push(1); console.log(b.list.length)",
     "1"),
    ("js-prototypes-classes", "prototype pollution", "a later empty object reads true",
     r"function merge(t,s){ for (const k in s){ if (typeof s[k]==='object' && s[k]!==null) { t[k]=merge(t[k]||{}, s[k]) } else t[k]=s[k] } return t } merge({}, JSON.parse('{\"__proto__\":{\"admin\":true}}')); console.log(({}).admin); delete Object.prototype.admin",
     "true"),
    # --- the event loop
    ("js-event-loop-timers", "sync log, a zero-delay timer", "The output is A D C B",
     r"console.log('A'); setTimeout(()=>console.log('B'),0); Promise.resolve().then(()=>console.log('C')); console.log('D')",
     "A\nD\nC\nB"),
    ("js-event-loop-timers", "around an await", "That gives 1, 2, 3",
     r"async function f(){ console.log(1); await null; console.log(3) } f(); console.log(2)",
     "1\n2\n3"),
    ("js-event-loop-timers", "Two promise chains", "the output is 1, 2, 3, 4",
     r"Promise.resolve().then(()=>console.log(1)).then(()=>console.log(3)); Promise.resolve().then(()=>console.log(2)).then(()=>console.log(4))",
     "1\n2\n3\n4"),
    ("js-event-loop-timers", "recursive setTimeout", "the done message prints before a timer",
     r"setTimeout(()=>console.log('timer'),0); let n=0; (function loop(){ if (++n<1000) Promise.resolve().then(loop); else console.log('done') })()",
     "done\ntimer"),
    ("js-event-loop-timers", "sleep(ms)", "at least roughly 50",
     r"const sleep=ms=>new Promise(r=>setTimeout(r,ms)); (async()=>{ const t=Date.now(); await sleep(50); console.log(Date.now()-t>=45) })()",
     "true"),
    ("js-event-loop-timers", "error thrown inside a timer", "the catch never fires",
     r"try { setTimeout(()=>{ throw new Error('late') },0) } catch (e) { console.log('caught') } process.on('uncaughtException', e=>console.log('uncaught', e.message)); console.log('after')",
     "after\nuncaught late"),
    # --- promises and async/await
    ("js-promises-async", "How does a promise settle", "delivers 1 to its then handler",
     r"new Promise((res,rej)=>{ res(1); rej(2); res(3) }).then(v=>console.log(v))",
     "1"),
    ("js-promises-async", "Promise.all, allSettled", "AggregateError whose errors array holds each reason",
     r"Promise.any([Promise.reject(1), Promise.reject(2)]).catch(e=>console.log(e.constructor.name, e.errors.join()))",
     "AggregateError 1,2"),
    ("js-promises-async", "Promise.all, allSettled", "an array of status objects",
     r"Promise.allSettled([Promise.resolve(1), Promise.reject(2)]).then(r=>console.log(r.map(x=>x.status).join()))",
     "fulfilled,rejected"),
    ("js-promises-async", "What does then return", "prints ok",
     r"Promise.reject(new Error('x')).catch(()=>'ok').then(v=>console.log(v))",
     "ok"),
    ("js-promises-async", "return await matter", "the rejection escapes the handler",
     r"async function a(){ try { return Promise.reject(new Error('x')) } catch (e) { return 'caught' } } async function b(){ try { return await Promise.reject(new Error('x')) } catch (e) { return 'caught' } } (async()=>{ console.log(await a().catch(()=>'a escaped')); console.log(await b()) })()",
     "a escaped\ncaught"),
    ("js-promises-async", "forEach with an async callback", "the array still has length 0 right after forEach",
     r"const out=[]; [1,2].forEach(async n=>{ await null; out.push(n) }); console.log(out.length)",
     "0"),
    ("js-promises-async", "sequential and when parallel", "take about 120",
     r"(async()=>{ const s=ms=>new Promise(r=>setTimeout(r,ms)); let t=Date.now(); await s(60); await s(60); const seq=Date.now()-t; t=Date.now(); await Promise.all([s(60), s(60)]); const par=Date.now()-t; console.log(seq>=115, par<115) })()",
     "true true"),
    ("js-promises-async", "timeout or cancellation", "whose name is TimeoutError",
     r"const s=AbortSignal.timeout(10); s.addEventListener('abort', ()=>console.log(s.reason.name)); setTimeout(()=>{},50)",
     "TimeoutError"),
    ("js-promises-async", "explicit promise construction", "still lands in catch with the message",
     r"new Promise(()=>{ throw new Error('x') }).catch(e=>console.log('rejected', e.message))",
     "rejected x"),
    ("js-promises-async", "unhandled rejection", "unless you listen for unhandledRejection",
     r"process.on('unhandledRejection', r=>console.log('unhandled', r)); Promise.reject('boom')",
     "unhandled boom"),
    ("js-promises-async", "hundred requests", "never has more than three jobs in flight",
     r"async function pool(items,limit,fn){ let i=0, active=0, max=0; const worker=async()=>{ while (i<items.length) { const item=items[i++]; active++; max=Math.max(max,active); await fn(item); active-- } }; await Promise.all(Array.from({length:limit}, worker)); return max } pool([1,2,3,4,5,6,7,8], 3, ()=>new Promise(r=>setTimeout(r,5))).then(console.log)",
     "3"),
    ("js-promises-async", "thenable", "gives that string",
     r"const t={ then(res){ res('thenable') } }; (async()=>console.log(await t))()",
     "thenable"),
    # --- types, coercion, equality
    ("js-types-coercion", "primitive types", "object, function, bigint and symbol",
     r"console.log(typeof null, typeof (()=>{}), typeof 1n, typeof Symbol())",
     "object function bigint symbol"),
    ("js-types-coercion", "0.1 + 0.2", "0.30000000000000004",
     r"console.log(0.1+0.2, Number.MAX_SAFE_INTEGER, 9007199254740993)",
     "0.30000000000000004 9007199254740991 9007199254740992"),
    ("js-types-coercion", "[] + {}", "[1] + [2] is the string 12",
     r"console.log([]+{}, []+[]==='', [1]+[2])",
     "[object Object] true 12"),
    ("js-types-coercion", "parseInt", "[1, NaN, NaN]",
     r"console.log([1,2,3].map(parseInt))",
     "[ 1, NaN, NaN ]"),
    ("js-types-coercion", "Object.is", "Object.is(NaN, NaN) is true and Object.is(0, -0) is false",
     r"console.log(NaN===NaN, Object.is(NaN,NaN), 0===-0, Object.is(0,-0))",
     "false true true false"),
    ("js-types-coercion", "falsy", "keeps exactly three",
     r"console.log([0,'',null,undefined,NaN,0n,[],{},'0'].filter(Boolean).length)",
     "3"),
    ("js-types-coercion", "plus decide", "undefined + 1 is NaN",
     r"console.log(1+'2', '3'-1, '3'*'4', true+1, null+1, undefined+1)",
     "12 2 12 2 1 NaN"),
    ("js-types-coercion", "turn into a primitive", "gives 43 when you add 1",
     r"const o={ valueOf(){ return 42 }, toString(){ return 'str' } }; console.log(o+1, `${o}`, String(o))",
     "43 str str"),
    ("js-types-coercion", "isNaN and Number.isNaN", "isNaN('abc') is true and isNaN('') is false",
     r"console.log(isNaN('abc'), Number.isNaN('abc'), isNaN(''), Number(''))",
     "true false false 0"),
    ("js-types-coercion", "[] == ![]", "null == 0 is false, null >= 0 is true, and null == undefined is true",
     r"console.log([]==![], null==0, null>=0, null==undefined)",
     "true false true true"),
    ("js-types-coercion", "BigInt", "2n ** 64n is exactly 18446744073709551616n",
     r"try { 1n+1 } catch (e) { console.log(e.name) } console.log(2n**64n, 1n<2, 1n==1, 1n===1)",
     "TypeError\n18446744073709551616n true true false"),
    # --- objects, arrays, immutability
    ("js-objects-arrays-immutability", "shallow and a deep copy", "the spread copy reads 2 and the structuredClone copy reads 1",
     r"const a={n:{x:1}}; const s={...a}; const c=structuredClone(a); a.n.x=2; console.log(s.n.x, c.n.x)",
     "2 1"),
    ("js-objects-arrays-immutability", "structuredClone not copy", "keeps only the Date as a string and the NaN as null",
     r"console.log(JSON.stringify({ a:undefined, b:()=>1, c:new Date(0), d:NaN }))",
     '{"c":"1970-01-01T00:00:00.000Z","d":null}'),
    ("js-objects-arrays-immutability", "structuredClone not copy", "throws a DataCloneError",
     r"try { structuredClone({ f(){} }) } catch (e) { console.log(e.name) }",
     "DataCloneError"),
    ("js-objects-arrays-immutability", "structuredClone not copy", "so instanceof is false",
     r"class P{} console.log(structuredClone(new P()) instanceof P)",
     "false"),
    ("js-objects-arrays-immutability", "Object.freeze", "freezing an object with a nested one and then changing the nested value works",
     r"const o=Object.freeze({ a:1, n:{ b:1 } }); o.a=2; o.n.b=2; console.log(o.a, o.n.b, Object.isFrozen(o))",
     "1 2 true"),
    ("js-objects-arrays-immutability", "toSorted", "the original still reads 3,1,2 and the result is 1,2,3",
     r"const a=[3,1,2]; const b=a.toSorted(); console.log(a.join(), b.join())",
     "3,1,2 1,2,3"),
    ("js-objects-arrays-immutability", "[10, 9, 1].sort()", "The result is 1,10,9",
     r"console.log([10,9,1].sort().join(), [10,9,1].sort((a,b)=>a-b).join())",
     "1,10,9 1,9,10"),
    ("js-objects-arrays-immutability", "Map instead of a plain object", "list as 1,2,b,a on an object, while a Map built in that order gives b,2,a,1",
     r"const o={ b:1, 2:1, a:1, 1:1 }; const m=new Map([['b',1],[2,1],['a',1],[1,1]]); console.log(Object.keys(o).join(), [...m.keys()].join())",
     "1,2,b,a b,2,a,1"),
    ("js-objects-arrays-immutability", "How does a Set compare", "leaves four values",
     r"console.log([...new Set([1,1,'1',NaN,NaN,0,-0])].length)",
     "4"),
    ("js-objects-arrays-immutability", "WeakMap", "a string key throws a TypeError",
     r"try { new WeakMap().set('k',1) } catch (e) { console.log(e.name) }",
     "TypeError"),
    ("js-objects-arrays-immutability", "nested state", "the sibling is still the same object, the changed branch is new, and the old state is unchanged",
     r"const s={ a:{n:1}, b:{m:1} }; const t={ ...s, a:{ ...s.a, n:2 } }; console.log(t.b===s.b, t.a===s.a, s.a.n)",
     "true false 1"),
    ("js-objects-arrays-immutability", "destructuring defaults", "gives a as 1 and b as null",
     r"const {a=1, b=2}={ a:undefined, b:null }; console.log(a, b)",
     "1 null"),
    ("js-objects-arrays-immutability", "every value in an object", "doubling the values gives a as 2 and b as 4",
     r"console.log(Object.fromEntries(Object.entries({ a:1, b:2 }).map(([k,v])=>[k,v*2])))",
     "{ a: 2, b: 4 }"),
    ("js-objects-arrays-immutability", "Array(3).map", "the result is still three holes",
     r"console.log(Array(3).map((_,i)=>i), Array.from({length:3}, (_,i)=>i))",
     "[ <3 empty items> ] [ 0, 1, 2 ]"),
    # --- modules and bundling
    ("js-modules-bundling", "ES modules differ", "the importer reads 1 before and 2 after",
     r"import('data:text/javascript,export let n=1; export function inc(){n++}').then(m=>{ const before=m.n; m.inc(); console.log(before, m.n) })",
     "1 2"),
    ("js-modules-bundling", "dynamic import", "gives m.default equal to 5",
     r"import('data:text/javascript,export default 5').then(m=>console.log(m.default))",
     "5"),
    ("js-modules-bundling", "default export and named", "gives a then default",
     r"import('data:text/javascript,export default 1; export const a=2').then(m=>console.log(Object.keys(m).join()))",
     "a,default"),
    ("js-modules-bundling", "type=module", "leave a shared counter at 1",
     r"const url='data:text/javascript,globalThis.hits=(globalThis.hits||0)+1'; import(url).then(()=>import(url)).then(()=>console.log(globalThis.hits))",
     "1"),
    # --- the DOM and events (EventTarget is the part node has)
    ("js-dom-events", "remove an event listener", "prints hit only once",
     r"const t=new EventTarget(); const f=()=>console.log('hit'); t.addEventListener('x',f); t.addEventListener('x',f); t.dispatchEvent(new Event('x')); t.removeEventListener('x',f); t.dispatchEvent(new Event('x'))",
     "hit"),
    ("js-dom-events", "custom events", "a dispatched detail of 42 arrives as 42",
     r"const t=new EventTarget(); t.addEventListener('hi', e=>console.log(e.detail)); t.dispatchEvent(new CustomEvent('hi', { detail:42 }))",
     "42"),
    # --- rendering and performance
    ("web-rendering-performance", "debounce and throttle", "three rapid calls produce one run",
     r"function debounce(fn,ms){ let t; return (...a)=>{ clearTimeout(t); t=setTimeout(()=>fn(...a),ms) } } let n=0; const d=debounce(()=>n++,20); d(); d(); d(); setTimeout(()=>console.log(n),60)",
     "1"),
    ("web-rendering-performance", "debounce and throttle", "runs the first call straight away",
     r"function throttle(fn,ms){ let last=-Infinity; return (...a)=>{ const now=Date.now(); if (now-last>=ms) { last=now; fn(...a) } } } let n=0; const t=throttle(()=>n++,1000); t(); t(); t(); console.log(n)",
     "1"),
    ("web-rendering-performance", "ten thousand rows", "the first visible row is 30 and about 16 rows",
     r"const vh=600, rh=40, top=1234; console.log(Math.floor(top/rh), Math.ceil(vh/rh)+1)",
     "30 16"),
    ("web-rendering-performance", "heavy work off the main thread", "its length on the sender is 0 and on the receiver 8",
     r"const b=new ArrayBuffer(8); const c=structuredClone(b, { transfer:[b] }); console.log(b.byteLength, c.byteLength)",
     "0 8"),
    # --- security
    ("web-security-storage", "same-origin policy", "https://a.com and https://a.com:443 are the same origin",
     r"console.log(new URL('https://a.com/x').origin===new URL('https://a.com:443/y').origin, new URL('http://a.com').origin===new URL('https://a.com').origin)",
     "true false"),
    # --- HTTP and fetch
    ("web-http-fetch-caching", "fetch not reject on a 404", "ok is false and status is 404",
     r"const http=require('http'); const s=http.createServer((q,r)=>{ r.statusCode=404; r.end('no') }).listen(0, async()=>{ const res=await fetch('http://127.0.0.1:'+s.address().port); console.log(res.ok, res.status); s.close() })",
     "false 404"),
    ("web-http-fetch-caching", "cancel a fetch", "rejects with an AbortError",
     r"const c=new AbortController(); c.abort(); fetch('http://127.0.0.1:1/', { signal:c.signal }).catch(e=>console.log(e.name))",
     "AbortError"),
    # --- testing
    ("web-testing-tooling", "property-based", "over a hundred random arrays",
     r"const ok=Array.from({length:100}, ()=>Array.from({length:Math.floor(Math.random()*10)}, ()=>Math.floor(Math.random()*100))).every(a=>a.slice().reverse().reverse().join()===a.join()); console.log(ok)",
     "true"),
    # --- node
    ("node-internals", "phases of Node's event loop", "setImmediate always beats a zero-delay setTimeout",
     r"require('fs').readFile(__filename, ()=>{ setTimeout(()=>console.log('timeout'),0); setImmediate(()=>console.log('immediate')) })",
     "immediate\ntimeout"),
    ("node-internals", "nextTick, promises", "a synchronous log comes first, then nextTick, then the promise, then setImmediate",
     r"setImmediate(()=>console.log('immediate')); Promise.resolve().then(()=>console.log('promise')); process.nextTick(()=>console.log('tick')); console.log('sync')",
     "sync\ntick\npromise\nimmediate"),
    ("node-internals", "streams", "gives abc",
     r"(async()=>{ let s=''; for await (const c of require('stream').Readable.from(['a','b','c'])) s+=c; console.log(s) })()",
     "abc"),
    ("node-internals", "worker threads", "A worker's message reaches the main thread",
     r"const { Worker, isMainThread, parentPort }=require('worker_threads'); if (isMainThread) { new Worker(__filename).on('message', m=>console.log(m)) } else { parentPort.postMessage('from worker') }",
     "from worker"),
    ("node-internals", "block the event loop", "blocked prints before timer",
     r"setTimeout(()=>console.log('timer'),0); const t=Date.now(); while (Date.now()-t<50) {} console.log('blocked')",
     "blocked\ntimer"),
    ("node-internals", "strings, bytes", "length is 2, Buffer.byteLength gives 4, and spreading it gives one item",
     r"console.log('\u{1F600}'.length, Buffer.byteLength('\u{1F600}'), [...'\u{1F600}'].length)",
     "2 4 1"),
    ("node-internals", "EventEmitter handle errors", "Node throws the error",
     r"const E=require('events'); const e=new E(); try { e.emit('error', new Error('x')) } catch (err) { console.log('thrown', err.message) }",
     "thrown x"),
    ("node-internals", "EventEmitter handle errors", "The default limit is 10 listeners per event",
     r"console.log(require('events').defaultMaxListeners)",
     "10"),
    # --- game development
    ("js-browser-game-dev", "delta time", "both end at 100",
     r"const speed=100; let x1=0, x2=0; for (let i=0;i<60;i++) x1+=speed*(1/60); for (let i=0;i<30;i++) x2+=speed*(1/30); console.log(Math.round(x1), Math.round(x2))",
     "100 100"),
    ("js-browser-game-dev", "fixed timestep with an accumulator", "which is four updates with 8 left over",
     r"let acc=0, updates=0; for (const dt of [16,16,16]) { acc+=dt; while (acc>=10) { acc-=10; updates++ } } console.log(updates, acc)",
     "4 8"),
    ("js-browser-game-dev", "spiral of death", "only five 10 millisecond steps run and 950 remain",
     r"let acc=1000, steps=0; while (acc>=10 && steps<5) { acc-=10; steps++ } console.log(steps, acc)",
     "5 950"),
    ("js-browser-game-dev", "choppy", "you draw at 8",
     r"const prev=0, curr=10, alpha=8/10; console.log(prev+(curr-prev)*alpha)",
     "8"),
    ("js-browser-game-dev", "collision detection", "at 0 and 10 give false, and at 0 and 9 give true",
     r"const hit=(a,b)=>a.x<b.x+b.w && a.x+a.w>b.x && a.y<b.y+b.h && a.y+a.h>b.y; console.log(hit({x:0,y:0,w:10,h:10},{x:10,y:0,w:10,h:10}), hit({x:0,y:0,w:10,h:10},{x:9,y:0,w:10,h:10}))",
     "false true"),
    ("js-browser-game-dev", "tunnelling", "jumps clean over a 5 pixel wall",
     r"let x=0, hit=false; for (let i=0;i<20;i++) { x+=30; if (x>=100 && x<=105) hit=true } console.log(hit, x)",
     "false 600"),
    ("js-browser-game-dev", "Entity component system", "leaves the others untouched",
     r"const pos=new Map([[1,{x:0}],[2,{x:5}]]); const vel=new Map([[1,{dx:2}]]); for (const [id,v] of vel) { pos.get(id).x+=v.dx } console.log([...pos.values()].map(p=>p.x).join())",
     "2,5"),
    ("js-browser-game-dev", "load assets", "returns results in the same order as the input",
     r"Promise.all([new Promise(r=>setTimeout(()=>r('slow'),20)), 'fast']).then(v=>console.log(v.join()))",
     "slow,fast"),
    ("js-browser-game-dev", "deterministic", "return identical values",
     r"function m(a){ return ()=>{ a|=0; a=a+0x6D2B79F5|0; let t=Math.imul(a^a>>>15, 1|a); t=t+Math.imul(t^t>>>7, 61|t)^t; return ((t^t>>>14)>>>0)/4294967296 } } const r1=m(42), r2=m(42); console.log(r1()===r2(), r1()<1)",
     "true true"),
    # --- front-end system design
    ("frontend-system-design", "reducer-based store", "the original is untouched, and an unknown action returns the same object",
     r"const r=(s,a)=>a.type==='inc' ? { ...s, n:s.n+1 } : s; const s0={n:0}; const s1=r(s0,{type:'inc'}); console.log(s0.n, s1.n, r(s1,{type:'x'})===s1)",
     "0 1 true"),
    # The euro sign and the no-break space are swapped for ASCII so the
    # comparison does not depend on the console's code page.
    ("frontend-system-design", "internationalisation", "a dot for thousands, a comma for decimals and the symbol after",
     r"console.log(new Intl.NumberFormat('de-DE', { style:'currency', currency:'EUR' }).format(1234.5).replace(/ /g,' ').replace('€','EUR'))",
     "1.234,50 EUR"),
    ("frontend-system-design", "internationalisation", "Arabic has six categories, including two",
     r"const p=new Intl.PluralRules('en'); console.log(p.select(1), p.select(2), new Intl.PluralRules('ar').select(2))",
     "one other two"),
    ("frontend-system-design", "type-ahead", "only the latest, ab, is kept",
     r"let latest=0; const results=[]; const search=async(q,ms)=>{ const id=++latest; await new Promise(r=>setTimeout(r,ms)); if (id===latest) results.push(q) }; search('a',30); search('ab',5); setTimeout(()=>console.log(results.join()),60)",
     "ab"),
]


def _question(topic_id: str, fragment: str):
    found = topic(topic_id)
    assert found is not None, topic_id
    hits = [q for q in found.questions if fragment in q.ask]
    assert len(hits) == 1, (topic_id, fragment, len(hits))
    return hits[0]


class ShapeTests(unittest.TestCase):
    def test_ids_are_unique_and_do_not_clash(self) -> None:
        ids = [t.id for t in bank4.INTERVIEW_TOPICS]
        self.assertEqual(len(ids), len(set(ids)))
        everything = [t.id for t in topics()]
        for t in bank4.INTERVIEW_TOPICS:
            with self.subTest(topic=t.id):
                self.assertEqual(everything.count(t.id), 1)

    def test_the_bank_is_a_real_size(self) -> None:
        self.assertGreaterEqual(len(bank4.INTERVIEW_TOPICS), 14)
        self.assertLessEqual(len(bank4.INTERVIEW_TOPICS), 18)
        for t in bank4.INTERVIEW_TOPICS:
            with self.subTest(topic=t.id):
                self.assertGreaterEqual(len(t.questions), 8)
                self.assertLessEqual(len(t.questions), 12)
        total = sum(len(t.questions) for t in bank4.INTERVIEW_TOPICS)
        self.assertGreaterEqual(total, 140)

    def test_most_questions_carry_a_follow_up(self) -> None:
        for t in bank4.INTERVIEW_TOPICS:
            with self.subTest(topic=t.id):
                have = sum(1 for q in t.questions if q.follow_up)
                self.assertGreaterEqual(have, len(t.questions) * 0.7)

    def test_language_topics_are_javascript_and_platform_topics_are_shared(
        self,
    ) -> None:
        for t in bank4.INTERVIEW_TOPICS:
            with self.subTest(topic=t.id):
                if t.id in SHARED:
                    self.assertEqual(t.languages, ())
                    self.assertTrue(t.belongs_to("python"))
                else:
                    self.assertEqual(t.languages, ("javascript",))
                    self.assertTrue(t.belongs_to("javascript"))
                    self.assertFalse(t.belongs_to("python"))
        self.assertTrue(SHARED <= {t.id for t in bank4.INTERVIEW_TOPICS})

    def test_a_javascript_student_gets_them_after_the_semantics_topic(self) -> None:
        seen = [t.id for t in topics("javascript")]
        mine = [t.id for t in bank4.INTERVIEW_TOPICS]
        for topic_id in mine:
            self.assertIn(topic_id, seen)
        semantics = seen.index("javascript-semantics")
        first = min(seen.index(i) for i in mine)
        self.assertGreater(first, semantics)
        self.assertEqual([i for i in seen if i in mine], mine)

    def test_a_python_student_gets_only_the_shared_ones(self) -> None:
        seen = {t.id for t in topics("python")}
        self.assertEqual({i for i in seen if i in {t.id for t in bank4.INTERVIEW_TOPICS}}, SHARED)

    def test_orders_continue_after_the_older_banks(self) -> None:
        # The three banks that came before this one, not the Python bank that
        # came after it (orders 300 and up).
        from code_coach.concepts.bank import TOPICS
        from code_coach.concepts.bank2 import MORE_TOPICS
        from code_coach.concepts.bank3 import LANGUAGE_TOPICS

        older = [t.order for t in TOPICS + MORE_TOPICS + LANGUAGE_TOPICS]
        for t in bank4.INTERVIEW_TOPICS:
            self.assertGreater(t.order, max(older))

    def test_no_interview_ask_repeats_an_older_one(self) -> None:
        mine = {t.id for t in bank4.INTERVIEW_TOPICS}
        older = {q.ask for t in topics() if t.id not in mine for q in t.questions}
        for t in bank4.INTERVIEW_TOPICS:
            for q in t.questions:
                with self.subTest(ask=q.ask[:50]):
                    self.assertNotIn(q.ask, older)


class ClaimTableTests(unittest.TestCase):
    def test_there_are_enough_claims_and_every_topic_has_one_or_is_prose(self) -> None:
        self.assertGreaterEqual(len(CLAIMS), 40)
        # The platform topics are mostly prose, but all of the language and
        # runtime topics have runnable examples.
        covered = {c[0] for c in CLAIMS}
        for t in bank4.INTERVIEW_TOPICS:
            if t.id not in {"web-testing-tooling"}:
                with self.subTest(topic=t.id):
                    self.assertIn(t.id, covered)

    def test_each_claim_names_a_question_and_a_phrase_in_its_answer(self) -> None:
        """The snippet and the prose cannot drift apart: the sentence that
        states the result has to be in the answer it belongs to."""
        for topic_id, fragment, phrase, _code, _expected in CLAIMS:
            with self.subTest(topic=topic_id, ask=fragment, phrase=phrase[:40]):
                question = _question(topic_id, fragment)
                self.assertIn(phrase, question.answer)

    def test_no_claim_is_listed_twice(self) -> None:
        keys = [(c[0], c[1], c[2]) for c in CLAIMS]
        self.assertEqual(len(keys), len(set(keys)))


@unittest.skipUnless(HAS_NODE, "node is needed to check the claims")
class NodeClaimTests(unittest.TestCase):
    def test_every_claim_prints_what_the_answer_says(self) -> None:
        for topic_id, fragment, phrase, code, expected in CLAIMS:
            with self.subTest(topic=topic_id, ask=fragment, phrase=phrase[:40]):
                out, err, status = run_code(code, language="javascript", timeout=30)
                self.assertEqual(status, 0, err)
                self.assertEqual(out.strip().replace("\r\n", "\n"), expected)


if __name__ == "__main__":
    unittest.main()
