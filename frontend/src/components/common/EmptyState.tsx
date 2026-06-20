import type { ReactNode } from "react";

interface EmptyStateProps {
  icon: ReactNode;
  title: string;
  body: string;
}

export function EmptyState({ body, icon, title }: EmptyStateProps) {
  return (
    <div className="empty-state">
      <div className="empty-state-icon">{icon}</div>
      <h2>{title}</h2>
      <p>{body}</p>
    </div>
  );
}
