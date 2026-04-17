import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import App from '../../src/App'

describe('App', () => {
  it('renders the app brand name', () => {
    render(<App />)
    expect(screen.getByText('Industrial Datagen')).toBeInTheDocument()
  })

  it('renders navigation links', () => {
    render(<App />)
    expect(screen.getByText('Dashboard')).toBeInTheDocument()
    expect(screen.getByText('Datasets')).toBeInTheDocument()
  })

  it('renders the dashboard page by default', () => {
    render(<App />)
    expect(screen.getByText('Simulation Dashboard')).toBeInTheDocument()
  })
})
