import { useState, useEffect } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/router'
import { motion, AnimatePresence } from 'framer-motion'
import { Menu, X, ChevronDown } from 'lucide-react'
import clsx from 'clsx'

const Navigation = () => {
  const [isOpen, setIsOpen] = useState(false)
  const [scrolled, setScrolled] = useState(false)
  const router = useRouter()

  const navigation = [
    { name: 'Home', href: '/' },
    {
      name: 'Findings',
      href: '/findings',
      children: [
        { name: 'WHO Analysis', href: '/findings/who' },
        { name: 'Thematic Analysis', href: '/findings/themes' },
        { name: 'Program Insights', href: '/findings/programs' },
      ],
    },
    { name: 'Methodology', href: '/methodology' },
    { name: 'Data Explorer', href: '/data-explorer' },
    { name: 'About', href: '/about' },
  ]

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 10)
    }
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  const isActive = (href: string) => router.pathname === href

  return (
    <nav
      className={clsx(
        'fixed top-0 z-50 w-full transition-all duration-300',
        scrolled ? 'bg-white/95 backdrop-blur-md shadow-sm' : 'bg-transparent'
      )}
    >
      <div className="container">
        <div className="flex h-16 items-center justify-between">
          {/* Logo */}
          <Link href="/" className="flex items-center space-x-2">
            <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-primary-600 to-accent-600" />
            <span className="font-bold text-xl">ACME Analysis</span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex md:items-center md:space-x-8">
            {navigation.map((item) => (
              <div key={item.name} className="relative group">
                <Link
                  href={item.href}
                  className={clsx(
                    'flex items-center space-x-1 px-3 py-2 text-sm font-medium transition-colors',
                    isActive(item.href)
                      ? 'text-primary-600'
                      : 'text-gray-700 hover:text-primary-600'
                  )}
                >
                  <span>{item.name}</span>
                  {item.children && <ChevronDown className="h-4 w-4" />}
                </Link>
                
                {/* Dropdown */}
                {item.children && (
                  <div className="absolute left-0 mt-2 w-48 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200">
                    <div className="rounded-lg bg-white shadow-lg ring-1 ring-black ring-opacity-5">
                      <div className="py-1">
                        {item.children.map((child) => (
                          <Link
                            key={child.name}
                            href={child.href}
                            className={clsx(
                              'block px-4 py-2 text-sm transition-colors',
                              isActive(child.href)
                                ? 'bg-primary-50 text-primary-600'
                                : 'text-gray-700 hover:bg-gray-50'
                            )}
                          >
                            {child.name}
                          </Link>
                        ))}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ))}
            
            <Link
              href="/report"
              className="btn-primary text-sm"
            >
              Download Report
            </Link>
          </div>

          {/* Mobile menu button */}
          <button
            onClick={() => setIsOpen(!isOpen)}
            className="md:hidden p-2 rounded-md text-gray-700 hover:bg-gray-100"
          >
            {isOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
          </button>
        </div>
      </div>

      {/* Mobile Navigation */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="md:hidden bg-white border-t"
          >
            <div className="container py-4 space-y-1">
              {navigation.map((item) => (
                <div key={item.name}>
                  <Link
                    href={item.href}
                    onClick={() => setIsOpen(false)}
                    className={clsx(
                      'block px-3 py-2 text-base font-medium rounded-md',
                      isActive(item.href)
                        ? 'bg-primary-50 text-primary-600'
                        : 'text-gray-700 hover:bg-gray-50'
                    )}
                  >
                    {item.name}
                  </Link>
                  {item.children && (
                    <div className="ml-4 mt-1 space-y-1">
                      {item.children.map((child) => (
                        <Link
                          key={child.name}
                          href={child.href}
                          onClick={() => setIsOpen(false)}
                          className={clsx(
                            'block px-3 py-2 text-sm rounded-md',
                            isActive(child.href)
                              ? 'bg-primary-50 text-primary-600'
                              : 'text-gray-600 hover:bg-gray-50'
                          )}
                        >
                          {child.name}
                        </Link>
                      ))}
                    </div>
                  )}
                </div>
              ))}
              <Link
                href="/report"
                onClick={() => setIsOpen(false)}
                className="block w-full btn-primary text-center mt-4"
              >
                Download Report
              </Link>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </nav>
  )
}

export default Navigation