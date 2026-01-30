// const RASA_URL = "http://localhost:5005/webhooks/rest/webhook";
const RASA_URL = "https://purvsonani-crisis-response-chatbot-backend.hf.space/webhooks/rest/webhook";

export async function sendRasaMessage(sender, message) {
  try {
    const res = await fetch(RASA_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ sender, message }),
    });

    if (!res.ok) {
      throw new Error(`API Error: ${res.statusText}`);
    }

    return await res.json();
  } catch (error) {
    console.error("Rasa API Error:", error);
    return []; // Return empty array on error to prevent app crash
  }
}
