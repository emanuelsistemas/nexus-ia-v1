import React, { useState, KeyboardEvent } from "react";
import { theme } from "../utils/theme";

interface ChatInputProps {
  onSendMessage: (message: string) => void;
  placeholder?: string;
  disabled?: boolean;
}

export const ChatInput: React.FC<ChatInputProps> = ({
  onSendMessage,
  placeholder = "Digite sua mensagem...",
  disabled = false,
}) => {
  const [message, setMessage] = useState("");

  const handleSend = () => {
    if (message.trim() && !disabled) {
      onSendMessage(message.trim());
      setMessage("");
    }
  };

  const handleKeyPress = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div
      className="fixed bottom-0 left-0 right-0 p-4 md:p-6 border-t transition-all duration-200"
      style={{
        background: theme.colors.background,
        borderColor: theme.colors.border,
      }}
    >
      <div className="max-w-5xl mx-auto flex gap-4">
        <textarea
          className="flex-1 resize-none rounded-xl p-4 min-h-[60px] transition-all duration-200 focus:ring-2 focus:ring-primary focus:outline-none"
          style={{
            background: theme.chat.input.background,
            border: theme.chat.input.border,
            color: theme.colors.text.primary,
          }}
          placeholder={placeholder}
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          disabled={disabled}
        />
        <button
          className="px-6 py-3 rounded-xl font-semibold transition-all duration-200 hover:opacity-90 hover:scale-105 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed"
          style={{
            background: theme.colors.primary,
            color: theme.colors.text.primary,
          }}
          onClick={handleSend}
          disabled={disabled || !message.trim()}
        >
          Enviar
        </button>
      </div>
    </div>
  );
};

