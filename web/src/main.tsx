import "./monaco-setup";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App";
import { ErrorBoundary } from "./components/ErrorBoundary";
import "./styles/iae.css";
import "./styles/workspace.css";
import "./styles/typing.css";
import "./styles/lessons.css";
import "./styles/reference.css";
import "./styles/markup.css";
import "./styles/skin-tokens.css";
import "./styles/skins.css";
import { applySkin, savedSkin } from "./skins";

// Before the first render rather than in an effect, so a Light or
// Arcade user never sees a flash of the dark app while it loads.
applySkin(savedSkin());

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <ErrorBoundary>
      <App />
    </ErrorBoundary>
  </StrictMode>,
);
