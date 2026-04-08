import { useState, useRef, useEffect } from "react";

interface Message {
  role: "user" | "assistant";
  content: string;
  sql?: string;
  chart?: any;
}

export default function AskCortex() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;
    const userMsg = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: userMsg }]);
    setLoading(true);

    try {
      const res = await fetch("/api/v1/agent/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userMsg }),
      });
      const data = await res.json();

      let content = "";
      let sql = "";
      if (data.message) {
        content = typeof data.message === "string" ? data.message : JSON.stringify(data.message);
      } else if (data.choices?.[0]?.messages) {
        for (const m of data.choices[0].messages) {
          if (m.type === "text") content += m.content + "\n";
          if (m.type === "sql") sql = m.statement;
        }
      } else if (typeof data === "string") {
        content = data;
      } else {
        content = JSON.stringify(data, null, 2);
      }

      setMessages((prev) => [...prev, { role: "assistant", content: content.trim(), sql }]);
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: `Error: ${err.message}` },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const suggestions = [
    "Which channels drive the most revenue?",
    "How does Shapley compare to linear attribution?",
    "What is the forecast for the next 12 weeks?",
    "Which channels have the highest spend elasticity?",
  ];

  return (
    <div className="flex flex-col h-[calc(100vh-3rem)]">
      <h2 className="text-xl font-bold text-sf-dark mb-4">Ask Cortex</h2>

      <div className="flex-1 overflow-y-auto space-y-4 mb-4">
        {messages.length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-400 mb-6">Ask questions about your marketing data</p>
            <div className="flex flex-wrap justify-center gap-2">
              {suggestions.map((s) => (
                <button
                  key={s}
                  onClick={() => setInput(s)}
                  className="px-3 py-2 text-sm bg-white border border-gray-200 rounded-lg hover:bg-gray-50 text-gray-600"
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((m, i) => (
          <div
            key={i}
            className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-[80%] rounded-xl px-4 py-3 text-sm ${
                m.role === "user"
                  ? "bg-sf-blue text-white"
                  : "bg-white border border-gray-200 text-gray-800"
              }`}
            >
              <pre className="whitespace-pre-wrap font-sans">{m.content}</pre>
              {m.sql && (
                <details className="mt-2">
                  <summary className="text-xs text-gray-400 cursor-pointer">View SQL</summary>
                  <pre className="mt-1 p-2 bg-gray-50 rounded text-xs overflow-auto">{m.sql}</pre>
                </details>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="bg-white border border-gray-200 rounded-xl px-4 py-3 text-sm text-gray-400">
              Thinking...
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <div className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
          placeholder="Ask about your marketing data..."
          className="flex-1 border border-gray-300 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-sf-blue"
          disabled={loading}
        />
        <button
          onClick={handleSend}
          disabled={loading || !input.trim()}
          className="px-6 py-3 bg-sf-blue text-white rounded-xl text-sm font-medium hover:bg-sf-blue/90 disabled:opacity-50"
        >
          Send
        </button>
      </div>
    </div>
  );
}
