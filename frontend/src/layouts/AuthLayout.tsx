import { ShieldCheck } from "lucide-react";

import { LoginForm } from "../features/auth";

export function AuthLayout() {
  return (
    <main className="auth-layout">
      <section className="auth-copy">
        <div className="brand-mark">
          <ShieldCheck size={26} />
        </div>
        <h1>Task Management Portal</h1>
        <p>Secure access for admins and workers, backed by the dedicated auth service.</p>
      </section>
      <LoginForm />
    </main>
  );
}
