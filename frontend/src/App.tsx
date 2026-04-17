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

function AppNav() {
  const location = useLocation()

  return (
    <Nav aria-label="Main navigation">
      <NavList>
        <NavItem isActive={location.pathname === '/'}>
          <Link to="/">Dashboard</Link>
        </NavItem>
        <NavItem isActive={location.pathname === '/datasets'}>
          <Link to="/datasets">Datasets</Link>
        </NavItem>
      </NavList>
    </Nav>
  )
}

function AppLayout() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true)

  const masthead = (
    <Masthead>
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
          <span style={{ fontSize: '1.25rem', fontWeight: 600 }}>
            Industrial Datagen
          </span>
        </MastheadBrand>
      </MastheadMain>
      <MastheadContent>
        <Toolbar>
          <ToolbarContent>
            <ToolbarItem>v0.1.0</ToolbarItem>
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
