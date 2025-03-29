import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import UserPage from "../userPage/userPage";
import Authenticate from "../authenticate/authenticate";

export const router = (
  <Router>
    <Routes>
      <Route path="/" element={<Authenticate />} />
      <Route path="/user" element={<UserPage />} />
    </Routes>
  </Router>
);
