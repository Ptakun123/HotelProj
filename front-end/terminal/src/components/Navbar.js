import { NavLink } from 'react-router-dom';
import './Navbar.css';

export default function Navbar() {
  return (
    <nav className="navbar">
      <div className="navbar__logo">
        <NavLink to="/search">UAIM HOTELE</NavLink>
      </div>
      <ul className="navbar__links">
        <li><NavLink to="/search"   activeclassname="active">Search</NavLink></li>
        <li><NavLink to="/my-reservations" activeclassname="active">My Reservations</NavLink></li>
        <li><NavLink to="/login"    activeclassname="active">Login</NavLink></li>
        <li><NavLink to="/register" activeclassname="active">Register</NavLink></li>
      </ul>
    </nav>
  );
}
