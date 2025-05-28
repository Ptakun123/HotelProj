export default function PageLayout({ children }) {
  return (
    <div className="min-h-screen flex flex-col bg-gray-50 font-sans text-gray-800">
      <main className="container mx-auto px-4 flex-1">{children}</main>
      <footer className="bg-white shadow p-4 text-center text-sm text-gray-600">
        © 2025 Hotel UAIM Rezerwacje
      </footer>
    </div>
  );
}