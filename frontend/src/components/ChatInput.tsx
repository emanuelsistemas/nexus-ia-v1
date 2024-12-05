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
      className="p-4 fixed bottom-0 left-0 right-0"
      style={{ background: theme.colors.background }}
    >
      <div className="max-w-4xl mx-auto flex gap-2">
        <textarea
          className="flex-1 resize-none rounded-lg p-3"
          style={{
            background: theme.chat.input.background,
            border: theme.chat.input.border,
            color: theme.colors.text.primary,
          }}
          rows={1}
          placeholder={placeholder}
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          disabled={disabled}
        />
        <button
          className="px-4 py-2 rounded-lg font-medium transition-colors"
          style={{
            background: theme.colors.primary,
            color: theme.colors.text.primary,
            opacity: disabled || !message.trim() ? 0.5 : 1,
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

