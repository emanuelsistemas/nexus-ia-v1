import React from "react";
import { ChatPage } from "./pages/ChatPage";
import { theme } from "./utils/theme";

function App() {
  return (
    <div style={{ background: theme.colors.background }}>
      <ChatPage />
    </div>
  );
}

export default App;

