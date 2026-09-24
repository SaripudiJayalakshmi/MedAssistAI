// ProtectedRoute.jsx
// Wraps a page component — if the user isn't logged in, redirect to /login instead.

import { Navigate } from "react-router-dom";
import { isLoggedIn } from "../auth";

function ProtectedRoute({ children }) {
  if (!isLoggedIn()) {
    return <Navigate to="/login" replace />;
  }
  return children;
}

export default ProtectedRoute;