import { useState } from 'react'
import {
  Masthead,
  MastheadBrand,
  MastheadContent,
  MastheadMain,
  MastheadToggle,
  Nav,
  NavItem,
  NavList,
  Page,
  PageSidebar,
  PageSidebarBody,
  PageToggleButton,
  SkipToContent,
  Toolbar,
  ToolbarContent,
  ToolbarItem,
} from '@patternfly/react-core'
import { BarsIcon } from '@patternfly/react-icons'
import { BrowserRouter, Link, Route, Routes, useLocation } from 'react-router-dom'

import Dashboard from './pages/Dashboard'
import Datasets from './pages/Datasets'
import Documentation from './pages/Documentation'

function AppNav() {
  const location = useLocation()

  return (
    <Nav aria-label="Main navigation" className="rh-nav">
      <NavList>
        <NavItem isActive={location.pathname === '/'}>
          <Link to="/">Dashboard</Link>
        </NavItem>
        <NavItem isActive={location.pathname === '/datasets'}>
          <Link to="/datasets">Datasets</Link>
        </NavItem>
        <NavItem isActive={location.pathname === '/documentation'}>
          <Link to="/documentation">Documentation</Link>
        </NavItem>
      </NavList>
    </Nav>
  )
}

function AppLayout() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true)

  const masthead = (
    <Masthead className="rh-masthead">
      <MastheadMain>
        <MastheadToggle>
          <PageToggleButton
            variant="plain"
            aria-label="Global navigation"
            isSidebarOpen={isSidebarOpen}
            onSidebarToggle={() => setIsSidebarOpen(!isSidebarOpen)}
          >
            <BarsIcon />
          </PageToggleButton>
        </MastheadToggle>
        <MastheadBrand data-testid="app-brand">
          <span className="rh-brand-accent" />
          <span className="rh-brand-name">Industrial Datagen</span>
        </MastheadBrand>
      </MastheadMain>
      <MastheadContent>
        <Toolbar>
          <ToolbarContent>
            <ToolbarItem>
              <span className="rh-brand-version">v0.1.0</span>
            </ToolbarItem>
          </ToolbarContent>
        </Toolbar>
      </MastheadContent>
    </Masthead>
  )

  const sidebar = (
    <PageSidebar isSidebarOpen={isSidebarOpen}>
      <PageSidebarBody>
        <AppNav />
      </PageSidebarBody>
    </PageSidebar>
  )

  const skipToContent = <SkipToContent href="#main-content">Skip to content</SkipToContent>

  return (
    <Page masthead={masthead} sidebar={sidebar} skipToContent={skipToContent} mainContainerId="main-content">
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/datasets" element={<Datasets />} />
        <Route path="/documentation" element={<Documentation />} />
      </Routes>
    </Page>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <AppLayout />
    </BrowserRouter>
  )
}
