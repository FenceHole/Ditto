import { useState, useEffect } from 'react'
import { initializeApp } from 'firebase/app'
import { getAuth, signInAnonymously, onAuthStateChanged } from 'firebase/auth'
import { getFirestore, collection, doc, onSnapshot, addDoc, serverTimestamp } from 'firebase/firestore'

// Firebase configuration - injected at build time via workflow
let auth = null
let db = null
const appId = 'ditto-ultimate-sanctuary'

// Initialize Firebase if config is available
if (window.__firebase_config) {
  const app = initializeApp(window.__firebase_config)
  auth = getAuth(app)
  db = getFirestore(app)
}

const Icon = ({ name, size = 20, className = "" }) => {
  useEffect(() => {
    if (window.lucide) window.lucide.createIcons()
  }, [name])
  return <i data-lucide={name} style={{ width: size, height: size }} className={className}></i>
}

const WingIcon = () => (
  <svg viewBox="0 0 100 100" className="w-32 h-32 mx-auto text-rose-800 opacity-40 animate-pulse">
    <path d="M50 80 Q 10 50 50 20 Q 90 50 50 80" fill="none" stroke="currentColor" strokeWidth="0.5" />
    <path d="M50 20 L 35 45 M 50 20 L 65 45" stroke="currentColor" strokeWidth="1" />
    <path d="M30 40 L 70 60 M 70 40 L 30 60" stroke="#d4af37" strokeWidth="0.3" strokeDasharray="2 1" />
  </svg>
)

function App() {
  const [view, setView] = useState('setup')
  const [user, setUser] = useState(null)
  const [sanctuaryId, setSanctuaryId] = useState('')
  const [inputKey, setInputKey] = useState('')
  const [answer, setAnswer] = useState('')
  const [entries, setEntries] = useState([])
  const [copyStatus, setCopyStatus] = useState(false)

  // THE INTENTIONAL PROMPTS
  const prompts = [
    { type: "Sacrifice", q: "Annie, the stories say he gave his wings for her. Chris, what is one 'wing' of your old self you are letting go of to protect Annie today?" },
    { type: "The Claim", q: "Chris, take the lead. Annie, what is one area of your life where you want Chris to step in and handle the weight so you can just breathe?" },
    { type: "Camino", q: "We're 'See Through' here. Annie, what's a secret part of your heart that Chris hasn't explored yet but you're ready to show him?" },
    { type: "Velvet", q: "In the safety of our Court, what is a fantasy you've been afraid to speak? Chris is listening, and there is no judgment here." }
  ]
  const currentPrompt = prompts[new Date().getDate() % prompts.length]

  useEffect(() => {
    const savedKey = localStorage.getItem('ditto_court_v3_id')
    if (savedKey) { 
      setSanctuaryId(savedKey)
      setView('bench')
    }
    
    if (auth) {
      signInAnonymously(auth).catch(console.error)
      const unsub = onAuthStateChanged(auth, setUser)
      return () => unsub()
    }
  }, [])

  useEffect(() => {
    if (!user || !sanctuaryId || !db) return
    
    const collectionRef = collection(doc(collection(doc(collection(db, 'artifacts'), appId), 'public'), 'data'), `court_${sanctuaryId}`)
    const unsub = onSnapshot(collectionRef, snap => {
      const data = snap.docs.map(d => ({ id: d.id, ...d.data() }))
      setEntries(data.sort((a, b) => (b.timestamp?.seconds || 0) - (a.timestamp?.seconds || 0)))
    })
    return () => unsub()
  }, [user, sanctuaryId])

  const submitEcho = async (cat = 'daily') => {
    if (!answer.trim() || !db) return
    
    const isChris = user.uid === entries.find(e => e.userName === 'Chris')?.uid || entries.length === 0
    const collectionRef = collection(doc(collection(doc(collection(db, 'artifacts'), appId), 'public'), 'data'), `court_${sanctuaryId}`)
    
    await addDoc(collectionRef, {
      uid: user.uid,
      userName: isChris ? 'Chris' : 'Annie',
      content: answer,
      category: cat,
      prompt: currentPrompt.q,
      timestamp: serverTimestamp()
    })
    
    setAnswer('')
    if (cat === 'bench') setView('echoes')
  }

  if (view === 'setup') {
    return (
      <div className="min-h-screen court-gradient flex items-center justify-center p-8">
        <div className="max-w-md w-full text-center space-y-12 animate-in fade-in zoom-in duration-1000">
          <div className="space-y-4">
            <WingIcon />
            <h1 className="text-7xl font-black italic tracking-tighter text-rose-800 gold-glow">Ditto.</h1>
            <p className="text-[10px] uppercase tracking-[0.5em] opacity-40 font-sans font-black">The Sovereign Court of Chris & Annie</p>
          </div>
          {!sanctuaryId ? (
            <div className="space-y-6">
              <button onClick={() => {
                const key = Math.random().toString(36).substring(2, 8).toUpperCase()
                setSanctuaryId(key)
                localStorage.setItem('ditto_court_v3_id', key)
              }} className="w-full bg-rose-900 text-white py-5 rounded-full font-sans font-black uppercase tracking-widest text-[10px] crimson-shadow border border-rose-700/30">Establish Our Court</button>
              <div className="flex items-center gap-4 opacity-20"><div className="h-[1px] flex-grow bg-current"></div><span className="text-[10px] font-sans">OR SYNC</span><div className="h-[1px] flex-grow bg-current"></div></div>
              <input value={inputKey} onChange={e => setInputKey(e.target.value)} placeholder="ENTER KEY" className="w-full bg-transparent border-b border-rose-900/30 text-center py-4 text-3xl font-sans font-black tracking-[0.5em] outline-none uppercase" />
              <button onClick={() => { if(inputKey.length === 6) { setSanctuaryId(inputKey.toUpperCase()); localStorage.setItem('ditto_court_v3_id', inputKey.toUpperCase()); setView('bench'); } }} className="text-[10px] font-sans font-black uppercase tracking-widest text-rose-700 opacity-60">Connect Hearts</button>
            </div>
          ) : (
            <div className="space-y-8">
              <div className="p-10 glass rounded-[3rem] border-rose-900/20 shadow-2xl">
                <p className="text-[9px] font-sans font-black uppercase tracking-widest opacity-40 mb-4 italic text-rose-400">Your Private Sanctuary Key</p>
                <h2 className="text-5xl font-sans font-black tracking-[0.3em] text-rose-700">{sanctuaryId}</h2>
                <button onClick={() => { navigator.clipboard.writeText(sanctuaryId); setCopyStatus(true); setTimeout(()=>setCopyStatus(false), 2000); }} className="text-[10px] font-sans font-black uppercase opacity-40 hover:text-rose-500 transition-all flex items-center gap-2 mx-auto mt-4">
                  <Icon name={copyStatus ? "check-circle" : "share-2"} size={14} /> {copyStatus ? "Copied" : "Copy Key for Annie"}
                </button>
              </div>
              <button onClick={() => setView('bench')} className="bg-rose-900 text-white px-10 py-4 rounded-full text-[10px] font-sans font-black uppercase tracking-widest crimson-shadow hover:scale-105 transition-all">Enter The Haven</button>
            </div>
          )}
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-[#050507]">
      {/* TOP NAVIGATION */}
      <nav className="px-10 py-8 sticky top-0 z-50 flex justify-between items-center glass border-b border-rose-950/20 bg-black/60">
        <div className="flex items-center gap-4">
          <div className="w-10 h-10 bg-rose-900 rounded-2xl flex items-center justify-center text-white rotate-6 crimson-shadow"><Icon name="crown" size={20} /></div>
          <div>
            <h1 className="text-2xl font-black italic tracking-tighter">Ditto.</h1>
            <p className="text-[8px] font-sans font-black opacity-30 tracking-widest">COURT KEY: {sanctuaryId}</p>
          </div>
        </div>
        <div className="text-right">
          <p className="text-[8px] font-sans font-black uppercase opacity-20 italic">Protector Presence</p>
          <p className="text-[10px] font-sans font-bold text-rose-700 tracking-widest uppercase animate-gold">CHRIS ACTIVE</p>
        </div>
      </nav>

      <main className="max-w-xl mx-auto px-6 py-12 pb-44">
        {/* MODULE SWITCHER */}
        <div className="flex p-1.5 rounded-full mb-12 glass shadow-inner border border-white/5">
          {['bench', 'library', 'velvet', 'echoes'].map(tab => (
            <button key={tab} onClick={() => setView(tab)} className={`flex-grow py-4 rounded-full transition-all flex flex-col items-center gap-1 ${view === tab ? 'bg-rose-900 text-white crimson-shadow' : 'opacity-30'}`}>
              <Icon name={tab === 'bench' ? 'sword' : tab === 'library' ? 'book' : tab === 'velvet' ? 'flame' : 'history'} size={14} />
              <span className="text-[7px] font-sans font-black uppercase tracking-widest">{tab}</span>
            </button>
          ))}
        </div>

        {/* MODULE: THE BENCH */}
        {view === 'bench' && (
          <div className="space-y-10 animate-in fade-in slide-in-from-bottom-8 duration-1000">
            <div className="p-10 rounded-[4rem] glass border-rose-900/20 text-center relative overflow-hidden group">
              <div className="inline-flex items-center gap-2 px-4 py-2 bg-rose-900/10 rounded-full mb-10 border border-rose-900/20">
                <Icon name="sparkles" size={14} className="text-rose-700 animate-pulse" />
                <span className="text-[10px] font-sans font-black text-rose-700 uppercase tracking-widest italic">The Daily Mirror</span>
              </div>
              <h2 className="text-3xl font-medium leading-tight mb-12 italic text-slate-100 px-2 font-serif">"{currentPrompt.q}"</h2>
              <textarea value={answer} onChange={e => setAnswer(e.target.value)} placeholder="Be see-through, be honest..." className="w-full p-8 rounded-[2.5rem] bg-black/60 border border-white/5 text-sm font-sans outline-none focus:border-rose-900 h-64 mb-10 transition-all focus:ring-8 focus:ring-rose-900/5" />
              <button onClick={() => submitEcho('bench')} className="w-full bg-rose-900 text-white py-6 rounded-[2rem] font-sans font-black uppercase tracking-[0.3em] text-[10px] crimson-shadow hover:bg-rose-800 active:scale-95 transition-all">Ditto This Vow</button>
            </div>
            <div className="p-8 glass rounded-[3rem] border-rose-900/20 flex gap-6 items-start">
              <Icon name="shield-check" className="text-rose-700 shrink-0 mt-1" size={24} />
              <div>
                <p className="text-[10px] font-sans font-black uppercase text-rose-400 italic mb-1">Chris's Vow of Protection</p>
                <p className="text-[11px] font-sans opacity-50 leading-relaxed italic">Annie, this space is governed by Chris's strength. Your vulnerability here is safe, sacred, and protected. You can speak without fear.</p>
              </div>
            </div>
          </div>
        )}

        {/* MODULE: VELVET VAULT */}
        {view === 'velvet' && (
          <div className="space-y-10 animate-in zoom-in duration-700">
            <div className="bg-[#120505] p-12 rounded-[4rem] border-2 border-rose-900/30 text-center relative overflow-hidden">
              <Icon name="flame" size={80} className="text-rose-950 mx-auto mb-8 opacity-20" />
              <h3 className="text-4xl font-black italic tracking-tighter text-white mb-6">The Boundless Haven.</h3>
              <p className="text-[10px] text-rose-700 font-sans font-black uppercase tracking-[0.4em] mb-12 italic">STRETCH LIMITS. NO JUDGMENT.</p>
              <p className="text-xs opacity-50 font-sans leading-relaxed mb-10 italic">Annie, this is for the things you thought you had to hide. Chris is ready to be there with you in every shadow. Share your kinks, your fantasies, and your deepest cravings.</p>
              <textarea value={answer} onChange={e => setAnswer(e.target.value)} placeholder="Unleash the shadows..." className="w-full p-8 rounded-[3rem] bg-black/80 border border-rose-950 text-sm h-64 mb-10 outline-none focus:border-rose-700 transition-all text-rose-100 font-sans" />
              <button onClick={() => submitEcho('velvet')} className="w-full bg-rose-950 text-rose-600 py-6 rounded-full font-sans font-black uppercase tracking-widest text-[11px] border border-rose-900/50 shadow-xl shadow-rose-900/10 hover:bg-rose-900 hover:text-white transition-all">Trust Chris With This</button>
            </div>
          </div>
        )}

        {/* MODULE: ECHOES */}
        {view === 'echoes' && (
          <div className="space-y-10 animate-in fade-in duration-500">
            <div className="flex justify-between items-center px-4">
              <h3 className="text-[11px] font-sans font-black text-slate-500 uppercase tracking-[0.4em] italic">The Archive of Us</h3>
              <Icon name="history" size={16} className="text-slate-600" />
            </div>
            {entries.length === 0 ? (
              <div className="py-40 text-center opacity-10"><WingIcon /><p className="text-[10px] font-sans uppercase font-black tracking-widest mt-8 italic">The story is waiting for your ink.</p></div>
            ) : (
              entries.map(e => (
                <div key={e.id} className="p-10 rounded-[3.5rem] glass border-rose-900/10 relative group mb-8 transition-all hover:border-rose-900/30">
                  <div className="flex justify-between items-center mb-10">
                    <div className="flex items-center gap-4">
                      <div className={`w-10 h-10 rounded-full flex items-center justify-center text-[11px] font-sans font-black italic shadow-inner ${e.userName === 'Chris' ? 'bg-rose-900 text-white' : 'bg-slate-800 text-slate-300'}`}>{e.userName === 'Chris' ? 'C' : 'A'}</div>
                      <div>
                        <span className="text-[11px] font-sans font-black uppercase tracking-widest text-rose-700 italic block">{e.userName}</span>
                        <span className="text-[8px] font-sans opacity-20 uppercase font-black tracking-[0.2em]">{e.userName === 'Chris' ? 'The Protector' : 'The Heart'}</span>
                      </div>
                    </div>
                    <span className={`text-[8px] font-sans font-black uppercase px-3 py-1 rounded-full border ${e.category === 'velvet' ? 'bg-rose-950/20 text-rose-500 border-rose-900/30' : 'bg-rose-900/10 text-rose-700 border-rose-900/20'}`}>{e.category}</span>
                  </div>
                  <p className="text-sm md:text-base leading-relaxed opacity-90 italic font-serif px-2 font-medium">"{e.content}"</p>
                  <div className="mt-10 flex justify-between items-center opacity-10">
                    <span className="text-[8px] font-sans font-black uppercase tracking-widest">{new Date(e.timestamp?.seconds * 1000).toLocaleDateString()}</span>
                    <Icon name="heart" size={12} className="fill-current" />
                  </div>
                </div>
              ))
            )}
          </div>
        )}

        {/* MODULE: LIBRARY */}
        {view === 'library' && (
          <div className="space-y-10 animate-in zoom-in duration-700">
            <div className="bg-rose-950/10 border border-rose-900/20 p-12 rounded-[4rem] relative overflow-hidden">
              <Icon name="book-open" size={140} className="absolute -bottom-10 -right-10 opacity-5 rotate-12" />
              <h3 className="text-3xl font-black italic tracking-tighter text-rose-700 mb-6 underline decoration-rose-900/30">The Storybook Haven.</h3>
              <p className="text-xs opacity-60 font-sans leading-relaxed font-medium mb-12 italic">Annie, this is where we map the worlds you love. Tell Chris about the heroes that make you feel safe, the sacrifices that move you, and the romance you crave. We are writing our own series now.</p>
              <div className="grid grid-cols-1 gap-6">
                {[
                  "Annie, if Chris were a character in your favorite series, what magic would he use to guard you?",
                  "What is the most romantic 'sacrifice' you've ever read about? Could we do that here?",
                  "Chris, name one storybook hero trait you are adopting for Annie today."
                ].map((q, i) => (
                  <button key={i} onClick={() => { setView('bench'); setAnswer(`Library Note: ${q}\n\n`); }} className="p-8 bg-black/40 border border-white/5 rounded-[2.5rem] text-left text-xs italic opacity-40 hover:opacity-100 hover:border-rose-900 transition-all font-sans">
                    {q}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}
      </main>

      {/* FIXED FOOTER NAVIGATION */}
      <footer className="fixed bottom-0 left-0 right-0 p-10 flex justify-around items-center glass border-t border-rose-950/20 bg-black/90 z-50">
        {['bench', 'library', 'velvet', 'echoes'].map(tab => (
          <button key={tab} onClick={() => setView(tab)} className={`transition-all duration-300 ${view === tab ? 'text-rose-700 scale-150' : 'text-slate-600 opacity-40 hover:opacity-80'}`}>
            <Icon name={tab === 'bench' ? 'sword' : tab === 'library' ? 'book' : tab === 'velvet' ? 'flame' : 'history'} size={28} />
          </button>
        ))}
      </footer>
    </div>
  )
}

export default App
