import React, { useState, useRef, useEffect } from "react";
import { ChatMessage } from "../components/ChatMessage";
import { ChatInput } from "../components/ChatInput";
import { theme } from "../utils/theme";

interface Message {
  id: string;
  text: string;
  isUser: boolean;
  timestamp: string;
}

export const ChatPage: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (text: string) => {
    const newMessage: Message = {
      id: Date.now().toString(),
      text,
      isUser: true,
      timestamp: new Date().toLocaleTimeString(),
    };

    setMessages((prev) => [...prev, newMessage]);
    setIsLoading(true);

    try {
      // Simula uma resposta do assistente após 1 segundo
      await new Promise((resolve) => setTimeout(resolve, 1000));

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: "Esta é uma resposta simulada do assistente. Em breve será integrada com a API real.",
        isUser: false,
        timestamp: new Date().toLocaleTimeString(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error("Erro ao enviar mensagem:", error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div
      className="min-h-screen pb-32"
      style={{ background: theme.colors.background }}
    >
      {/* Header */}
      <header
        className="fixed top-0 left-0 right-0 h-16 flex items-center px-6 border-b z-10"
        style={{
          background: theme.colors.background,
          borderColor: theme.colors.border,
        }}
      >
        <h1 className="text-2xl font-bold" style={{ color: theme.colors.text.primary }}>
          Nexus IA
        </h1>
      </header>

      {/* Chat Container */}
      <main className="max-w-5xl mx-auto pt-24 pb-4">
        {messages.length === 0 ? (
          <div
            className="text-center py-12"
            style={{ color: theme.colors.text.secondary }}
          >
            <h2 className="text-3xl font-bold mb-4">Bem-vindo ao Nexus IA</h2>
            <p className="text-lg">Comece uma conversa enviando uma mensagem.</p>
          </div>
        ) : (
          <div className="space-y-6">
            {messages.map((message) => (
              <ChatMessage
                key={message.id}
                message={message.text}
                isUser={message.isUser}
                timestamp={message.timestamp}
              />
            ))}
          </div>
        )}
        <div ref={messagesEndRef} />
      </main>

      {/* Input */}
      <ChatInput onSendMessage={handleSendMessage} disabled={isLoading} />
    </div>
  );
};

