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
            Search
          </NavLink>
        </li>
        <li>
          <NavLink to="/my-reservations" className={({ isActive }) => isActive ? 'active' : ''}>
            My Reservations
          </NavLink>
        </li>
        {!user ? (
          <>
            <li>
              <NavLink to="/login" className={({ isActive }) => isActive ? 'active' : ''}>
                Login
              </NavLink>
            </li>
            <li>
              <NavLink to="/register" className={({ isActive }) => isActive ? 'active' : ''}>
                Register
              </NavLink>
            </li>
          </>
        ) : (
          <>
            <li>
              <NavLink to="/profile" className={({ isActive }) => isActive ? 'active flex items-center gap-2' : 'flex items-center gap-2'}>
                <FaUserCircle className="w-5 h-5" />
                My Profile
              </NavLink>
            </li>
            <li>
              <button
                onClick={handleLogout}
                className="navbar__link-button"
              >
                Logout
              </button>
            </li>
          </>
        )}
      </ul>
    </nav>
  );
}
