import React from "react";
import ReactDOM from "react-dom/client";

import App from "./App";
import "./index.css";

// React starts the application here.
// Everything else is rendered inside <App />.
ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
