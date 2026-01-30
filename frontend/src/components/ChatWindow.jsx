import { useState, useEffect, useRef } from "react";
import { sendRasaMessage } from "../services/rasaApi";
import SheltersList from "./SheltersList";

export default function ChatWindow() {
  const [messages, setMessages] = useState([
    {
      id: "init-1",
      text: "I am an automated emergency assistant and do not replace emergency services.",
      sender: "bot",
    },
    {
      id: "init-2",
      text: "Are you currently experiencing an emergency?",
      sender: "bot",
      // CRITICAL: Ensure 'buttons' is an array of objects with 'title' and 'payload'
      buttons: [
        { title: "Yes", payload: "/confirm_emergency" },
        { title: "No", payload: "/deny_emergency" }
      ]
    }
  ]);
  // const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [activeButtons, setActiveButtons] = useState([]);
  const [isHandover, setIsHandover] = useState(false);
  const endRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
    
    const lastMessage = messages[messages.length - 1];
    if (lastMessage?.buttons && lastMessage.buttons.length > 0) {
      setActiveButtons(lastMessage.buttons);
    }
  }, [messages, activeButtons, isHandover]);

  // --- MAIN SEND LOGIC ---
  async function sendMessage(payload, isButton = false, buttonTitle = "") {
    if (!payload.trim()) return;

    // 1. UI: Optimistic update (Show user message immediately)
    const isCoordinates = !isButton && /^-?\d+\.\d+,\s*-?\d+\.\d+$/.test(payload);
    if (!isCoordinates) {
      setMessages((m) => [
        ...m,
        {
          sender: "user",
          text: isButton ? buttonTitle : payload.replace(/^\/.*/, ""),
        },
      ]);
    }

    setInput("");
    setActiveButtons([]);

    const messageToSend = isButton && payload.startsWith("/") ? payload : payload;

    try {
      // 2. API: Call Rasa Backend
      const data = await sendRasaMessage("web", messageToSend); 
      
      console.log("RASA RESPONSE DATA:", data);

      // 3. LOGIC: Handle Handover
      const triggerHandover = data.some((msg) => msg.custom?.handoff === true);
      if (triggerHandover) {
        setIsHandover(true);
        return;
      }

      // 4. LOGIC: Parse Response
      const newMessages = data.map((d) => {
        // Case A: Backend sends Shelter Data -> Render Card Component
        if (d.custom?.show_shelters) {
          return { 
            type: "shelters", 
            sender: "bot", 
            shelterData: d.custom.shelters 
          };
        }
        
        // Case B: Backend sends Text -> Render Text Bubble
        if (!d.text) return null;
        return { sender: "bot", text: d.text };
      }).filter(Boolean);

      setMessages((m) => [...m, ...newMessages]);

      // 5. LOGIC: Handle Buttons
      const lastWithButtons = [...data].reverse().find((d) => d.buttons);
      setActiveButtons(lastWithButtons?.buttons || []);

    } catch (err) {
      console.error("Error flow failed:", err);
    }
  }

  // --- UTILS ---
  function shareCurrentLocation() {
    if (!navigator.geolocation) {
      alert("Geolocation not supported");
      return;
    }
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const { latitude, longitude } = pos.coords;
        sendMessage(`${latitude}, ${longitude}`);
      },
      () => alert("Unable to retrieve location"),
    );
  }

  function getButtonClass(payload, title) {
    const text = (payload + " " + title).toLowerCase();
    
    // RED (Danger)
    if (text.match(/operator|confirm_emergency|large|spreading|trapped|injured|inside home|path blocked|damage|gas|flood zone/)) return "danger";
    
    // GREY (Safe/End)
    if (text.match(/end chat|end_chat|safe|deny|small|control|outside|leave|clear|okay/)) return "safe";
    
    // BLUE (Services)
    if (text.match(/location|shelter/)) return "location";
    
    return "neutral";
  }

  // --- RENDER ---
  if (isHandover) {
    return (
      <div className="handover-container">
        <div className="status-bar">🎧 Connecting to operator...</div>
        <div className="handover-card">
          <div className="spinner"></div>
          <div className="icon-big">🎧</div>
          <h2>Connecting to emergency operator...</h2>
          <p>Please remain on this screen. A human operator will assist you shortly.</p>
        </div>
        <div className="info-box">
          <strong>Human-in-the-Loop Handover</strong>
          <ul className="handover-list">
            <li>AI assistant has detected high-risk indicators</li>
            <li>User input disabled during handover</li>
            <li>All conversation data preserved and shared with operator</li>
            <li>Operator will have full context and location information</li>
          </ul>
        </div>
      </div>
    );
  }

  return (
    <div className="chat-container">
      <div className="chat-window">
        {messages.map((m, i) => (
          <div key={i} className={`row ${m.sender}`}>
            {/* Conditional Rendering: Card vs Text Bubble */}
            {m.type === "shelters" ? (
              <SheltersList data={m.shelterData} />
            ) : (
              <div className={`bubble ${m.sender}`}>{m.text}</div>
            )}
          </div>
        ))}
        <div ref={endRef} />
      </div>

      {activeButtons.length > 0 && (
        <div className="action-bar">
          {activeButtons.map((b, i) => (
            <button 
              key={i} 
              className={`action-btn ${getButtonClass(b.payload, b.title)}`} 
              onClick={() => (b.payload === "/provide_location" ? shareCurrentLocation() : sendMessage(b.payload, true, b.title))}
            >
              {b.title}
            </button>
          ))}
        </div>
      )}

      <div className="input-bar">
        <input value={input} onChange={(e) => setInput(e.target.value)} placeholder="Type here..." onKeyDown={(e) => e.key === "Enter" && sendMessage(input)} />
        <button className="send-btn" onClick={() => sendMessage(input)}>➤</button>
      </div>
    </div>
  );
}