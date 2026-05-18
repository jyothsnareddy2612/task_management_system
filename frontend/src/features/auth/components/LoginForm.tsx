import { LogIn } from "lucide-react";
import { type FormEvent, useState } from "react";

import { Button } from "../../../components/ui/Button";
import { Input } from "../../../components/ui/Input";
import { Select } from "../../../components/ui/Select";
import { authService } from "../services/authService";
import { useAuth } from "../context/AuthContext";

export function LoginForm() {
  const { error, isLoading, login, register } = useAuth();
  const [mode, setMode] = useState<"login" | "register">("login");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState<"ADMIN" | "WORKER">("WORKER");

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (mode === "register") {
      await register({ email, name, password, role });
      return;
    }
    await login({ email, password });
  }

  return (
    <section className="auth-panel" aria-label="Authentication">
      <div className="auth-mode" role="tablist" aria-label="Authentication mode">
        <button className={mode === "login" ? "active" : ""} onClick={() => setMode("login")} type="button">
          Login
        </button>
        <button className={mode === "register" ? "active" : ""} onClick={() => setMode("register")} type="button">
          Register
        </button>
      </div>

      <form className="auth-form" onSubmit={handleSubmit}>
        {mode === "register" ? (
          <>
            <Input label="Name" minLength={2} onChange={(event) => setName(event.target.value)} required value={name} />
            <Select
              label="Role"
              onChange={(event) => setRole(event.target.value as "ADMIN" | "WORKER")}
              options={[
                { label: "Worker", value: "WORKER" },
                { label: "Admin", value: "ADMIN" },
              ]}
              value={role}
            />
          </>
        ) : null}
        <Input label="Email" onChange={(event) => setEmail(event.target.value)} required type="email" value={email} />
        <Input
          label="Password"
          minLength={8}
          onChange={(event) => setPassword(event.target.value)}
          required
          type="password"
          value={password}
        />
        {error ? <p className="form-error">{error}</p> : null}
        <Button disabled={isLoading} icon={<LogIn size={18} />} type="submit">
          {isLoading ? "Working..." : mode === "login" ? "Login" : "Create account"}
        </Button>
        <Button onClick={() => window.location.assign(authService.getGoogleLoginUrl())} type="button" variant="secondary">
          Continue with Google
        </Button>
      </form>
    </section>
  );
}
