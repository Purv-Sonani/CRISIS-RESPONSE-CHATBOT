import Header from "./components/Header";
import ChatWindow from "./components/ChatWindow";
import "./styles/variables.css";
import "./styles/chat.css";

export default function App() {
  return (
    <>
    <div className="app-root">
      <Header />
      <ChatWindow />
    </div>
    </>
  );
}
