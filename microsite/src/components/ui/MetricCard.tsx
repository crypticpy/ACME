import { LucideIcon } from 'lucide-react'
import { motion } from 'framer-motion'
import clsx from 'clsx'

interface MetricCardProps {
  label: string
  value: string | number
  icon: LucideIcon
  description?: string
  color?: 'primary' | 'secondary' | 'accent'
  trend?: {
    value: number
    isPositive: boolean
  }
}

const MetricCard = ({
  label,
  value,
  icon: Icon,
  description,
  color = 'primary',
  trend,
}: MetricCardProps) => {
  const colorClasses = {
    primary: 'from-primary-50 to-primary-100 text-primary-700',
    secondary: 'from-secondary-50 to-secondary-100 text-secondary-700',
    accent: 'from-accent-50 to-accent-100 text-accent-700',
  }

  const iconColorClasses = {
    primary: 'text-primary-600',
    secondary: 'text-secondary-600',
    accent: 'text-accent-600',
  }

  return (
    <motion.div
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      className={clsx(
        'relative overflow-hidden rounded-xl p-6 shadow-sm hover:shadow-md transition-all',
        'bg-gradient-to-br',
        colorClasses[color]
      )}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium opacity-80">{label}</p>
          <p className="mt-2 text-3xl font-bold tracking-tight">{value}</p>
          {description && (
            <p className="mt-1 text-sm opacity-70">{description}</p>
          )}
          {trend && (
            <div className="mt-2 flex items-center text-sm">
              <span className={clsx(
                'font-medium',
                trend.isPositive ? 'text-green-700' : 'text-red-700'
              )}>
                {trend.isPositive ? '+' : '-'}{Math.abs(trend.value)}%
              </span>
              <span className="ml-1 opacity-70">from last period</span>
            </div>
          )}
        </div>
        <div className={clsx('p-3 rounded-lg bg-white/50', iconColorClasses[color])}>
          <Icon className="h-6 w-6" />
        </div>
      </div>
      
      {/* Background decoration */}
      <div className="absolute -right-8 -bottom-8 h-32 w-32 rounded-full bg-white/10" />
    </motion.div>
  )
}

export default MetricCard