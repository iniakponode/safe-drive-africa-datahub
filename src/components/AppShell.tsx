import type { ReactNode } from 'react'
import { useState } from 'react'
import { NavLink } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
import type { Role } from '../lib/types'

type NavItem = {
  label: string
  path: string
}

const navByRole: Record<Role, NavItem[]> = {
  fleet_manager: [
    { label: 'Dashboard', path: '/fleet' },
    { label: 'Driver Monitor', path: '/fleet/monitor' },
    { label: 'Trip Context', path: '/fleet/trip-context' },
    { label: 'Assignments', path: '/fleet/assignments' },
    { label: 'Reports', path: '/fleet/reports' },
    { label: 'Analytics', path: '/fleet/analytics' },
    { label: 'Fleet Setup', path: '/fleet/setup' },
  ],
  driver: [
    { label: 'Dashboard', path: '/driver' },
    { label: 'Profile', path: '/driver/profile' },
    { label: 'Trips', path: '/driver/trips' },
    { label: 'Questionnaire', path: '/driver/questionnaire' },
    { label: 'Tips', path: '/driver/tips' },
    { label: 'Leaderboard', path: '/driver/leaderboard' },
  ],
  researcher: [
    { label: 'Summary', path: '/researcher' },
    { label: 'Alcohol Bundle', path: '/researcher/alcohol-bundle' },
    { label: 'Exports', path: '/researcher/exports' },
    { label: 'Snapshots', path: '/researcher/snapshots' },
    { label: 'Ingestion', path: '/researcher/ingestion' },
  ],
  insurance_partner: [
    { label: 'Dashboard', path: '/insurance' },
    { label: 'Telematics', path: '/insurance/telematics' },
    { label: 'Alerts', path: '/insurance/alerts' },
    { label: 'Reports', path: '/insurance/reports' },
    { label: 'Raw Export', path: '/insurance/raw-export' },
  ],
  admin: [
    { label: 'Admin Home', path: '/admin' },
    { label: 'API Clients', path: '/admin/api-clients' },
    { label: 'Dataset Access', path: '/admin/dataset-access' },
    { label: 'Cloud Endpoints', path: '/admin/cloud-endpoints' },
    { label: 'Insurance Partners', path: '/admin/insurance-partners' },
    { label: 'Driver Profiles', path: '/admin/driver-profiles' },
    { label: 'Fleet View', path: '/fleet' },
    { label: 'Driver View', path: '/driver' },
    { label: 'Researcher View', path: '/researcher' },
    { label: 'Insurance View', path: '/insurance' },
  ],
}

type AppShellProps = {
  title: string
  eyebrow?: string
  subtitle?: string
  actions?: ReactNode
  children: ReactNode
}

export function AppShell({ title, eyebrow, subtitle, actions, children }: AppShellProps) {
  const { profile, logout } = useAuth()
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const role = profile?.role ?? 'admin'
  const navItems = navByRole[role]
  const initials = profile?.name
    ? profile.name
        .split(' ')
        .map((part) => part[0])
        .join('')
        .slice(0, 2)
        .toUpperCase()
    : 'SD'

  const closeMobileMenu = () => setMobileMenuOpen(false)

  return (
    <div className="app">
      <div className="background">
        <span className="orb orb--one" />
        <span className="orb orb--two" />
        <span className="gridlines" />
      </div>

      <div className="shell">
        <aside className={`sidebar ${mobileMenuOpen ? 'sidebar--open' : ''}`}>
          <div className="brand">
            <span className="brand__mark">S</span>
            <div>
              <p className="brand__name">SafeDrive Africa</p>
              <p className="brand__role">{role.replace('_', ' ')}</p>
            </div>
            <button 
              className="mobile-close"
              onClick={closeMobileMenu}
              aria-label="Close menu"
            >
              ✕
            </button>
          </div>
          <nav className="nav">
            {navItems.map((item) => (
              <NavLink
                key={item.label}
                to={item.path}
                className={({ isActive }) =>
                  `nav__item ${isActive ? 'nav__item--active' : ''}`
                }
                onClick={closeMobileMenu}
              >
                {item.label}
              </NavLink>
            ))}
          </nav>
          <div className="sidebar__footer">
            <p className="sidebar__label">Signed in</p>
            <p className="sidebar__meta">{profile?.name ?? 'Unknown'}</p>
            <button className="sidebar__action" onClick={logout}>
              Sign out
            </button>
          </div>
        </aside>

        {mobileMenuOpen && (
          <div 
            className="sidebar-overlay"
            onClick={closeMobileMenu}
          />
        )}

        <main className="main">
          <header className="topbar">
            <div className="topbar__left">
              <button 
                className="mobile-menu-btn"
                onClick={() => setMobileMenuOpen(true)}
                aria-label="Open menu"
              >
                <span></span>
                <span></span>
                <span></span>
              </button>
              <div>
                {eyebrow && <p className="eyebrow">{eyebrow}</p>}
                <h1>{title}</h1>
                {subtitle && <p className="subtext">{subtitle}</p>}
              </div>
            </div>
            <div className="topbar__actions">
              {actions}
              <div className="avatar">{initials}</div>
            </div>
          </header>
          {children}
        </main>
      </div>
    </div>
  )
}
