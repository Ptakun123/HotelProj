import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { FaUserCircle } from 'react-icons/fa';
import './Navbar.css';

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    // Pokazanie popupu o pomyślnym wylogowaniu
    window.alert('Pomyślnie wylogowano.');
    navigate('/login');
  };

  return (
    <nav className="navbar">
      <div className="navbar__logo">
        <NavLink to="/search">UAIM HOTELE</NavLink>
      </div>
      <ul className="navbar__links">
        <li>
          <NavLink to="/search" className={({ isActive }) => isActive ? 'active' : ''}>
            Wyszukaj
          </NavLink>
        </li>
        {user && (
          <li>
            <NavLink
              to="/my-reservations"
              className={({ isActive }) => (isActive ? 'active' : '')}
            >
              Moje Rezerwacje
            </NavLink>
          </li>
        )}
        {!user ? (
          <>
            <li>
              <NavLink to="/login" className={({ isActive }) => isActive ? 'active' : ''}>
                Logowanie
              </NavLink>
            </li>
            <li>
              <NavLink to="/register" className={({ isActive }) => isActive ? 'active' : ''}>
                Rejestracja
              </NavLink>
            </li>
          </>
        ) : (
          <>
            <li>
              <NavLink to="/profile" className={({ isActive }) => isActive ? 'active flex items-center gap-2' : 'flex items-center gap-2'}>
                <FaUserCircle className="w-5 h-5" />
                Mój Profil
              </NavLink>
            </li>
            <li>
              <button
                onClick={handleLogout}
                className="navbar__link-button"
              >
                Wyloguj
              </button>
            </li>
          </>
        )}
      </ul>
    </nav>
  );
}
