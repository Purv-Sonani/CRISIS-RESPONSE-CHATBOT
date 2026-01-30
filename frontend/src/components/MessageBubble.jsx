export default function MessageBubble({ from, text }) {
  return (
    <div className={`bubble ${from}`}>
      {text}
    </div>
  );
}
