import { AuthProvider, useAuth } from "../features/auth";
import { AuthLayout } from "../layouts/AuthLayout";
import { DashboardLayout } from "../layouts/DashboardLayout";

function AppShell() {
  const { user } = useAuth();

  if (!user) {
    return <AuthLayout />;
  }

  return <DashboardLayout />;
}

export function App() {
  return (
    <AuthProvider>
      <AppShell />
    </AuthProvider>
  );
}
