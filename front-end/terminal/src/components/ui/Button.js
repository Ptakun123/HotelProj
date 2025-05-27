export default function Button({ children, onClick, variant = 'primary' }) {
  const base = 'py-2 px-4 rounded-lg font-medium focus:outline-none';
  const variants = {
    primary: 'bg-primary text-white hover:bg-blue-700',
    secondary: 'bg-secondary text-white hover:bg-yellow-600',
  };
  return (
    <button className={`${base} ${variants[variant]}`} onClick={onClick}>
      {children}
    </button>
  );
}