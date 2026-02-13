import React from 'react';
import './RoleBadge.css';

const ROLE_COLORS = {
  BAT: 'role-bat',
  BOWL: 'role-bowl',
  ALL: 'role-all',
  WK: 'role-wk'
};

const ROLE_LABELS = {
  BAT: 'Batter',
  BOWL: 'Bowler',
  ALL: 'All-Rounder',
  WK: 'Wicket Keeper'
};

export default function RoleBadge({ role }) {
  const normalizedRole = role ? role.toUpperCase() : '';
  const className = `role-badge ${ROLE_COLORS[normalizedRole] || 'role-default'}`;
  const label = ROLE_LABELS[normalizedRole] || role;

  return (
    <span className={className}>
      {label}
    </span>
  );
}
