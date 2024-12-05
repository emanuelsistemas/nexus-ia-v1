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
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} mb-4`}>
      <div
        className="max-w-[80%] rounded-lg p-4"
        style={{
          background: messageStyle.background,
          border: messageStyle.border,
          boxShadow: messageStyle.shadow,
        }}
      >
        <div className="prose prose-invert">{message}</div>
        {timestamp && (
          <div className="text-xs mt-2" style={{ color: theme.colors.text.muted }}>
            {timestamp}
          </div>
        )}
      </div>
    </div>
  );
};

