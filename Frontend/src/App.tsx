import React from "react";
import logo from "./logo.svg";
import { BrowserRouter as Router } from "react-router-dom";
import { router } from "./services/router";

function App() {
  return (
    <>
      <div className="App">{router}</div>
    </>
  );
}

export default App;
