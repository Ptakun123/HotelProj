import { useContext } from 'react';
import { AuthContext } from '../contexts/AuthContext';
import { Navigate } from 'react-router-dom';

export default function ProtectedRoute({ children, publicOnly = false }) {
  const { user } = useContext(AuthContext);

  // PublicRoute: jeśli user jest zalogowany i publicOnly=true, przekieruj do profilu
  if (publicOnly && user) {
    return <Navigate to="/profile" replace />;
  }

  // ProtectedRoute: jeśli user nie jest zalogowany i publicOnly=false, przekieruj do logowania
  if (!publicOnly && !user) {
    return <Navigate to="/login" replace />;
  }
  return children;
}