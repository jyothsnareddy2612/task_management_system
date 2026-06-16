import type { InputHTMLAttributes } from "react";

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label: string;
}

export function Input({ label, id, ...props }: InputProps) {
  const inputId = id ?? label.toLowerCase().replace(/\s+/g, "-");

  return (
    <label className="field" htmlFor={inputId}>
      <span>{label}</span>
      <input id={inputId} {...props} />
    </label>
  );
}
