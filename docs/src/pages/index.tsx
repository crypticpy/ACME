import { motion } from 'framer-motion'
import Link from 'next/link'
import { ArrowRight, BarChart3, Users, Lightbulb, MapPin } from 'lucide-react'
import Layout from '@/components/layout/Layout'
import MetricCard from '@/components/ui/MetricCard'
import { fadeIn, slideUp } from '@/utils/animations'
import { useSummaryMetrics } from '@/hooks/useAnalysisData'

const HomePage = () => {
  const { summary, loading, error } = useSummaryMetrics()
  
  const keyMetrics = [
    {
      label: 'Survey Responses',
      value: loading ? '...' : summary?.totalResponses.toLocaleString() || '0',
      icon: Users,
      description: 'Community members shared their perspectives',
      color: 'primary' as const,
    },
    {
      label: 'Themes Identified',
      value: loading ? '...' : summary?.themesIdentified.toString() || '0',
      icon: Lightbulb,
      description: 'Major themes on cultural funding',
      color: 'accent' as const,
    },
    {
      label: 'Programs Analyzed',
      value: loading ? '...' : summary?.programsAnalyzed.toString() || '0',
      icon: BarChart3,
      description: 'ACME programs evaluated',
      color: 'secondary' as const,
    },
    {
      label: 'ZIP Codes Covered',
      value: loading ? '...' : summary?.geographicCoverage.toString() || '0',
      icon: MapPin,
      description: 'Geographic reach across Austin',
      color: 'primary' as const,
    },
  ]

  return (
    <Layout>
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-br from-primary-50 via-white to-accent-50 py-20">
        <div className="container relative z-10">
          <motion.div
            initial="hidden"
            animate="visible"
            variants={fadeIn}
            className="mx-auto max-w-4xl text-center"
          >
            <h1 className="text-5xl font-bold tracking-tight text-gray-900 sm:text-6xl lg:text-7xl">
              <span className="gradient-text">ACME Cultural Funding</span>
              <br />
              Analysis 2025
            </h1>
            <p className="mt-6 text-xl leading-8 text-gray-600">
              Comprehensive insights from Austin's creative community on arts, culture, music, and
              entertainment funding
            </p>
            <div className="mt-10 flex items-center justify-center gap-x-6">
              <Link
                href="/findings"
                className="btn-primary group"
              >
                Explore Findings
                <ArrowRight className="ml-2 h-4 w-4 transition-transform group-hover:translate-x-1" />
              </Link>
              <Link
                href="/methodology"
                className="btn-secondary"
              >
                View Methodology
              </Link>
            </div>
          </motion.div>
        </div>
        
        {/* Background decoration */}
        <div className="absolute inset-0 -z-10 overflow-hidden">
          <div className="absolute -top-40 -right-32 h-80 w-80 rounded-full bg-primary-200 opacity-20 blur-3xl" />
          <div className="absolute -bottom-40 -left-32 h-80 w-80 rounded-full bg-accent-200 opacity-20 blur-3xl" />
        </div>
      </section>

      {/* Key Metrics */}
      <section className="py-16 bg-gray-50">
        <div className="container">
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            variants={slideUp}
          >
            <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">
              Analysis at a Glance
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {keyMetrics.map((metric, index) => (
                <motion.div
                  key={metric.label}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: index * 0.1 }}
                >
                  <MetricCard {...metric} />
                </motion.div>
              ))}
            </div>
          </motion.div>
        </div>
      </section>

      {/* Key Findings Preview */}
      <section className="py-16">
        <div className="container">
          <div className="mx-auto max-w-4xl">
            <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">
              Key Insights
            </h2>
            <div className="space-y-8">
              <motion.div
                initial="hidden"
                whileInView="visible"
                viewport={{ once: true }}
                variants={fadeIn}
                className="card"
              >
                <h3 className="text-xl font-semibold mb-3">Diverse Community Engagement</h3>
                <p className="text-gray-600">
                  Our analysis captured perspectives from artists, organizational staff, and community
                  members across 93 unique ZIP codes in Austin, ensuring comprehensive representation
                  of the creative ecosystem.
                </p>
              </motion.div>
              
              <motion.div
                initial="hidden"
                whileInView="visible"
                viewport={{ once: true }}
                variants={fadeIn}
                transition={{ delay: 0.1 }}
                className="card"
              >
                <h3 className="text-xl font-semibold mb-3">Critical Funding Themes</h3>
                <p className="text-gray-600">
                  Ten major themes emerged from the analysis, highlighting community priorities
                  including equitable access, sustainable funding models, and support for emerging
                  artists and diverse cultural expressions.
                </p>
              </motion.div>
              
              <motion.div
                initial="hidden"
                whileInView="visible"
                viewport={{ once: true }}
                variants={fadeIn}
                transition={{ delay: 0.2 }}
                className="card"
              >
                <h3 className="text-xl font-semibold mb-3">Program-Specific Insights</h3>
                <p className="text-gray-600">
                  Each ACME program received targeted feedback, revealing unique strengths and
                  opportunities for enhancement to better serve Austin's creative community.
                </p>
              </motion.div>
            </div>
            
            <div className="mt-12 text-center">
              <Link
                href="/findings/themes"
                className="btn-primary group"
              >
                View All Findings
                <ArrowRight className="ml-2 h-4 w-4 transition-transform group-hover:translate-x-1" />
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Call to Action */}
      <section className="py-16 bg-gradient-to-r from-primary-600 to-primary-700">
        <div className="container">
          <div className="mx-auto max-w-2xl text-center">
            <h2 className="text-3xl font-bold text-white mb-4">
              Explore the Full Analysis
            </h2>
            <p className="text-xl text-primary-100 mb-8">
              Dive deep into our comprehensive findings and discover how Austin can strengthen
              its cultural funding ecosystem.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                href="/report"
                className="inline-flex items-center justify-center rounded-md bg-white px-6 py-3 text-base font-medium text-primary-600 shadow-sm hover:bg-primary-50 transition-colors"
              >
                Download Executive Report
              </Link>
              <Link
                href="/data-explorer"
                className="inline-flex items-center justify-center rounded-md bg-primary-500 px-6 py-3 text-base font-medium text-white shadow-sm hover:bg-primary-400 transition-colors"
              >
                Interactive Data Explorer
              </Link>
            </div>
          </div>
        </div>
      </section>
    </Layout>
  )
}

export default HomePage