import { useState } from "react";

export default function InputBox({ onSend }) {
  const [text, setText] = useState("");

  const submit = () => {
    if (!text.trim()) return;
    onSend(text);
    setText("");
  };

  return (
    <div className="input-box">
      <input
        value={text}
        onChange={e => setText(e.target.value)}
        placeholder="Describe the emergency..."
        onKeyDown={e => e.key === "Enter" && submit()}
      />
      <button onClick={submit}>Send</button>
    </div>
  );
}
