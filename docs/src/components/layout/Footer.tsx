import Link from 'next/link'
import { Github, Mail, FileText } from 'lucide-react'

const Footer = () => {
  const currentYear = new Date().getFullYear()

  const footerLinks = {
    analysis: [
      { name: 'WHO Analysis', href: '/findings/who' },
      { name: 'Thematic Analysis', href: '/findings/themes' },
      { name: 'Program Insights', href: '/findings/programs' },
      { name: 'Data Explorer', href: '/data-explorer' },
    ],
    resources: [
      { name: 'Executive Report', href: '/report' },
      { name: 'Methodology', href: '/methodology' },
      { name: 'Raw Data', href: '/data' },
      { name: 'About', href: '/about' },
    ],
    acme: [
      { name: 'ACME Website', href: 'https://acme.gov', external: true },
      { name: 'Cultural Programs', href: 'https://acme.gov/programs', external: true },
      { name: 'Contact Us', href: 'mailto:cultural@acme.gov', external: true },
    ],
  }

  return (
    <footer className="bg-gray-900 text-gray-300">
      <div className="container py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Brand */}
          <div className="col-span-1">
            <div className="flex items-center space-x-2 mb-4">
              <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-primary-500 to-accent-500" />
              <span className="font-bold text-xl text-white">ACME Analysis</span>
            </div>
            <p className="text-sm text-gray-400">
              Comprehensive analysis of Austin's cultural funding landscape
            </p>
            <div className="flex space-x-4 mt-6">
              <a
                href="https://github.com/acme/cultural-funding-analysis"
                target="_blank"
                rel="noopener noreferrer"
                className="text-gray-400 hover:text-white transition-colors"
                aria-label="GitHub"
              >
                <Github className="h-5 w-5" />
              </a>
              <a
                href="mailto:cultural@acme.gov"
                className="text-gray-400 hover:text-white transition-colors"
                aria-label="Email"
              >
                <Mail className="h-5 w-5" />
              </a>
              <Link
                href="/report"
                className="text-gray-400 hover:text-white transition-colors"
                aria-label="Download Report"
              >
                <FileText className="h-5 w-5" />
              </Link>
            </div>
          </div>

          {/* Links */}
          <div className="col-span-3 grid grid-cols-1 sm:grid-cols-3 gap-8">
            <div>
              <h3 className="text-white font-semibold mb-4">Analysis</h3>
              <ul className="space-y-2">
                {footerLinks.analysis.map((link) => (
                  <li key={link.name}>
                    <Link
                      href={link.href}
                      className="text-sm hover:text-white transition-colors"
                    >
                      {link.name}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>

            <div>
              <h3 className="text-white font-semibold mb-4">Resources</h3>
              <ul className="space-y-2">
                {footerLinks.resources.map((link) => (
                  <li key={link.name}>
                    <Link
                      href={link.href}
                      className="text-sm hover:text-white transition-colors"
                    >
                      {link.name}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>

            <div>
              <h3 className="text-white font-semibold mb-4">ACME</h3>
              <ul className="space-y-2">
                {footerLinks.acme.map((link) => (
                  <li key={link.name}>
                    {link.external ? (
                      <a
                        href={link.href}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-sm hover:text-white transition-colors inline-flex items-center"
                      >
                        {link.name}
                        <span className="ml-1 text-xs">↗</span>
                      </a>
                    ) : (
                      <Link
                        href={link.href}
                        className="text-sm hover:text-white transition-colors"
                      >
                        {link.name}
                      </Link>
                    )}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>

        {/* Bottom */}
        <div className="mt-12 pt-8 border-t border-gray-800">
          <div className="flex flex-col sm:flex-row justify-between items-center">
            <p className="text-sm text-gray-400">
              © {currentYear} ACME. All rights reserved.
            </p>
            <div className="flex space-x-6 mt-4 sm:mt-0">
              <Link href="/privacy" className="text-sm text-gray-400 hover:text-white transition-colors">
                Privacy Policy
              </Link>
              <Link href="/terms" className="text-sm text-gray-400 hover:text-white transition-colors">
                Terms of Use
              </Link>
              <Link href="/accessibility" className="text-sm text-gray-400 hover:text-white transition-colors">
                Accessibility
              </Link>
            </div>
          </div>
        </div>
      </div>
    </footer>
  )
}

export default Footer