import React from "react";
import { theme } from "../utils/theme";

interface ChatMessageProps {
  message: string;
  isUser: boolean;
  timestamp?: string;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({ message, isUser, timestamp }) => {
  const messageStyle = isUser ? theme.chat.message.user : theme.chat.message.assistant;

  return (
    <div
      className={`flex ${isUser ? "justify-end" : "justify-start"} mb-6 px-4 md:px-6 lg:px-8`}
    >
      <div
        className={`relative max-w-[85%] md:max-w-[75%] rounded-2xl p-6 transition-all duration-200 hover:shadow-lg`}
        style={{
          background: messageStyle.background,
          border: messageStyle.border,
          boxShadow: messageStyle.shadow,
        }}
      >
        {/* Indicador de quem está falando */}
        <div
          className={`absolute -top-6 ${isUser ? "right-4" : "left-4"} text-sm font-semibold`}
          style={{ color: theme.colors.text.secondary }}
        >
          {isUser ? "Você" : "Assistente"}
        </div>

        {/* Conteúdo da mensagem */}
        <div className="prose prose-invert prose-lg max-w-none">
          {message}
        </div>

        {/* Timestamp */}
        {timestamp && (
          <div
            className="text-xs mt-3 opacity-60"
            style={{ color: theme.colors.text.muted }}
          >
            {timestamp}
          </div>
        )}
      </div>
    </div>
  );
};

